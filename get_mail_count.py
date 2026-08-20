import os
import sys
import sqlite3
import json
from email_config import config

## データベース（必要に応じて V10 などのバージョン部分は環境に合わせてください）
DB_PATH = '~/Library/Mail/V10/MailData/Envelope Index'

## mailbox名のリスト
MAILBOX = config['mailbox']

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
SELECT COUNT(*)
FROM messages m
LEFT JOIN subjects s ON m.subject = s.rowid
LEFT JOIN addresses a ON m.sender = a.rowid
LEFT JOIN mailboxes mb ON m.mailbox = mb.rowid
LEFT JOIN message_global_data d ON m.message_id = d.message_id
WHERE m.read = 0
  AND mb.url LIKE '%INBOX%'
ORDER BY m.date_sent DESC;
"""

# 3. 件数を取得し，printする。
cursor.execute(query)
rows = cursor.fetchone()
conn.close()

print(rows[0])
