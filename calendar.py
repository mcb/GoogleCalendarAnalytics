from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
# remove .readonly if want to create events
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

HEX_TO_TASK = {
    '#a4bdfc' : 'CS188', # Lavender
    '#7ae7bf' : 'CHEM120A', # Sage
    '#dbadff' : 'Other', # Grape
    '#ff887c' : 'EECS16A', # Flamingo
    '#fbd75b' : 'CS194', # Banana
    '#ffb878' : 'Other', # Tangerine
    '#46d6db' : 'Other', # Peacock
    '#e1e1e1' : 'Other', # Graphite
    '#5484ed' : 'CBE160', # Blueberry
    '#51b749' : 'Other' # Basil
    '#dc2127': 'Important' # Tomato
} 

# From Calendar, aggregate Events using Color
# sum up end.dateTime - start.dateTime

def get_service():
    """
    Get creds and output to pickle file if they don't exist. Use creds to create
    Resource for interacting with Google Calendar API.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service


def get_events(startyear, startmonth, startday, endyear, endmont, endday, service):
    """
    Get events within a certain range, in pacific time
    """
    tmin = datetime.datetime(startyear, startmonth, startday,
                             tzinfo=datetime.timezone(datetime.timedelta(hours=-7))).isoformat()
    tmax = datetime.datetime(endyear, endmonth, endday,
                             tzinfo=datetime.timezone(datetime.timedelta(hours=-7))).isoformat()
    events = service.events().list(calendarId='primary', timeMax=tmax, timeMin=tmin,
                                   singleEvents=True, orderBy='startTime').execute()
    return events


def map_colorId_to_hex(service):
    """
    Create mapping of colorId to hex for events.
    """
    colorId_to_hex = {}
    for id, color in colors['event'].items():
        colorId_to_hex[id] = color['background']
    return colorId_to_hex

def analyze():


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


if __name__ == '__main__':
    main()
