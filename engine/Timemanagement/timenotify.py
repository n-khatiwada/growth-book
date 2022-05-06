import subprocess
import os
from humanfriendly import format_timespan
from datetime import datetime, timedelta

min_ut = datetime.strptime('23:59:59', '%H:%M:%S')
timesheets, upcoming_tasks, running_tasks, min_ust, min_event = ['Deep Work', 'Shallow Work'], [], [], timedelta(hours=min_ut.hour, minutes=min_ut.minute), None
for j in range(2): # No. of Time-Sheets: Deep Work and Shallow Work
    os.system('t s {} >/dev/null 2>&1 '.format(timesheets[j]))
    # os.system('t s {}'.format(timesheets[j]))
    output = subprocess.run(['t today --format csv'], shell=True, capture_output=True, text=True).stdout.splitlines()[1:]
    if output != []:
        for i in range(len(output)):
            event = [output[i]][0].split(',')
            event_start_date = datetime.strptime(event[0], '"%Y-%m-%d %H:%M:%S"')
            event_end_date = datetime.strptime(event[1], '"%Y-%m-%d %H:%M:%S"')
            start_time, end_time, notes = event_start_date.time(), event_end_date.time(), event[2][1:-1] 
            events = [start_time, end_time, notes]
            today = datetime.today()
            if today.time() < events[1]:
                if (today.time() > events[0]) and (today.time() < events[1]):
                    t1 = timedelta(hours=events[1].hour, minutes=events[1].minute)
                    t2 = timedelta(hours=today.time().hour, minutes=today.time().minute)
                    duration = format_timespan((t1 - t2).total_seconds())
                    running_tasks.append(events[2])
                    running_tasks.append(duration)
                elif today.time() < events[0]:
                    t1 = timedelta(hours=events[0].hour, minutes=events[0].minute)
                    if t1.total_seconds() < min_ust.total_seconds():
                        min_event = events
                        min_ust = t1
    else:
        print('You have no tasks scheduled')
        exit(0)
t2 = timedelta(hours=today.time().hour, minutes=today.time().minute)
duration = format_timespan((min_ust - t2).total_seconds())
if min_event is not None:
    upcoming_tasks.append(min_event[2])
    upcoming_tasks.append(duration)
if (len(running_tasks) > 1) and (len(upcoming_tasks) > 1) :
    print('{} ends in {}. Next {}'.format(running_tasks[0], running_tasks[1], upcoming_tasks[0]))
elif len(upcoming_tasks) < 1 and (len(running_tasks) > 1):
   print('{} ends in {}'.format(running_tasks[0], running_tasks[1]))
elif (len(running_tasks) < 1) and (len(upcoming_tasks) > 1):
    print('Next: {} starts in {}'.format(upcoming_tasks[0], upcoming_tasks[1]))
else:
    print('You have no tasks scheduled')
