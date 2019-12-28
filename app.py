import imaplib
import time
import os
import email
import sys
import creds

from datetime import datetime
from multiprocessing import Process

def main():
    while True:
        try:
            console_text = '[Console]'
            email_user = creds.email_address
            email_pass = creds.email_password
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            print(datetime.now(), console_text, 'Signing in...')
            typ, accountDetails = mail.login(email_user, email_pass)

            if typ != 'OK':
                raise Exception("Not able to sign in!")
            if typ == 'OK':
                print(datetime.now(), console_text, 'Signed in!')
            print(datetime.now(),console_text,'Checking for new emails...')
            mail.select('Inbox')
            typ, data = mail.search(None, 'NOT', 'SEEN')
            if typ != 'OK':
                raise Exception('Error searching inbox!')
            mail_ids = data[0]
            id_list = mail_ids.split()
            if id_list == []:
                print(datetime.now(),console_text,'No new emails found.')
            else:
                print(datetime.now(),console_text,'New emails found. Fetching mail and scanning for attachments...')
            for num in data[0].split():
                typ, data = mail.fetch(num, '(RFC822)')
                if typ != 'OK':
                    raise Exception('Error fetching mail!')
                raw_email = data[0][1]
                raw_email_string = raw_email.decode('utf-8')
                email_message = email.message_from_string(raw_email_string)
                for part in email_message.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue
                    fileName = part.get_filename()
                    if bool(fileName):
                        print(datetime.now(),console_text,'Attachment found:',fileName)
                        print(datetime.now(),console_text,'Attempting to download...')
                        filePath = os.path.join('c:/temp', fileName)
                        print(datetime.now(), console_text, 'Checking if file exists and writing file to:', filePath)
                        if not os.path.isfile(filePath):
                            print(datetime.now(), console_text, 'File does not exist! Writing to disk...', filePath)
                            fp = open(filePath, 'wb')
                            fp.write(part.get_payload(decode=True))
                            fp.close()
                            if os.path.isfile(filePath):
                                print(datetime.now(), console_text, 'Sucessfully downloaded attachment:', fileName)
                        else:
                            print(datetime.now(), console_text, 'File already exists. Skipping.', filePath)
                        subject = str(email_message).split("Subject: ", 1)[1].split("\nTo:", 1)[0]
                    else:
                        print(datetime.now(),console_text,'No attachments found.')
            print(datetime.now(),console_text,'Sleeping for 15 minutes.')
            time.sleep(900)
        except KeyboardInterrupt:
            print(datetime.now(), console_text, 'Logging out and closing...')
            mail.close()
            print(mail.state)
            mail.logout()
            print(mail.state)
            sys.exit()

if __name__ == '__main__':
    p1 = Process(target=main)
    p1.start()