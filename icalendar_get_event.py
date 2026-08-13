import sys
import re
from datetime import datetime, timedelta, timezone
from maccal import CalendarStore


# 参加者一覧
def make_attendees(src):
  if src == "": return ""
  attendees = []
  json  = "{\n"
  json += "  \"attendee\": [\n"
  for i, attendee in enumerate(src, 1):
    name = attendee.name
    addr = attendee.email
    # role: UNKNOWN = 0, REQUIRED = 1, OPTIONAL = 2, CHAIR = 3, NON_PARTICIPANT = 4
    role = str(attendee.role.value)
    # status: UNKNOWN = 0, PENDING = 1, ACCEPTED = 2, DECLINED = 3, TENTATIVE = 4, DELEGATED = 5, COMPLETED = 6, IN_PROCESS = 7
    status = str(attendee.status.value)
    json += "    { \"name\": \"" + name + "\", \"email\": \"" + addr + "\", \"role\": " + role + ", \"status\": " + status + " }"
    if i < len(src): json += ","
    json += "\n"
  json += "  ]\n"
  json += "}"
  return json

# 一致するカレンダーのイベントのみ抽出
def make_events(src, calendar_list, mode):
  events = []
  for event in src:
    title = event.title
    start = event.start.strftime('%Y/%m/%d %H:%M')
    end = event.end.strftime('%Y/%m/%d %H:%M')
    calendar = event.calendar
    if calendar in calendar_list or mode:
      events.append(event)
  return events

# JSON文字列へ変換
def events_to_json(events):
  json  = "{\n"
  json += "  \"events\": [\n"
  for i, event in enumerate(events, 1):
    event_id = event.event_id
    calendar_id = event.calendar_id
    location = event.location
    attendees = event.attendees
    title = event.title
    start = event.start.strftime('%Y/%m/%d %H:%M')
    end = event.end.strftime('%Y/%m/%d %H:%M')
    calendar = event.calendar
    notes = event.notes
    url = event.url
    if not location: location = ""
    if not attendees: attendees = ""
    if not notes: notes = ""
    if not url: url = ""
    notes = notes.replace('\n', '\\n')
    attendees = make_attendees(attendees)
    if attendees == "": attendees = "\"\""
    json +=  "    {\n"
    json += f"      \"event_id\":    \"{event_id}\",\n"
    json += f"      \"calendar_id\": \"{calendar_id}\",\n"
    json += f"      \"title\":       \"{title}\",\n"
    json += f"      \"start\":       \"{start}\",\n"
    json += f"      \"end\":         \"{end}\",\n"
    json += f"      \"location\":    \"{location}\",\n"
    json += f"      \"attendees\":   {attendees},\n"
    json += f"      \"notes\":       \"{notes}\",\n"
    json += f"      \"url\":         \"{url}\",\n"
    json += f"      \"calendar\":    \"{calendar}\"\n"
    json +=  "    }"
    if i < len(events):
      json += ","
    json += "\n"
  json += "  ]\n"
  json += "}\n"
  return json

# メールアドレス構文チェック
def check_address(addr):
  match = re.match('[A-Za-z0-9._+]+@[A-Za-z]+.[A-Za-z]', addr)
  return match


# イベント一覧
def get_events(store, start, end, calendar_list):
  # Get events for the next 7 days
  events = store.get_events(start=start, end=end)
  events = make_events(events, calendar_list, False)
  json = events_to_json(events)
  return json


# イベント検索（タイトル部分一致）
def search_events(store, title, start, end, calendar_list):
  events = store.find_events(title, start=start, end=end)
  events = make_events(events, calendar_list, False)
  json = events_to_json(events)
  return json


# イベント検索（参加者部分一致）
def search_events_by_attendees(store, addr, start, end, calendar_list):
  events = store.find_events(addr, start=start, end=end, fields=["attendee_email"])
  events = make_events(events, calendar_list, True)
  json = events_to_json(events)
  return json



if __name__ == "__main__":
  search = ""
  if len(sys.argv) >= 5:
    search = sys.argv[1]
    start = sys.argv[2]
    end = sys.argv[3]
    cal = sys.argv[4]
  elif len(sys.argv) >= 4:
    start = sys.argv[1]
    end = sys.argv[2]
    cal = sys.argv[3]
  else:
    print(f"Usage: python3 {sys.argv[0]} <開始日時> <終了日時> <カレンダー>", file=sys.stderr)
    print(f"       python3 {sys.argv[0]} <タイトルの検索文字列> <開始日時> <終了日時> <カレンダー>", file=sys.stderr)
    print(f"       カレンダー: ',' 区切りで複数指定可能（'勤務,祝日'）\n       日時: `2026/01/10 12:00'", file=sys.stderr)
    sys.exit(1)

  # 初期化
  store = CalendarStore()

  start = datetime.strptime(start, "%Y/%m/%d %H:%M")
  end   = datetime.strptime(end,   "%Y/%m/%d %H:%M")
  calendar_list = cal.split(",")
  if len(sys.argv) >= 5:
    if check_address(search) != None:
      events = search_events_by_attendees(store, search, start, end, calendar_list)
    else:
      events = search_events(store, search, start, end, calendar_list)
  else:
    events = get_events(store, start, end, calendar_list)
  print(f"{events}")
