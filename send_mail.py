import smtplib
from email.message import EmailMessage
from email_config import config
import uuid

def send_email(from_addr, to_addr, subject, body):

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = f"{config['from_name']} <{config['from_email']}>"
    msg['To'] = to_addr
    msg['Message-ID'] = f"<{uuid.uuid4()}@{config['host']}>"

    try:
        with smtplib.SMTP(config['host'], config['port']) as server:
            if config['use_tls']:
                server.starttls()  # TLSの開始
            server.login(config['username'], config['password'])
            server.send_message(msg, from_addr=config['envelope_from'])
    except Exception as e:
        print(f"メール送信に失敗しました: {e}", file=sys.stderr)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print(f"Usage: python {sys.argv[0]} <To> <Subject> <Body>", file=sys.stderr)
        sys.exit(1)

    from_addr = f"{config['from_name']} <{config['from_email']}>"
    to_addr = sys.argv[1]
    subject = sys.argv[2]
    body = sys.argv[3]

    print(f"メールを送信します...")
    send_email(from_addr, to_addr, subject, body)
    print(f"メール送信完了")
