import os
import sys
import sqlite3
import json
from email_config import config

## データベース（必要に応じて V10 などのバージョン部分は環境に合わせてください）
DB_PATH = '~/Library/Mail/V10/MailData/Envelope Index'

## mailbox名のリスト
MAILBOX = config['mailbox']

# 取得するメールの最大件数
# 例: python3 get_mail_list.py 20
if len(sys.argv) < 2:
  print(f"Usage: python3 {sys.argv[0]} <最大件数> [<対象日>] [<メールステータス 0/1>]", file=sys.stderr)
  sys.exit(1)

tdate = ""
if len(sys.argv) >= 3:
  if sys.argv[2].find('/'):
    tdate = sys.argv[2]
  else:
    print('Error: 対象日は "2026/01/10" のように指定してください', file=sys.stderr)
    sys.exit(1)

readmode = 0
if len(sys.argv) >= 4:
  readmode = int(sys.argv[3])
  if readmode < 0 or readmode > 1:
    print('Error: メールステータスは 未読：0または既読：1 で指定してください', file=sys.stderr)
    sys.exit(1)


# SQLiteはLIMITにパラメータバインドが使えないため、明示的なバリデーション後、安全に埋め込む
maxnum = int(sys.argv[1])
if maxnum <= 0 or maxnum > 10000:
  print('Error: 最大件数は 1〜10000 の範囲で指定してください', file=sys.stderr)
  sys.exit(1)


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

query = f"""
SELECT
    datetime(m.date_sent, 'unixepoch') AS sent_date,
    mb.url AS mailbox_path,
    m.read AS read_status,
    s.subject AS subject_text,
    a.address AS sender_address,
    d.message_id_header AS message_id,
    m.rowid AS rowid,
    m.mailbox AS mailbox
FROM messages m
LEFT JOIN subjects s ON m.subject = s.rowid
LEFT JOIN addresses a ON m.sender = a.rowid
LEFT JOIN mailboxes mb ON m.mailbox = mb.rowid
LEFT JOIN message_global_data d ON m.message_id = d.message_id
WHERE m.read = {readmode}
  AND mb.url LIKE '%INBOX%'
ORDER BY m.date_sent DESC
LIMIT {maxnum};
"""

# 3. 中身を全て取得するfetchall()を使って、printする。
cursor.execute(query)
rows = cursor.fetchall()
conn.close()

if not rows:
  print(
    json.dumps(
      {'error': f'該当するメールはありません'},
      ensure_ascii=False,
    )
  )
  sys.exit(1)

## 指定の日付に一致する行のみ抽出
qrows = []
for row in rows:
  date = row['sent_date'].replace('-', '/')
  if date.find(tdate) >= 0:
    qrows.append(row)

## 整形出力
json  = "{\n"
json += "  \"emails\": [\n"
for i, row in enumerate(qrows, 1):
  date = row['sent_date'].replace('-', '/')
  subject = row['subject_text'].replace('"', "")
  sender = row['sender_address'].replace('"', "")
  message_id = row['message_id'].replace('"', "")
  rowid = row['rowid']
  mailbox = row['mailbox']
  mailbox = MAILBOX[mailbox] if mailbox in MAILBOX else mailbox
  json +=  "    {\n"
  json += f"      \"date\":       \"{date}\",\n"
  json += f"      \"subject\":    \"{subject}\",\n"
  json += f"      \"sender\":     \"{sender}\",\n"
  json += f"      \"message_id\": \"{message_id}\",\n"
  json += f"      \"mailbox\":    \"{mailbox}\",\n"
  json += f"      \"rowid\":      {rowid}\n"
  json +=  "    }"
  if i < len(qrows):
    json += ","
    json += "\n"
json += "\n  ]\n"
json += "}\n"

print(json)
