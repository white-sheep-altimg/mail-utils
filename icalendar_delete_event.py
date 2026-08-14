import sys
import re
from datetime import datetime, timedelta, timezone
from maccal import CalendarStore


# イベント削除
def delete_event_by_event_id(store, event_id):
  try:
    result = store.delete_event(event_id)
  except:
    print(f"一致する予定が見つかりませんでした: {event_id}", file=sys.stderr)
    return -1
  return 0


if __name__ == "__main__":
  search = ""
  if len(sys.argv) >= 2:
    event_id = sys.argv[1]
  else:
    print(f"Usage: python {sys.argv[0]} <event_id>", file=sys.stderr)
    sys.exit(1)

  # 初期化
  store = CalendarStore()

  print(f"削除開始", file=sys.stderr)
  if delete_event_by_event_id(store, event_id) < 0:
    print(f"削除できませんでした", file=sys.stderr)
  else:
    print(f"削除完了", file=sys.stderr)
