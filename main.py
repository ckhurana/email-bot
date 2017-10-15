import imaplib
import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import sched, time
from config import EMAIL_ADDRESS, EMAIL_PASSWORD

# Globals
s = sched.scheduler(time.time, time.sleep)
delay = 10
mail = ''
server = ''

def login(email, password):
    mail = imaplib.IMAP4_SSL('imap.zoho.com')
    mail.login(email, password)
    server = smtplib.SMTP_SSL('smtp.zoho.com', 465)
    server.login(email, password)
    return mail, server

def list_labels(mail):
    return mail.list()

def select(mail, s):
    mail.select(s)

def get_all_emails_uid(mail):
    return mail.uid('search', None, 'ALL')[1][0].decode('utf-8').split()

def get_unread_emails_uid(mail):
    return mail.uid('search', None, '(UNSEEN)')[1][0].decode('utf-8').split()

def update_read_status(mail, email_uid):
    mail.uid('store', email_uid, '+FLAGS', '(\\SEEN)')

def get_email(mail, email_uid, set_seen=True):
    res, raw_email = mail.uid('fetch', email_uid, '(RFC822)')
    str_email = raw_email[0][1].decode('utf-8')
    email_msg = email.message_from_string(str_email)
    if set_seen:
        # print('Setting msg seen', email_uid)
        update_read_status(mail, email_uid)
    return email_msg

def get_all_emails(mail, email_uid_list, set_seen=True):
    email_list = []
    if len(email_uid_list) > 0:
            for i in list(reversed(email_uid_list)):
                email_msg = get_email(mail, i, set_seen)
                email_list.append(email_msg)
                # print(email_msg['From'], '->' , email_msg['To'], '-' , email_msg['Subject'])
    else:
        print('No mails available in the list.')
    return email_list

def test_sub(server, email_list):
    for e in email_list:
        subject = e['Subject'].lower().strip()
        efrom = e['From'].split()
        eto = e['To'].split()
        esub = e['Subject'].strip()
        # print (eto, efrom, subject)
        msg = ''

        validMail = True
        isHtml = False
        if subject.startswith('[hi]') or subject.startswith('[hello]'):
            msg = "Hello " + ' '.join(efrom[:-1]) + "!\n\n\n- Sent from bot replica of Chirag Khurana!"
        elif subject.startswith('[test]'):
            msg = "Testing you " + ' '.join(efrom[:-1]) + "!\n\n\n- Sent from bot replica of Chirag Khurana!"
        
        # My profile information
        elif subject.startswith('[ck]'):
            msg = """\
                <html>
                <body>
                    <h3>HELLO!</h3> 
                    <h3>I'm Chirag Khurana, a developer with a designer's state of mind based out of Delhi, India.<br/>In my spare time, I'm Batman.</h3>
                    <br>
                    <div class="projects"> 
                        <h4>A few things I've worked on</h4>
                        <ul>
                            <li><a href="https://play.google.com/store/apps/details?id=com.zuccessful.zallpaper">
                                <h4>ZALLS - WALLPAPERS</h4>
                            </a></li>

                            <li><a href="http://labs.chiragkhurana.com">
                                <h4>CK LABS</h4>
                            </a></li>

                            <li><a href="http://btech.chiragkhurana.com?sort=percentage&order=desc">
                                <h4>RESULT SCRAPER</h4>
                            </a></li>

                            <li><a href="http://kicka55studios.in">
                                <h4>KICKA55 STUDIOS</h4>
                            </a></li>
                        </ul>
                    </div>

                    <div class="footer">
                        <h4>Online Presence</h4>
                        <ul>
                            <li><a href="https://github.com/ckhurana" class="fa fa-github fa-lg">Github</a></li>
                            <li><a href="https://www.linkedin.com.in/khuranachirag" class="fa fa-linkedin fa-lg">LinkedIn</a></li>
                            <li><a href="https://twitter.com/ChiragKhurana95" class="fa fa-twitter fa-lg">Twitter</a></li>
                            <li><a href="https://www.behance.net/chiragkhurana" class="fa fa-behance fa-lg">Behance</a></li>
                            <li><a href="https://www.instagram.com/chirag.in" class="fa fa-instagram fa-lg">Instagram</a></li>
                            <li>Contact me: <b>me [at] chiragkhurana [dot] com</b></li>
                        </ul>
                        <br>
                        <p>&copy; 2017 | <a href="http://chiragkhurana.com">Chirag Khurana</a></p>
                    </div>
                </body>
                </html>
            """
            isHtml = True
        else:
            validMail = False
        

        # server.sendmail(eto[-1], efrom[-1], msg)
        if validMail:
            efrom, eto = eto[-1], efrom[-1]
            sendMail(efrom, eto, esub, msg, isHtml)
            print('Sent mail to', eto)


def sendMail(me, you, subject, content, isHtml=False):
    global mail, server
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = you
    if isHtml:
        part = MIMEText(content, 'html') 
    else:
        part = MIMEText(content, 'plain')
    msg.attach(part)
    try:
        server.sendmail(me, you, msg.as_string())
    except Exception as e:
        mail, server = login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(me, you, msg.as_string())


def keep_checking(mail, server, sc):
    print('-' * 40)
    print('Checking...')
    select(mail, 'inbox')
    mail_ids = get_unread_emails_uid(mail)
    # print(mail_ids)
    email_list = get_all_emails(mail, mail_ids, True)
    # print (email_list)
    test_sub(server, email_list)
    s.enter(delay, 1, keep_checking, (mail, server, sc))


if __name__ == '__main__':
    global mail, server
    mail, server = login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    while True:
        try:
            s.enter(1, 1, keep_checking, (mail, server, s))
            s.run()
        except Exception as e:
            print(e)
            server.quit()
            mail, server = login(EMAIL_ADDRESS, EMAIL_PASSWORD)



