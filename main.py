import imaplib
import smtplib
import email

import sched, time
from config import EMAIL_ADDRESS, EMAIL_PASSWORD

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
        print('Setting msg seen', email_uid)
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
        print (efrom, eto, subject)
        msg = ''
        if subject.startswith('[hi]') or subject.startswith('[hello]'):
            msg = "\nHello " + ' '.join(efrom[:-1]) + "!\n\n\n- Sent from bot replica of Chirag Khurana!"
        if subject.startswith('[test]'):
            msg = "\n\nTesting you " + ' '.join(efrom[:-1]) + "!\n\n\n- Sent from bot replica of Chirag Khurana!"
        server.sendmail(eto[-1], efrom[-1], msg)
        print('Sent mail to', efrom)

s = sched.scheduler(time.time, time.sleep)
delay = 120

def keep_checking(mail, server, sc):
    print('Checking...')
    select(mail, 'inbox')
    mail_ids = get_unread_emails_uid(mail)
    print(mail_ids)
    email_list = get_all_emails(mail, mail_ids, True)
    print (email_list)
    test_sub(server, email_list)

    s.enter(delay, 1, keep_checking, (mail, server, sc))

if __name__ == '__main__':
    mail, server = login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    while True:
        try:
            s.enter(1, 1, keep_checking, (mail, server, s))
            s.run()
        except Exception as e:
            print(e)
            mail, server = login(EMAIL_ADDRESS, EMAIL_PASSWORD)



