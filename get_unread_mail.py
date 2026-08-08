import json
import os
import sqlite3
import sys

## データベース（必要に応じて V10 などのバージョン部分は環境に合わせてください）
DB_PATH = '~/Library/Mail/V10/MailData/Envelope Index'



# 取得するメールの最大件数
# 例: python3 get_mail_json.py 20
if len(sys.argv) < 2:
  print('Usage: python3 get_unread_mail.py <最大件数>', file=sys.stderr)
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
    m.rowid AS rowid
FROM messages m
LEFT JOIN subjects s ON m.subject = s.rowid
LEFT JOIN addresses a ON m.sender = a.rowid
LEFT JOIN mailboxes mb ON m.mailbox = mb.rowid
LEFT JOIN message_global_data d ON m.message_id = d.message_id
WHERE m.read = 0
  AND mb.url LIKE '%INBOX%'
ORDER BY m.date_sent DESC
LIMIT {maxnum};
"""

cursor.execute(query)
rows = cursor.fetchall()
conn.close()

if not rows:
  print(
      json.dumps(
          {'error': f'未読メールはありません'},
          ensure_ascii=False,
      )
  )
  sys.exit(1)


# 3. 中身を全て取得するfetchall()を使って、printする。
json  = "{\n"
json += "  \"emails\": [\n"
for i, row in enumerate(rows, 1):
    date = row['sent_date']
    subject = row['subject_text'].replace('"', "")
    sender = row['sender_address'].replace('"', "")
    message_id = row['message_id'].replace('"', "")
    rowid = row['rowid']
    json +=  "    {\n"
    json += f"      \"date\":       \"{date}\",\n"
    json += f"      \"subject\":    \"{subject}\",\n"
    json += f"      \"sender\":     \"{sender}\",\n"
    json += f"      \"message_id\": \"{message_id}\",\n"
    json += f"      \"rowid\":      {rowid}\n"
    json +=  "    }"
    if i < len(rows):
        json += ","
    json += "\n"
json += "  ]\n"
json += "}\n"

print(json)
