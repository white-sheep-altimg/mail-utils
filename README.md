# mail-utils

macOS Mail の SQLite データベース（`Envelope Index`）からメール情報を取得・出力する Python ユーティリティ群。外部依存なし（標準ライブラリのみ）。

## 前提条件

- **macOS 専用**。macOS Mail が設定されている環境で動作
- スクリプト実行前に macOS の「システム設定 → プライバシーとセキュリティ → フルディスクアクセス」で Terminal / Python に権限を付与すること

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

## アーキテクチャ

### get_mail_json.py

1. SQLite（`Envelope Index`）から `messages` テーブルを JOIN し、ROWID・送信日・件名・送信者・メールボックスのメタ情報を取得
2. `find_emlx_file()` で `.emlx` 実体ファイルを `~/Library/Mail/V*/` 以下から検索
3. `.emlx` を MIME パースし、ヘッダと本文を抽出（text/plain → text/html → plain text 変換の優先順位）
4. quoted-printable の未デコードフォールバック対応

### get_unread_mail.py

1. SQLite から `read = 0` かつ `mailbox_path LIKE '%INBOX%'` の条件で未読メールを検索
2. 結果を JSON 配列として出力（日付・件名・送信者・message_id・rowid）

## 設計上の注意

- `.emlx` 検索は `os.walk` によるフルスキャン。メール数が多いと遅くなる可能性がある
- SQLite は LIMIT にパラメータバインドが使えないため、`get_unread_mail.py` では 1〜10000 の範囲バリデーション後、安全に埋め込んでいる
