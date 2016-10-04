
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

from phue import Bridge
import datetime
import json, requests

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'config/client_secret.json'
APPLICATION_NAME = 'Calendar-Hue'
BRIDGE_IP_FINDER_URL = 'https://www.meethue.com/api/nupnp'

NOTIFY_THRESHOLD_SECOND = 600
HUE_LIGHT_ID = 2
HUE_NORMAL_COLOR = [0.3657,0.4331]
HUE_ALERT_COLOR = [0.674,0.322]
HUE_TRANSITION_TIME = 50

def alert_time_limit():
    b = Bridge(get_bridge_ip())
    b.connect()
    b.logging=('debug')
    b.set_light(HUE_LIGHT_ID, 'xy', HUE_ALERT_COLOR,transitiontime = HUE_TRANSITION_TIME)

def set_normal():
    b = Bridge(get_bridge_ip())
    b.connect()
    b.logging=('debug')
    b.set_light(HUE_LIGHT_ID, 'xy', HUE_NORMAL_COLOR,transitiontime = HUE_TRANSITION_TIME)

def get_bridge_ip():
    resp = requests.get(url=BRIDGE_IP_FINDER_URL)
    data = json.loads(resp.text)
    return data[0]['internalipaddress']


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    eventsResult = service.events().list(
        calendarId='giftee.co_2d3935303830373930333936@resource.calendar.google.com', timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])


    # TODO noitem found
    print(datetime.datetime.strptime(events[0]['start']['dateTime'], '%Y-%m-%dT%H:%M:%S+09:00'))

    nextStartTime = datetime.datetime.strptime(events[0]['start']['dateTime'], '%Y-%m-%dT%H:%M:%S+09:00')
    delta = (nextStartTime - datetime.datetime.now()).total_seconds()

    if delta < 0:
        print("capture next")
        nextStartTime = datetime.datetime.strptime(events[1]['start']['dateTime'], '%Y-%m-%dT%H:%M:%S+09:00')
        delta = (nextStartTime - datetime.datetime.now()).total_seconds()

    print(delta)

    if NOTIFY_THRESHOLD_SECOND > delta:
        alert_time_limit()
    else:
        set_normal()



    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


if __name__ == '__main__':
    main()
