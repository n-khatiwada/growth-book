import json
import subprocess
import pickle
import os
from datetime import datetime

def time_pause():
    idx, notes = running_tasks()

    # Remove pickle and do with file, 'status.txt'
    if idx != None:
        os.system('t edit --id {} --end "now" >/dev/null 1>&1 '.format(idx))
        with open('pickle_data', 'wb') as f:
            pickle.dump(notes, f)
        return 0
    else:
        print('You have no scheduled tasks')
        exit(0)
def time_play():
    notes = None
    with open('pickle_data', 'wb') as f:
        notes = pickle.load(f)
    if notes != None:
        os.system('t in notes >/dev/null 1>&1 '.format(notes))
        with open('pickle_data', 'wb') as f:
            pickle.dump([], f)
        return 0
    else:
        print('No Paused Entry found')
        return 1

def running_tasks():
    timesheets = ['Deep Work', 'Shallow Work']
    for j in range(2): # No. of Time-Sheets: Deep Work and Shallow Work
        os.system('t s {} >/dev/null 2>&1 '.format(timesheets[j]))
        garbage = subprocess.run(['t today -fjson'], shell=True, capture_output=True, text=True).stdout.splitlines()[0]
        if garbage != []:
            output = json.loads(garbage)
            for i in range(len(output)):
                event = output[i]
                event_start_date = datetime.strptime(event['start'], '%Y-%m-%d %H:%M:%S %z')
                event_end_date = datetime.strptime(event['end'], '%Y-%m-%d %H:%M:%S %z')
                idx, start_time, end_time, notes = event['id'], event_start_date.time(), event_end_date.time(), event['note']
                events = [idx, start_time, end_time, notes]
                today = datetime.today()
                if today.time() < events[2]:
                    if (today.time() > events[1]) and (today.time() < events[2]):
                        return idx, notes
        else:
            return None, None
