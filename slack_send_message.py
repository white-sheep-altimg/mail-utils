import os
import sys
import time
import requests
import configparser
from dotenv import load_dotenv
import json


## configuration
VERBOSE = False
config_file = 'config.ini'
dotenv_file = '.env'

MSGSEND_URL = "https://slack.com/api/chat.postMessage"


def chunk_string(text, chunk_size):
	chunks = []
	for i in range(0, len(text), chunk_size):
		chunk = text[i:i + chunk_size]
		chunks.append(chunk)
	return chunks

def send_slack_message(token, channel, chunks):
  headers = {"Authorization": f"Bearer {token}"}
  for chunk in chunks:
    data  = {
      "channel": f"{channel}",
      "text": f"{chunk}"
    }
    res = requests.post(MSGSEND_URL, headers=headers, data=data)
    data = res.json()
    if VERBOSE: print(f"{json.dumps(data)}", file=sys.stderr)
    if data.get('ok') == False:
      print(f"送信に失敗しました: {chunk}", file=sys.stderr)
    # time.sleep(1)
  return data


if __name__ == "__main__":
  # 初期化
  if load_dotenv(dotenv_file):
    token = os.environ.get('bot_token')
    channel = os.environ.get('channel')
    limit = int(os.environ.get('limit'))
    chunk_size = int(os.environ.get('chunk_size'))
    if VERBOSE: print(f"LOAD({dotenv_file}): {token}, {channel}, {limit}, {chunk_size}", file=sys.stderr)
  elif os.path.exists(config_file):
    config_parser = configparser.ConfigParser()
    config = config_parser.read(config_file, encoding='utf-8')
    slack_settings = config_parser['slack']
    token = slack_settings.get('bot_token')
    channel = slack_settings.get('channel')
    limit = slack_settings.getint('limit', LIMIT)
    chunk_size = slack_settings.getint('chunk_size')
    if VERBOSE: print(f"LOAD({config_file}): {token}, {channel}, {limit}, {chunk_size}", file=sys.stderr)
  else:
    print(f"初期化ファイルが見つかりません: {dotenv_file} または {config_file}", file=sys.stderr)
    sys.exit(1)


  if len(sys.argv) < 2:
    print(f"Usage: python3 {sys.argv[0]} <\"メッセージ\">", file=sys.stderr)
    sys.exit(1)
  message = sys.argv[1]

  print(f"送信開始", file=sys.stderr)
  chunks = chunk_string(message, chunk_size)
  data = send_slack_message(token, channel, chunks)
  print(f"{json.dumps(data)}")
  print(f"送信完了", file=sys.stderr)
