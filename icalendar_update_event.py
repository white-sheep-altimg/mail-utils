import sys
import re
from datetime import datetime, timedelta, timezone
from maccal import CalendarStore


def update_event(store, event_id, title, start, end, notes):
  event = store.update_event(event_id, title=title, start=start, end=end, notes=notes)
  return event


# JSON文字列へ変換
def event_to_json(events):
  json  = "{\n"
  json += "  \"events\": [\n"
  event_id = event.event_id
  calendar_id = event.calendar_id
  location = event.location
  attendees = event.attendees
  title = event.title
  start = event.start.strftime('%Y/%m/%d %H:%M')
  end = event.end.strftime('%Y/%m/%d %H:%M')
  calendar = event.calendar
  notes = event.notes
  if not location: location = ""
  if not attendees: attendees = "[]"
  if not notes: notes = ""
  notes = notes.replace('\n', '\\n')
  json +=  "    {\n"
  json += f"      \"event_id\":    \"{event_id}\",\n"
  json += f"      \"calendar_id\": \"{calendar_id}\",\n"
  json += f"      \"title\":       \"{title}\",\n"
  json += f"      \"start\":       \"{start}\",\n"
  json += f"      \"end\":         \"{end}\",\n"
  json += f"      \"location\":    \"{location}\",\n"
  json += f"      \"attendees\":   {attendees},\n"
  json += f"      \"notes\":       \"{notes}\",\n"
  json += f"      \"calendar\":    \"{calendar}\"\n"
  json +=  "    }\n"
  json += "  ]\n"
  json += "}\n"
  return json


if __name__ == "__main__":
  search = ""
  if len(sys.argv) >= 6:
    event_id = sys.argv[1]
    title = sys.argv[2]
    start = sys.argv[3]
    end = sys.argv[4]
    notes = sys.argv[5]
  else:
    print(f"       python {sys.argv[0]} <event_id> <タイトル> <開始日時> <終了日時> <note>", file=sys.stderr)
    print(f"       カレンダー: ',' 区切りで複数指定可能（'勤務,祝日'）\n       日時: `2026/01/10 12:00'", file=sys.stderr)
    sys.exit(1)

  # 初期化
  store = CalendarStore()

  start = datetime.strptime(start, "%Y/%m/%d %H:%M")
  end   = datetime.strptime(end,   "%Y/%m/%d %H:%M")
  event = update_event(store, event_id, title, start, end, notes)
  json = event_to_json(event)
  print(f"{json}")
