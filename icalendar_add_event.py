# coding: utf-8
import os
import sys
import subprocess
import datetime
import uuid
import configparser
from dotenv import load_dotenv

## configuration
VERBOSE = True
config_file = 'config.ini'
dotenv_file = '.env'

EVENT_FILE_NAME = "/tmp/event.ics"


def icalendar_add_event(email, hostname, title, start, end, description, location, url, mails):
  sdt = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
  suuid = f"{uuid.uuid4()}@{hostname}"
  start = start.replace('/', '').replace(':', '').replace(' ', 'T') + '00'
  end = end.replace('/', '').replace(':', '').replace(' ', 'T') + '00'

  attendees = f"ATTENDEE;CN=\"{email}\";CUTYPE=INDIVIDUAL;EMAIL=\"{email}\";PARTSTAT=ACCEPTED:mailto:{email}"
  for mail in mails:
    addr = mail.replace(" ", "")
    attendees += f"\nATTENDEE;CN=\"{addr}\";CUTYPE=INDIVIDUAL;EMAIL=\"{addr}\":mailto:{addr}"

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
{attendees}
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
  if load_dotenv(dotenv_file):
    email = os.environ.get('email')
    hostname = os.environ.get('hostname')
  elif os.path.exists(config_file):
    config_parser = configparser.ConfigParser()
    config = config_parser.read(config_file, encoding='utf-8')
    settings = config_parser['icalendar']
    mail = slack_settings.get('email')
    hostname = slack_settings.get('hostname')
  else:
    print(f"初期化ファイルが見つかりません: {dotenv_file} または {config_file}", file=sys.stderr)
    sys.exit(1)

  if len(sys.argv) < 5:
    print(f"Usage: python {sys.argv[0]} <TITLE> <START> <END> <DESCRIPTION> [<LOCATION>] [<URL>] [<attendees>]", file=sys.stderr)
    sys.exit(1)

  title = sys.argv[1]
  start = sys.argv[2]
  end = sys.argv[3]
  description = sys.argv[4]
  location = ""
  url = ""
  mails = ""
  if len(sys.argv) >= 8:
    mails = sys.argv[7].split(",")
  if len(sys.argv) >= 7:
    url = sys.argv[6]
  if len(sys.argv) >= 6:
    location = sys.argv[5]

  icalendar_add_event(email, hostname, title, start, end, description, location, url, mails)
  cmd = f"open {EVENT_FILE_NAME}"
  result = subprocess.run(['open', EVENT_FILE_NAME])
  if result.returncode != 0:
    print('イベントの登録に失敗しました', file=sys.stderr)
    sys.exit(1)
