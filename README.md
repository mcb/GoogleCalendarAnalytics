# GoogleCalendarAnalytics
Code to get summary of time spent on each color in Google Calendar. Code will prompt you to specify the task that maps to each color,
the start date and end date of your query, and how many days you want to average over (e.g. 7 for a weekly average).

If you want to change the task mapping, delete or modify tasks.json (the code will prompt you to create a new one if it doesn't exist
in your directory).

You will need to first turn on the Google Calendar API here (https://developers.google.com/calendar/quickstart/python)
and save credentials.json to working directory.

API: 
https://developers.google.com/calendar/concepts
https://developers.google.com/resources/api-libraries/documentation/calendar/v3/python/latest/index.html
