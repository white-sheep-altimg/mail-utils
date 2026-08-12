# mail-utils

もはやメールとは無関係なものも追加しています。業務等で利用しているスクリプトを再利用を考慮し，簡略化／整理して置いています。

macOS Mail の SQLite データベース（`Envelope Index`）からメール情報を取得・出力する Python ユーティリティ、SMTP 経由で送信・返信する Python スクリプト、Mail 経由で送信・返信する AppleScript、Slack API を操作する Python スクリプトの集合。



## 前提条件

- **macOS 専用**。macOS Mail が設定されている環境で動作
- Python スクリプト実行前に「フルディスクアクセス」で Terminal / Python に権限を付与すること
- AppleScript スクリプトは Mail と System Events へのアクセス許可を許可すること
- SMTP 経由送信スクリプトは `email_config.py` に SMTP 設定を記載（`email_config.py-example` をコピーして使用）

## コマンド

### メール単件取得（ROWID 指定）

```bash
python3 get_mail_by_rowid.py <ROWID>
```

指定した ROWID のメールを JSON 形式で出力。ヘッダ情報と本文（text/plain 優先、なければ text/html をテキスト変換）を含む。

指定した ROWID のメールを JSON 形式で出力。ヘッダ情報と本文（text/plain 優先、なければ text/html をテキスト変換）を含む。

### メール一覧取得

```bash
python3 get_mail_list.py <最大件数> [<モード: 未読=0, 既読=1>]
```
最大件数はメールボックスから取得する件数のため，必ずしも最終出力とは一致しない。

### メール一覧（日付絞り込み）

```bash
python3 get_mail_list_by_date.py <最大件数> [<対象日>] [<モード: 未読=0, 既読=1>]
```

INBOX の指定された日付のメールを最新順に JSON 配列で出力。日付は '2026/01/10' のように指定する。
最大件数はメールボックスから取得する件数のため，必ずしも最終出力とは一致しない。

### SMTP 経由メール送信

```bash
python3 send_mail.py <To> <Subject> <Body>
```

設定ファイルに記載の SMTP 経由でメールを送信。FromアドレスはSMTPサーバに依存する場合が多いため設定で固定です。

### SMTP 経由メール返信

```bash
python3 reply_mail.py <ROWID> <Body>
```

ROWID から返信元メールのヘッダ・本文を取得し、本文を引用した上で SMTP 経由で返信送信。FromアドレスはSMTPサーバに依存する場合が多いため設定で固定です。

### メール送信

```bash
osascript send_mail.scpt 'From' 'To' 'Subject' '本文'
```

新規メールを Mail アプリ上に作成（ウィンドウ表示）。

### Message-ID 指定返信

```bash
osascript reply_by_message_id.scpt 'Message-ID' '[定型文]'
```

Message-ID からメールを検索し、返信ウィンドウを開いて定型文を貼り付けて送信。第2引数の定型文は省略可能（デフォルト文言あり）。
メール検索がとっても遅いので実用的では無いと思いますが、サンプルとして入れておきます。

### カレンダーへのイベント登録

```bash
python icalendar_add_event.py 'TITLE' 'START' 'END' 'DESCRIPTION' ['LOCATION'] ['URL']
```

日付形式：'2026/08/10 10:00'

### Slack メッセージ送信

```bash
python3 slack_send_message.py <"メッセージ">
```

指定した Slack チャンネルにメッセージを送信。長いテキストは `chunk_size` で指定した文字数ごとに分割して複数メッセージとして送信する。

### Slack ファイル内容送信

```bash
python3 slack_send_file.py <"ファイル名">
```

ファイルのコンテンツを読み取り、Slack チャンネルにメッセージとして送信。`slack_send_message.py` と同様に `chunk_size` ごとに分割する。

### Slack メッセージ取得

```bash
python3 slack_get_message.py [<最大件数> | <timestamp>]
```

引数なしまたは数値を指定した場合: チャンネルの履歴を最新から `limit` 件取得。
timestamp（ドット付き文字列）を指定した場合: そのスレッドの返信一覧を取得。

### Slack メッセージ受信（Socket Mode）

```bash
python3 slack_recv_message.py
```

Slack Bolt の Socket Mode で起動し、ボットがメッセージを受信するたびに自動返信（`RECV: 受信しました`）を行う。

## 設定

### SMTP 設定（`email_config.py`）

`email_config.py-example` をコピーして `email_config.py` を作成し、以下の項目を環境に合わせて編集する。

| キー | 説明 |
|------|------|
| `get_mail_by_rowid` | get_mail_by_rowid.pyのパス |
| `host` | SMTP サーバホスト |
| `port` | ポート番号 |
| `username` | 認証ユーザー名 |
| `password` | パスワード |
| `use_tls` | TLS 使用の有無（`True` / `False`） |
| `from_email` | 送信元メールアドレス |
| `from_name` | 送信者名 |
| `envelope_from` | envelope-from（HELO/EHLO用） |
| `mailbox` | メールボックス名 |

mailbox（メールボックス名）は必須ではありません。少し変わった運用をしているのでSQLで牽くと分かりにくく，便宜上追加したものです。

### Slack 設定（`.env` または `config.ini`）

Slack 関連スクリプトは，`.env` ファイルまたは `config.ini` の `[slack]` / `[bolt]` セクションから設定を読み込む。
`.env` 優先，見つからなければ `config.ini` から読み込む。

**.env**
| 変数名 | 説明 |
|--------|------|
| `bot_token` | Slack Bot User OAuth Token（`xoxb-...`） |
| `channel` | 送信先・取得元のチャンネル ID |
| `limit` | メッセージ取得件数のデフォルト値 |
| `chunk_size` | メッセージ分割時の1チャンクあたりの文字数 |
| `bolt_app_token` | Slack App Level Token（`xapp-...`、Socket Mode 用） |
| `bolt_bot_token` | Bot User OAuth Token（Bolt 用） |

```env
bot_token = xoxb-...
channel = Cxxxxxxxxxx
limit = 10
chunk_size = 2000

bolt_app_token = xapp-...
bolt_bot_token = xoxb-...
```

`example.env` をコピーして `.env` を作成し、各トークンを環境に合わせて編集する。

**config.ini**
```ini
[slack]
bot_token = xoxb-...
channel = Cxxxxxxxxxx
limit = 10
chunk_size = 2000

[bolt]
app_token = xapp-...
bot_token = xoxb-...
```

`config.ini-example` をコピーして `config.ini` を作成し、各トークンを環境に合わせて編集する。


## アーキテクチャ

### get_mail_by_rowid.py

1. SQLite（`Envelope Index`）から `messages` テーブルを JOIN し、ROWID・送信日・件名・送信者・メールボックスのメタ情報を取得
2. `find_emlx_file()` で `.emlx` 実体ファイルを `~/Library/Mail/V*/` 以下から検索
3. `.emlx` を MIME パースし、ヘッダと本文を抽出（text/plain → text/html → plain text 変換の優先順位）
4. quoted-printable の未デコードフォールバック対応

### get_mail_list.py

1. SQLite から `read = 0/1` かつ `mailbox_path LIKE '%INBOX%'` の条件でメールを検索
2. 結果を JSON 配列として出力（日付・件名・送信者・message_id・rowid）

### get_mail_list_by_date.py

1. SQLite から `read = 0/1` かつ `mailbox_path LIKE '%INBOX%'` の条件でメールを検索
2. 指定の日付（先頭から部分一致）のメールのみ抽出
3. 結果を JSON 配列として出力（日付・件名・送信者・message_id・rowid）

### send_mail.scpt

1. 引数（From, To, Subject, 本文）を受け取る
2. Mail アプリに新規送信メッセージを作成（ウィンドウ表示）

### reply_by_message_id.scpt

1. Message-ID を引数で受け取り、`< >` や空白を正規化
2. すべてのアカウント・メールボックスを走査して対象メールを検索
3. 見つかったメールを返信ウィンドウ付きで開く
4. 第2引数（またはデフォルト文言）をクリップボードにコピーし、System Events で `Cmd+V` 貼り付け
5. 直前の送信メッセージを送信

### send_mail.py

1. `email_config.py` から SMTP 設定を読み込む
2. `EmailMessage` を構築し、SMTP 経由で送信

### reply_mail.py

1. `email_config.py` から SMTP 設定を読み込む
2. `get_mail_by_rowid.py` を subprocess で実行し、返信元メールのヘッダ・本文を取得
3. 本文を `> ` プレフィックス付きで引用
4. `In-Reply-To` / `References` ヘッダを設定して SMTP 経由で送信

### slack_send_message.py

1. `.env` または `config.ini` からトークン・チャンネル・チャンクサイズを読み込む
2. 引数のメッセージを `chunk_size` 文字ごとに分割
3. `chat.postMessage` API でチャンクごとに POST 送信

### slack_send_file.py

1. `.env` または `config.ini` からトークン・チャンネル・チャンクサイズを読み込む
2. 引数のファイルを読み込み、内容を `chunk_size` ごとに分割
3. `chat.postMessage` API でチャンクごとに POST 送信

### slack_get_message.py

1. `.env` または `config.ini` からトークン・チャンネル・取得件数を読み込む
2. 引数が数値の場合: `conversations.history` API でチャンネル履歴を取得
3. 引数が timestamp（ドット付き）の場合: `conversations.replies` API でスレッド返信を取得

### slack_recv_message.py

1. `.env` または `config.ini` から App Token・Bot Token を読み込む
2. `slack_bolt.App` を初期化し、Socket Mode で接続
3. `message` イベントを受信すると自動で `say()` による返信

## 設計上の注意

- `.emlx` 検索は `os.walk` によるフルスキャン。メール数が多いと遅くなる可能性がある
- SQLite は LIMIT にパラメータバインドが使えないため、`get_unread_mail.py` では 1〜10000 の範囲バリデーション後、安全に埋め込んでいる
