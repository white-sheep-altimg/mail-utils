import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import configparser
from dotenv import load_dotenv
import time

## bolt settings
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

# トークンを取得
if load_dotenv(dotenv_file):
  app_token = os.environ.get("bolt_app_token")
  bot_token = os.environ.get("bolt_bot_token")
  if VERBOSE: print(f"LOAD({dotenv_file}): {app_token}, {bot_token}", file=sys.stderr)
elif os.path.exists(config_file):
  config_parser = configparser.ConfigParser()
  config = config_parser.read(config_file, encoding='utf-8')
  slack_settings = config_parser['bolt']
  app_token = slack_settings.get('app_token')
  bot_token = slack_settings.get('bot_token')
  if VERBOSE: print(f"LOAD({config_file}): {app_token}, {bot_token}", file=sys.stderr)
else:
  print(f"初期化ファイルが見つかりません: {dotenv_file} または {config_file}", file=sys.stderr)
  sys.exit(1)


# メッセージ処理
# 不具合や効率のためメンションも`message'で受ける
def recv_message(message, say):
  type = message['type']
  user = message['user']
  ts = message['ts']
  text = message['text']
  team = message['team']
  blocks = message['blocks']
  block = blocks[0]
  elements = block['elements']
  elements = elements[0]
  # メンションの場合，必ず elements の先頭にbotユーザIDが入っている（実用はIDも確認すること）
  mentioned = True if len(elements['elements']) >= 2 else False

  # 返信・処理
  if mentioned:
    # メンション
    # 正常ならば app_mentionも，ここも呼ばれる
    say(f"メンション: {message}")
  else:
    # メッセージ
    say(f"メッセージ: {message}")


# 初期化
app = App(token=bot_token)

# メッセージ受信待ち
@app.event("message")
def message_receive(message, say):
  # 'message' には ack は不要
  if VERBOSE: print(f"MESSAGE: {message}", file=sys.stderr)
  recv_message(message, say)


# メンション
@app.event("app_mention")
def mention_handler(body, say):
  # 'app_mention' には ack は不要
  mention = body["event"]
  text = mention["text"]
  channel = mention["channel"]
  thread_ts = mention["ts"]
  text = f"Mention: {text}"
  time.sleep(30)
  # say(text=text, channel=channel, thread_ts=thread_ts)
  say(text)


# スラッシュコマンド
@app.command("/test")
def handle_hello_command(ack, command, respond):
  # まず ack() を呼んで応答を返す（3秒ルール回避）
  ack()
  # デフォルトは発行者のみのエフェメラルメッセージ
  respond(f"こんにちは、<@{command['user_id']}> さん！")


if __name__ == "__main__":
  # ソケットモードで起動
  SocketModeHandler(app, app_token).start()
