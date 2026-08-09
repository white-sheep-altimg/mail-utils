# coding: utf-8
import sys
import subprocess
import datetime
import uuid

HOSTNAME = 'example.com'
EVENT_FILE_NAME = "/tmp/event.ics"

def icalendar_add_event(title, start, end, description, location, url):
    sdt = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    suuid = f"{uuid.uuid4()}@{HOSTNAME}"
    start = start.replace('/', '').replace(':', '').replace(' ', 'T') + '00'
    end = end.replace('/', '').replace(':', '').replace(' ', 'T') + '00'

    ics = f'''
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//CalendarCLI//JA
CALSCALE:GREGORIAN
BEGIN:VTIMEZONE
TZID:Asia/Tokyo
BEGIN:STANDARD
DTSTART:19700101T000000
TZOFFSETFROM:+0900
TZOFFSETTO:+0900
END:STANDARD
END:VTIMEZONE
BEGIN:VEVENT
SUMMARY:{title}
DESCRIPTION:{description}
LOCATION:{location}
URL:{url}
DTSTART;TZID=Asia/Tokyo:{start}
DTEND;TZID=Asia/Tokyo:{end}
DTSTAMP:{sdt}
UID:{suuid}
END:VEVENT
END:VCALENDAR
'''
    # icsファイル作成
    f = open(EVENT_FILE_NAME, 'w', encoding='UTF-8')
    f.write(ics)
    f.close()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 5:
        print(f"Usage: python {sys.argv[0]} <TITLE> <START> <END> <DESCRIPTION> [<LOCATION>] [<URL>]", file=sys.stderr)
        sys.exit(1)

    title = sys.argv[1]
    start = sys.argv[2]
    end = sys.argv[3]
    description = sys.argv[4]
    location = ""
    url = ""
    if len(sys.argv) >= 6:
        location = sys.argv[5]
    if len(sys.argv) >= 7:
        url = sys.argv[6]

    icalendar_add_event(title, start, end, description, location, url)
    cmd = f"open {EVENT_FILE_NAME}"
    result = subprocess.run(['open', EVENT_FILE_NAME])
    if result.returncode != 0:
        print('イベントの登録に失敗しました', file=sys.stderr)
        sys.exit(1)
