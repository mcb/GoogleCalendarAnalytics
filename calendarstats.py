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
    '#51b749' : 'Other', # Basil
    '#dc2127': 'Important' # Tomato
} 

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

def get_dates():
    # datetime.datetime(endyear, endmonth, endday, tzinfo=datetime.timezone(datetime.timedelta(hours=-7))).isoformat()
    start_date = datetime.datetime(2020, 3, 13, tzinfo=datetime.timezone(datetime.timedelta(hours=-7)))
    end_date = datetime.datetime(2020, 3, 20, tzinfo=datetime.timezone(datetime.timedelta(hours=-7)))
    t_range = end_date - start_date
    return start_date, end_date, t_range

def get_events(startdate, enddate, service):
    """
    Get events within a certain range, in pacific time
    """
    tmin = startdate.isoformat()
    tmax = enddate.isoformat()
    event_results = service.events().list(calendarId='primary', timeMax=tmax, timeMin=tmin,
                                   singleEvents=True, orderBy='startTime').execute()
    return event_results.get('items', [])


def map_colorId_to_hex(service):
    """
    Create mapping of colorId to hex for events.
    """
    colorId_to_hex = {}
    colors = service.colors().get().execute()
    for id, color in colors['event'].items():
        colorId_to_hex[id] = color['background']
    return colorId_to_hex

def analyze(events, colorId_to_hex, trange, n=7):
    """ 
    Group events by task and compute the average time spent per n days.
    """
    task_to_time = {}
    for event in events:
        try:
            colorId = event['colorId']
            hex_color = colorId_to_hex[colorId]
            task = HEX_TO_TASK[hex_color]
            if not task_to_time.get(task):
                task_to_time[task] = {'events' : [], 'time' : datetime.timedelta(0)}
            summary = event['summary']
            start_time = datetime.datetime.fromisoformat(event['start']['dateTime'])
            end_time = datetime.datetime.fromisoformat(event['end']['dateTime'])
            event_time = end_time - start_time
            task_to_time[task]['events'].append((summary, event_time))
            task_to_time[task]['time'] += event_time
        except:
            print('[Uncategorized Task]: ', event['summary'])
    avg = str(n) + ' day average'
    for task in task_to_time:
        task_to_time[task][avg] = (task_to_time[task]['time'] / (trange / datetime.timedelta(n))).total_seconds() / 3600
    return task_to_time, n

def print_results(task_to_time, start_date, end_date, n):
    print('---------- %d day average from %s to %s ------------' % (n, str(start_date), str(end_date)))
    avg = str(n) + ' day average'
    for task in task_to_time:
        print('%s : %.2f hours' % (task, task_to_time[task][avg]))

def main():
    """
    Find events within user-specified range and specify average time spent.
    """
    start_date, end_date, t_range = get_dates()
    service = get_service()
    events = get_events(start_date, end_date, service)
    colorId_to_hex = map_colorId_to_hex(service)

    if not events:
        print('No events found in this range.')

    task_to_time, n = analyze(events, colorId_to_hex, t_range)
    print_results(task_to_time, start_date, end_date, n)

if __name__ == '__main__':
    main()
