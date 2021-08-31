from __future__ import print_function
import datetime
import pickle
import json
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.pickle.
# remove .readonly if want to create events
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

HEX_TO_COLOR = {
    '#a4bdfc': 'Lavender',  # CS188
    '#7ae7bf': 'Sage',  # CHEM120A
    '#dbadff': 'Grape',  # Other
    '#ff887c': 'Flamingo',  # EECS16A
    '#fbd75b': 'Banana',  # CS194
    '#ffb878': 'Tangerine',  # Other
    '#46d6db': 'Peacock',  # Other
    '#e1e1e1': 'Graphite',  # Other
    '#5484ed': 'Blueberry',  # CBE160
    '#51b749': 'Basil',  # Other
    '#dc2127': 'Tomato'  # Important
}


def get_inputs():
    """
    Gets date and task mappings.
    """
    print('This program calculates how much time you have spent on a task in Google Calendar, sorted by color.')
    # get color to task mapping
    if os.path.exists('tasks.json'):
        print('Using existing task mapping at \'tasks.json\'.')
        with open('tasks.json', 'r') as file:
            color_to_task = json.load(file)
    else:
        color_to_task = {}
        print('You do not have a task mapping yet.')
        for hex, color in HEX_TO_COLOR.items():
            print('Enter task corresponding to \'%s\':' % color)
            task = input()
            color_to_task[color] = task
        with open('tasks.json', 'w') as file:
            json.dump(color_to_task, file)

    # get start and end times
    print('Please enter start date (YYYY-MM-DD):')
    start_date_str = input()
    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').replace(
        tzinfo=datetime.timezone(datetime.timedelta(hours=-7)))
    # datetime.datetime(2020, 3, 13, tzinfo=datetime.timezone(datetime.timedelta(hours=-7)))
    print('Please enter end date (YYYY-MM-DD):')
    end_date_str = input()
    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').replace(
        tzinfo=datetime.timezone(datetime.timedelta(hours=-7)))
    # datetime.datetime(2020, 3, 20, tzinfo=datetime.timezone(datetime.timedelta(hours=-7)))
    t_range = end_date - start_date
    print('Please enter how many days you would like to average over (e.g. enter 7 for a weekly average):')
    n = int(input())
    return start_date, end_date, t_range, n, color_to_task


def get_service():
    """
    Get creds and output to pickle file if they don't exist. Use creds to create
    Resource for interacting with Google Calendar API.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service


def get_events(startdate, enddate, service):
    """
    Get events within a certain range, in pacific time
    """
    tmin = startdate.isoformat()
    tmax = enddate.isoformat()
    event_results = service.events().list(calendarId='primary', timeMax=tmax, timeMin=tmin,
                                          singleEvents=True, orderBy='startTime').execute()
    return event_results.get('items', [])


def map_colorId_to_task(service, color_to_task):
    """
    Create mapping of colorId to hex for events.
    """
    colorId_to_hex = {}
    colorId_to_task = {}
    colors = service.colors().get().execute()
    for id, color in colors['event'].items():
        colorId_to_hex[id] = color['background']
    for id, hex in colorId_to_hex.items():
        colorId_to_task[id] = color_to_task[HEX_TO_COLOR[hex]]
    return colorId_to_task


def analyze(events, colorId_to_task, trange, n):
    """ 
    Group events by task and compute the average time spent per n days.
    """
    task_to_time = {}
    for event in events:
        try:
            colorId = event['colorId']
            task = colorId_to_task[colorId]
            if not task_to_time.get(task):
                task_to_time[task] = {'events': [],
                                      'time': datetime.timedelta(0)}
            summary = event['summary']
            start_time = datetime.datetime.fromisoformat(
                event['start']['dateTime'])
            end_time = datetime.datetime.fromisoformat(
                event['end']['dateTime'])
            event_time = end_time - start_time
            task_to_time[task]['events'].append((summary, event_time))
            task_to_time[task]['time'] += event_time
        except:
            print('[Uncategorized Task]: ', event['summary'])
    avg = str(n) + ' day average'
    for task in task_to_time:
        task_to_time[task][avg] = (
            task_to_time[task]['time'] / (trange / datetime.timedelta(n))).total_seconds() / 3600
    return task_to_time


def print_results(task_to_time, start_date, end_date, n):
    print('---------- %d day average from %s to %s ------------' %
          (n, str(start_date), str(end_date)))
    avg = str(n) + ' day average'
    for task in task_to_time:
        print('%s : %.2f hours' % (task, task_to_time[task][avg]))


def main():
    """
    Find events within user-specified range and specify average time spent.
    """
    start_date, end_date, t_range, n, color_to_task = get_inputs()
    service = get_service()
    events = get_events(start_date, end_date, service)
    colorId_to_task = map_colorId_to_task(service, color_to_task)

    if not events:
        print('No events found in this range.')

    task_to_time = analyze(events, colorId_to_task, t_range, n)
    print_results(task_to_time, start_date, end_date, n)


if __name__ == '__main__':
    main()
