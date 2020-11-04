import datetime
import time
import winsound
from logging import Handler, Formatter
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

import requests
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = 'your telegram token'
TELEGRAM_CHAT_ID = 'your chat id'


class RequestsHandler(Handler):
    def emit(self, record):
        log_entry = self.format(record)
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': log_entry,
            'parse_mode': 'HTML'
        }
        return requests.post("https://api.telegram.org/bot{token}/sendMessage".format(token=TELEGRAM_TOKEN),
                             data=payload).content


class LogstashFormatter(Formatter):
    def __init__(self):
        super(LogstashFormatter, self).__init__()

    def format(self, record):
        t = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        return "<i>{datetime}</i><pre>\n{message}</pre>".format(message=record.msg, datetime=t)


def telegram_bot_sendtext(bot_message):
    bot_token = 'your bot token'
    bot_chatID = 'your chat id'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + 'divar.ir' + bot_message

    response = requests.get(send_text)

    return response.json()


def send_mail(content):
    # The mail addresses and password
    sender_address = 'email address'
    sender_pass = 'email pass'
    receiver_address = 'reciever email address'
    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'New House'  # The subject line
    # The body and the attachments for the mail
    message.attach(MIMEText(content, 'plain'))
    # Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    session.login(sender_address, sender_pass)  # login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent: ' + str(datetime.now()))


def find_last_post():
    url = "URL with desired filters on divar"
    page = requests.get(url)
    page = page.content
    htmls = BeautifulSoup(page, 'html.parser')
    selector = htmls.select(
        '#app > div.col-md-12.p-none.browse > main > div.blurring.dimmable > div.browse-post-list > a:nth-child(1)')
    link = str(selector[0]).split(' ')
    href = link[7].split("\"")

    return href[1]

# for handling network consumption
def sleep_handler():
    now = datetime.now()
    if now.hour == 23 or 9 >= now.hour >= 0:
        return 3600
    else:
        return 60


posts = []
while True:
    try:
        loaded = find_last_post()
        break
    except:
        print("error running: " + str(datetime.now()))
check_new = loaded
print('starting: ' + str(datetime.now()))
while True:
    time.sleep(sleep_handler())
    try:
        check_new = find_last_post()
    except:
        print('could not get post: ' + str(datetime.now()))
        continue
    if loaded == check_new:
        print('nothing new:' + str(datetime.now()))
    elif loaded != check_new and check_new not in posts:
        posts.append(check_new)
        print('found one: ' + str(datetime.now()))
        print(check_new)
        winsound.Beep(2000, 1000)
        loaded = check_new
        mail_content = 'divar.ir' + loaded
        i = 0
        # mail
        while True:
            try:
                send_mail(mail_content)
            except:
                print('Could not send mail, Trying...: ' + str(datetime.now()))
            else:
                break
        # Telegram
        while i < 5:
            try:
                telegram_bot_sendtext(loaded)
                i = i + 1
            except:
                print('could not send message, Trying...: ' + str(datetime.now()))
            else:
                print('telegrammed: ' + str(datetime.now()))
                break
failed = 'process failed'
send_mail(failed)
telegram_bot_sendtext(failed)
