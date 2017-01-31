#!/usr/bin/env python



import os
import base64
import argparse
import httplib2
import urllib.request

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()



SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'gmail-sbb-receipt-downloader'


SEARCH_QUERY="Ihre Bestellung im SBB Mobile Ticket Shop"
SEARCH_OPERATOR="newer_than:31d"
DOWNLOAD_PATH="/home/eni/adsy/spesen/sbb"


def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'gmail-sbb-receipt.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)
    return credentials



def get_sbb_receipt_url(messages, mid):
    mres = messages.get(userId='me', id=mid).execute()
    datab64 = mres['payload']['body']['data']
    data = base64.b64decode(datab64).decode()
    for line in data.split("\n"):
        line = line.strip()
        if line.find("https://www")>-1 and line.find(".pdf")>-1:
            return line


def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    users = service.users()
    messages = users.messages()

    query = "%s %s" % (SEARCH_QUERY, SEARCH_OPERATOR)
    res = messages.list(userId='me', q=query).execute()

    find_num = res["resultSizeEstimate"]
    print("Found %i matching messages" % find_num)
    for message in res["messages"]:
        url = get_sbb_receipt_url(messages, message['id'])
        bname = os.path.basename(url)
        dlpath = "%s/%s" % (DOWNLOAD_PATH, bname)
        if not os.path.exists(dlpath):
            print("Downloading %s" % bname)
            urllib.request.urlretrieve(url, dlpath)
        else:
            print("Receipt %s allready exists on file system" % bname)



if __name__ == '__main__':
    main()
