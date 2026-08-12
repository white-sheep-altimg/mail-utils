import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import configparser
from dotenv import load_dotenv

## settings
# 1. Socket Mode
#   Enable Socker Mode を ON
#   Token Name は任意の名前
# 2. OAuth & Permissions
#   Add an OAuth Scope で必要なスコープを追加
# 3. Event Subscriptions
#   Enable Eventsを on にする
#   Subscribe to bot events で必要なイベントを追加
# 4. Install App


# configuration
VERBOSE = False
config_file = 'config.ini'
dotenv_file = '.env'

if load_dotenv(dotenv_file):
  app_token = os.environ.get("bolt_app_token")
  bot_token = os.environ.get("bolt_bot_token")
  if VERBOSE: print(f"LOAD({dotenv_file}): {app_token}, {bot_token}", file=sys.stderr)
elif os.path.exists(config_file):
  # トークンを取得
  config_parser = configparser.ConfigParser()
  config = config_parser.read(config_file, encoding='utf-8')
  slack_settings = config_parser['bolt']
  app_token = slack_settings.get('app_token')
  bot_token = slack_settings.get('bot_token')
  if VERBOSE: print(f"LOAD({config_file}): {app_token}, {bot_token}", file=sys.stderr)
else:
  print(f"初期化ファイルが見つかりません: {dotenv_file} または {config_file}", file=sys.stderr)
  sys.exit(1)


# 初期化
app = App(token=bot_token)

# メッセージ受信待ち
@app.event("message")
def message_receive(message, say):
  if VERBOSE: print(f"MESSAGE: {message}", file=sys.stderr)
  # 返信
  say(f"RECV: 受信しました")


if __name__ == "__main__":
  # ソケットモードで起動
  SocketModeHandler(app, app_token).start()
