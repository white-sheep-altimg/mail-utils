# mail-utils

macOS Mail の SQLite データベース（`Envelope Index`）からメール情報を取得・出力する Python ユーティリティ、SMTP 経由で送信・返信する Python スクリプト、Mail 経由で送信・返信する AppleScript の集合。Python スクリプトは外部依存なし（標準ライブラリのみ）。

## 前提条件

- **macOS 専用**。macOS Mail が設定されている環境で動作
- Python スクリプト実行前に「フルディスクアクセス」で Terminal / Python に権限を付与すること
- AppleScript スクリプトは Mail と System Events へのアクセス許可を許可すること
- SMTP 経由送信スクリプトは `email_config.py` に SMTP 設定を記載（`email_config.py-example` をコピーして使用）

## コマンド

### メール単件取得（ROWID 指定）

```bash
python3 get_mail_json.py <ROWID>
```

指定した ROWID のメールを JSON 形式で出力。ヘッダ情報と本文（text/plain 優先、なければ text/html をテキスト変換）を含む。

### 未読メール一覧取得

```bash
python3 get_unread_mail.py <最大件数>
```

INBOX の未読メールを最新順に JSON 配列で出力。

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

## 設定

### SMTP 設定（`email_config.py`）

`email_config.py-example` をコピーして `email_config.py` を作成し、以下の項目を環境に合わせて編集する。

| キー | 説明 |
|------|------|
| `host` | SMTP サーバホスト |
| `port` | ポート番号 |
| `username` | 認証ユーザー名 |
| `password` | パスワード |
| `use_tls` | TLS 使用の有無（`True` / `False`） |
| `from_email` | 送信元メールアドレス |
| `from_name` | 送信者名 |
| `envelope_from` | envelope-from（HELO/EHLO用） |



## アーキテクチャ

### get_mail_json.py

1. SQLite（`Envelope Index`）から `messages` テーブルを JOIN し、ROWID・送信日・件名・送信者・メールボックスのメタ情報を取得
2. `find_emlx_file()` で `.emlx` 実体ファイルを `~/Library/Mail/V*/` 以下から検索
3. `.emlx` を MIME パースし、ヘッダと本文を抽出（text/plain → text/html → plain text 変換の優先順位）
4. quoted-printable の未デコードフォールバック対応

### get_unread_mail.py

1. SQLite から `read = 0` かつ `mailbox_path LIKE '%INBOX%'` の条件で未読メールを検索
2. 結果を JSON 配列として出力（日付・件名・送信者・message_id・rowid）

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

## 設計上の注意

- `.emlx` 検索は `os.walk` によるフルスキャン。メール数が多いと遅くなる可能性がある
- SQLite は LIMIT にパラメータバインドが使えないため、`get_unread_mail.py` では 1〜10000 の範囲バリデーション後、安全に埋め込んでいる
