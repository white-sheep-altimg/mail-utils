import os
import sys
import requests
import configparser
from dotenv import load_dotenv
import json


## configuration
VERBOSE = False
config_file = 'config.ini'
dotenv_file = '.env'

HISTORY_URL = "https://slack.com/api/conversations.history"
REPLIES_URL = "https://slack.com/api/conversations.replies"
LIMIT=10

def get_slack_history(token, channel, limit):
  header = {
    "Authorization": f"Bearer {token}",
  }
  payload  = {
    "channel" : f"{channel}",
    "limit" : f"{limit}"
  }
  res = requests.get(HISTORY_URL, headers=header, params=payload)
  data = res.json()
  return data

def get_slack_replies(token, channel, ts):
  header = {
    "Authorization": f"Bearer {token}",
  }
  payload  = {
    "channel" : f"{channel}",
    "ts" : f"{ts}"
  }
  res = requests.get(REPLIES_URL, headers=header, params=payload)
  data = res.json()
  return data


if __name__ == "__main__":
  # 初期化
  if load_dotenv(dotenv_file):
    token = os.environ.get('bot_token')
    channel = os.environ.get('channel')
    limit = int(os.environ.get('limit'))
    if VERBOSE: print(f"LOAD({dotenv_file}): {token}, {channel}, {limit}", file=sys.stderr)
  elif os.path.exists(config_file):
    # トークンを取得
    config_parser = configparser.ConfigParser()
    config = config_parser.read(config_file, encoding='utf-8')
    slack_settings = config_parser['slack']
    token = slack_settings.get('bot_token')
    channel = slack_settings.get('channel')
    limit = slack_settings.get('limit', LIMIT)
    if VERBOSE: print(f"LOAD({config_file}): {token}, {channel}, {limit}", file=sys.stderr)
  else:
    print(f"初期化ファイルが見つかりません: {dotenv_file} または {config_file}", file=sys.stderr)
    sys.exit(1)

  ts = ""
  narg = len(sys.argv)
  # if narg < 2:
  #   print(f"Usage: python {sys.argv[0]} [<最大件数> / <timestamp>]", file=sys.stderr)
  #   sys.exit(1)
  if narg >= 2:
    if sys.argv[1].find('.') >= 0:
      # timestamp
      ts = sys.argv[1]
    else:
      # limit
      limit = int(sys.argv[1])

  if ts == "":
    data = get_slack_history(token, channel, limit)
  else:
    data = get_slack_replies(token, channel, ts)
  print(f"{json.dumps(data)}")
