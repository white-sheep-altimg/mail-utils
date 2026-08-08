# mail-utils

macOS Mail の SQLite データベース（`Envelope Index`）からメール情報を取得・出力する Python ユーティリティと、Mail 経由で送信・返信する AppleScript の集合。Python スクリプトは外部依存なし（標準ライブラリのみ）。

## 前提条件

- **macOS 専用**。macOS Mail が設定されている環境で動作
- Python スクリプト実行前に「フルディスクアクセス」で Terminal / Python に権限を付与すること
- AppleScript スクリプトは Mail と System Events へのアクセス許可を許可すること

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
メール検索がとっても遅いので実用的では無いと思いますが，サンプルとして入れておきます。


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

## 設計上の注意

- `.emlx` 検索は `os.walk` によるフルスキャン。メール数が多いと遅くなる可能性がある
- SQLite は LIMIT にパラメータバインドが使えないため、`get_unread_mail.py` では 1〜10000 の範囲バリデーション後、安全に埋め込んでいる
