import imaplib
from email.parser import HeaderParser
from email.policy import default

def checkEmail():
    M = imaplib.IMAP4_SSL('smtp.gmail.com')
    user = 'EmailName@gmail.com'
    password = 'EmailPassword'
    M.login(user, password)

    M.select('INBOX')

    # Search for new unread emails
    typ, data = M.search(None, 'UNSEEN')
    if data[0]:
        # Get the latest email's subject
        latest_email_id = data[0].split()[-1]
        data = M.fetch(latest_email_id, '(BODY[HEADER])')
        header_data = data[1][0][1].decode('utf-8')
        parser = HeaderParser(policy=default)
        msg = parser.parsestr(header_data)
        return msg['subject']

    # No new unread emails found
    return None
