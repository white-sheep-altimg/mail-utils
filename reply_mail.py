import smtplib
from email.message import EmailMessage
from email_config import config
import uuid
import subprocess
import json
import base64


GET_MAIL_BY_ROWID = config['get_mail_by_rowid']
VERBOSE = False

def get_orig_mail(rowid):
    cmd = f"python {GET_MAIL_BY_ROWID} {rowid}"
    result = subprocess.Popen(cmd, stdout=subprocess.PIPE,shell=True).communicate()[0].decode('utf8')
    return json.loads(result)


def reply_email(from_addr, to_addr, subject, body, in_reply_to, references):

    msg = EmailMessage()
    msg.set_content(body)
    if subject[0:2] == 'Re':
        msg['Subject'] = subject
    else:
        msg['Subject'] = 'Re: ' + subject
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Message-ID'] = f"<{uuid.uuid4()}@{config['host']}>"
    msg['In-Reply-To'] = in_reply_to
    msg['References'] = in_reply_to + " " + references
    if VERBOSE: print(f"  {msg['Subject']}\n  {msg['From']} -> {msg['To']}", file=sys.stderr)

    try:
        with smtplib.SMTP(config['host'], config['port']) as server:
            if config['use_tls']:
                server.starttls()  # TLSの開始
            server.login(config['username'], config['password'])
            server.send_message(msg, from_addr=config['envelope_from'])
    except Exception as e:
        print(f"メールの返信に失敗しました: {e}", file=sys.stderr)



if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} <rowid> <Body>", file=sys.stderr)
        sys.exit(1)

    # 引数
    rowid = sys.argv[1]
    body = sys.argv[2]

    # 返信元メールを取得する（JSON形式）
    orig_mail = get_orig_mail(rowid)
    if len(orig_mail) <= 0 or 'error' in orig_mail:
        print(f"返信元メールが取得できませんでした: {rowid}", file=sys.stderr)
        sys.exit(1)

    # 返信元メールの情報を取得
    headers = orig_mail['headers']
    subject = headers['Subject']
    from_addr = headers['From']
    to_addr = headers['To']
    message_id = headers['Message-Id'] if 'Message-Id' in headers else ""
    in_reply_to = headers['In-Reply-To'] if 'In-Reply-To' in headers else ""
    references = headers['References'] if 'References' in headers else ""
    orig_body = orig_mail['body']
    orig_body = f'> {orig_body}'
    orig_body = orig_body.replace("\\", "\\\\").replace("\n", "\n> ")
    body = f"{body}\n\n{orig_body}"

    print(f"メールを送信します...")
    reply_email(from_addr, to_addr, subject, body, in_reply_to, references)
    print(f"メール送信完了")
