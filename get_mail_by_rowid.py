import email
from email.policy import default
from html.parser import HTMLParser
import json
import os
import sqlite3
import sys

## データベース（必要に応じて V10 などのバージョン部分は環境に合わせてください）
DB_PATH = '~/Library/Mail/V10/MailData/Envelope Index'



# HTMLをプレーンテキストに変換するクラス
class HTMLFilter(HTMLParser):

  def __init__(self):
    super().__init__()
    self.text = []
    self.ignore_tag = False  # スタイルやスクリプト内かどうかを判定するフラグ

  def handle_starttag(self, tag, attrs):
    # style や script タグが始まったら、中身のテキストを無視する
    if tag.lower() in ['style', 'script', 'head']:
      self.ignore_tag = True

  def handle_endtag(self, tag):
    # style や script タグが終わったら、通常モードに戻す
    if tag.lower() in ['style', 'script', 'head']:
      self.ignore_tag = False

  def handle_data(self, data):
    # 無視フラグが立っていないデータ（実際の本文テキスト）だけを蓄積する
    if not self.ignore_tag:
      self.text.append(data)

  def get_text(self):
    return ''.join(self.text)


def html_to_plain_text(html_content):
  parser = HTMLFilter()
  parser.feed(html_content)
  # 改行や空白の連続をきれいに整え、空行を省く
  lines = [line.strip() for line in parser.get_text().splitlines()]
  return '\n'.join([line for line in lines if line])


# 対象のメールの ROWID を指定（引数から受け取るか、直接指定）
# 例: python3 get_mail_by_rowid.py 46873
if len(sys.argv) < 2:
  print(f"Usage: python3 {sys.argv[0]} <ROWID>", file=sys.stderr)
  sys.exit(1)

target_rowid = sys.argv[1]

# 1. データベースのパス
db_path = os.path.expanduser(DB_PATH)

if not os.path.exists(db_path):
  # Vのバージョンが違う場合のフォールバック検索
  import glob

  matches = glob.glob(
      os.path.expanduser('~/Library/Mail/V*/MailData/Envelope Index')
  )
  if matches:
    db_path = matches[0]
  else:
    print(
        json.dumps(
            {
                'error': (
                    'Envelope Indexが見つかりませんでした（フルディスクアクセスの権限をご確認ください）'
                )
            },
            ensure_ascii=False,
        )
    )
    sys.exit(1)

# 2. SQLiteからメッセージ情報（リモートIDやメールボックスパス等）を取得
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

query = """
SELECT
    m.ROWID,
    m.remote_id,
    datetime(m.date_sent, 'unixepoch') AS sent_date,
    s.subject AS subject_text,
    a.address AS sender_address,
    mb.url AS mailbox_path
FROM messages m
LEFT JOIN subjects s ON m.subject = s.rowid
LEFT JOIN addresses a ON m.sender = a.rowid
LEFT JOIN mailboxes mb ON m.mailbox = mb.rowid
WHERE m.ROWID = ?
"""

cursor.execute(query, (target_rowid,))
row = cursor.fetchone()
conn.close()

if not row:
  print(
      json.dumps(
          {'error': f'ROWID {target_rowid} のメールが見つかりませんでした'},
          ensure_ascii=False,
      )
  )
  sys.exit(1)

# 3. .emlx ファイルのパスを探す
# macOSのメール実体ファイルは ~/Library/Mail/V[版]/[アカウントUUID]/[フォルダUUID]/Data/Messages/ に格納されています。
# remote_id または ROWID をもとに .emlx を検索します。
mail_base_dir = os.path.expanduser('~/Library/Mail')


def find_emlx_file(rowid):
  # 簡易的にライブラリ全体から該当する ROWID.emlx または類似ファイルを探す
  for root, dirs, files in os.walk(mail_base_dir):
    # ファイル名が一致するもの、あるいは .emlx の中から探す
    target_name = f'{rowid}.emlx'
    if target_name in files:
      return os.path.join(root, target_name)
    # 数字が一致するemlxを探すフォールバック
    for file in files:
      if file.endswith('.emlx') and file.startswith(str(rowid) + '.'):
        return os.path.join(root, file)
  return None


emlx_path = find_emlx_file(target_rowid)

headers_dict = {}
body_text = ''

if emlx_path and os.path.exists(emlx_path):
  with open(emlx_path, 'rb') as f:
    raw_content = f.read()

  # .emlx特有の構造を処理する:
  # ファイルの先頭にある「バイト長を表す数値の行」をスキップする
  # 例: "5635 \n..." のような数値ヘッダーを取り除く
  parts = raw_content.split(b'\n', 1)
  if parts[0].strip().isdigit():
    raw_content = parts[1]

  # 末尾の Apple用 plist (<?xml ... から始まる部分) があれば切り捨てる
  plist_idx = raw_content.find(b'<?xml')
  if plist_idx != -1:
    raw_content = raw_content[:plist_idx]

  # emailモジュールでMIMEとしてパース
  msg = email.message_from_bytes(raw_content, policy=default)

  # ヘッダ情報の抽出
  for key, value in msg.items():
    key = 'Message-Id' if key == 'Message-ID' else key
    headers_dict[key] = value

  # 本文（ボディ）の抽出とデコード
  if msg.is_multipart():
      # 優先度として text/plain を探す。なければ text/html を探す
      plain_parts = []
      html_parts = []

      for part in msg.walk():
          content_type = part.get_content_type()
          payload = part.get_payload(decode=True)
          if payload:
              charset = part.get_content_charset() or 'utf-8'
              decoded_text = payload.decode(charset, errors='replace')

              if content_type == 'text/plain':
                  plain_parts.append(decoded_text)
              elif content_type == 'text/html':
                  html_parts.append(decoded_text)

      # text/plain があればそれを優先、なければ text/html をテキスト化する
      if plain_parts:
          body_text = '\n'.join(plain_parts)
      elif html_parts:
          raw_html = '\n'.join(html_parts)
          body_text = html_to_plain_text(raw_html)

  else:
      payload = msg.get_payload(decode=True)
      if payload:
          charset = msg.get_content_charset() or 'utf-8'
          decoded_text = payload.decode(charset, errors='replace')

          if msg.get_content_type() == 'text/html':
              body_text = html_to_plain_text(decoded_text)
          else:
              body_text = decoded_text

# もし万が一 quoted-printable がデコードしきれずに残っている場合のフォールバック
if '=E3=' in body_text or '=81=' in body_text:
  try:
    body_text = quopri.decodestring(body_text.encode('ascii')).decode(
        'utf-8', errors='replace'
    )
  except Exception:
    pass

output_data = {
    'rowid': row['ROWID'],
    'sent_date': row['sent_date'],
    'subject': row['subject_text'],
    'sender': row['sender_address'],
    'mailbox': row['mailbox_path'],
    'headers': headers_dict,
    'body': body_text.strip(),
}

print(json.dumps(output_data, ensure_ascii=False, indent=2))
