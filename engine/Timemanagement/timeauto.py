import os
import subprocess
from humanfriendly import format_timespan
import numpy as np
from datetime import datetime, timedelta

def timesheet_tomorrow(work_type):

    # Format
    switch = 't s {}'.format(work_type)
    entry_format = "t in --at 'tomorrow {}' {}"
    out_format = "t out --at 'tomorrow {}'"

    # Entries
    time_in_entries, time_out_entries, planung = generic_schedule(work_type)
    if check_events_txt() == False:
        pass
    else:
        time_in_entries, time_out_entries, planung = tomorrow_events(work_type)
    
    # Later, move verification part to different function that returns True or False
    # Verification of entries
    time_in_entries, time_out_entries, planung = list(filter(None, time_in_entries)), list(filter(None, time_out_entries)), list(filter(None, planung))   # Filtering out empty entries if there exists.
    ntin = len(time_in_entries)
    ntout = len(time_out_entries)
    npl = len(planung)
    if ntin != ntout or ntin != npl or ntout != npl:
            print("The length of the entries do not match.")
            return 1 
    for i in range(ntin):
        x = datetime.strptime(time_in_entries[i], '%H:%M')
        y = datetime.strptime(time_out_entries[i], '%H:%M')
        if x > y:
            print("Exit time is ahead of entry in {} being entry time:{} and exit time:{}".format(work_type, x, y))
            return 1
        if i < (ntin - 1):
            x = datetime.strptime(time_in_entries[i+1], '%H:%M')
            y = datetime.strptime(time_in_entries[i], '%H:%M')
            if x < y:
                print("There is a clash in the schedule in {} entry time being {}.".format(work_type, x))
                return 1

    # Later, make an algorithm to either suggest or automatically fix the errors of entries with notifications if entries have been fixed
    
    queries = []
    for i in range(len(time_in_entries)):
        entry = entry_format.format(time_in_entries[i], planung[i])
        exit = out_format.format(time_out_entries[i])
        query = entry + ' && ' + exit
        queries.append(query)

    final_query = switch + ' && ' + ' && '.join(queries)
    
    return final_query

def generic_schedule(work_type):


    ''' Gives information about generic schedule of the week '''
    

    # Later, I'll keep the schedule in a separate file.
    # Work being dictionary key, can't be duplicate
    # Deep Work
    if work_type == 'Deep Work':
        monday = {
                'MP-Study': ['6:30', '9:00'],
                'Quasi-Free': ['10:00', '12:30']
                }
        tuesday = {
                'MITx': ['6:30', '9:00'],
                'MIT-x': ['10:00', '12:30']
                }
        wednesday = {
                'Penrose': ['6:30', '9:00'],
                'Quasi-Free': ['10:00', '12:30']
                }
        thursday = {
                'OneQuantum': ['6:30', '9:00'],
                'German': ['10:00', '12:30']
                }
        friday = {
                'MP-Study': ['6:30', '9:00'],
                'MP-Study': ['10:00', '9:00']
                }
        saturday = {
                'German': ['6:30', '9:00'],
                'OneQuantum':['10:00', '12:30']
                }
        sunday = {
                'Thesis': ['6:30', '9:00'],
                'Thesi-s': ['10:00', '12:30']
                }

    # Shallow Work
    elif work_type == 'Shallow Work':
        monday = {
                'LaTeX-Notes': ['14:00', '16:30'],
                'Web-Portfolio': ['16:30', '18:30']
                }
        tuesday = {
                'GUI-App': ['14:00', '16:30'],
                'Job-Search': ['16:30', '18:30']
                }
        wednesday = {
                'Grad-School': ['14:00', '16:30'],
                'Time-Management': ['16:30', '18:30']
                }
        thursday = {
                'Trading-Backtrader': ['14:00', '16:30'],
                'Job-Search': ['16:30', '18:30']
                }
        friday = {
                'GUI-App': ['14:00', '16:30'],
                'Grad-School': ['16:30', '18:30']
                }
        # Saturdays and Sundays are usually free days; taking care day; relaxing day; travels etc.
        saturday = {}
        sunday = {}

    week_day = datetime.today().weekday()
    options = {
            0: monday,
            1: tuesday,
            2: wednesday,
            3: thursday,
            4: friday,
            5: saturday,
            6: sunday
            }
    all_entries = options.get(week_day)
    time_entries, work_entries = np.array(list(all_entries.values())), list(all_entries.keys())
    time_in_entries, time_out_entries = list(time_entries[:,0]), list(time_entries[:,1])

    return time_in_entries, time_out_entries, work_entries
   
def tomorrow_events(work_type):

    ''' Reads a file and gets special events for tomorrow. '''
    f = open('events.txt', 'r')
    out = f.read().splitlines()
    events = [' '.join([x]).split() for x in out]
    dtie, dtoe, dp, stie, stoe, sp = [], [], [], [], [], []
    for i in range(len(events)):
        if events[i][0] == 'd':
            # Deep Work
            dtie.append(events[i][2])
            dtoe.append(events[i][3])
            dp.append(events[i][1])
        if events[i][0] == 's':
            # Shallow Work
            stie.append(events[i][2])
            stoe.append(events[i][3])
            sp.append(events[i][1])
    if work_type == 'Deep Work':
        return dtie, dtoe, dp
    else:
        return stie, stoe, sp

def free_times():
    ''' Calculates the free times of the day '''

    # Finding free time in the schedule
    start_times, end_times = [], []
    timesheets = ['Deep Work', 'Shallow Work']
    for j in range(2): # No. of Time-Sheets: Deep Work and Shallow Work
        os.system('t s {} >/dev/null 2>&1 '.format(timesheets[j]))
        # For tomorrow: 't d --start "tomorrow" --format csv'
        output = subprocess.run(['t today --format csv'], shell=True, capture_output=True, text=True).stdout.splitlines()[1:]
        print(output)
        for i in range(len(output)):
            event = [output[i]][0].split(',')
            event_start_date = datetime.strptime(event[0], '"%Y-%m-%d %H:%M:%S"')
            event_end_date = datetime.strptime(event[1], '"%Y-%m-%d %H:%M:%S"')
            start_time, end_time = event_start_date.time(), event_end_date.time()
            start_times.append(timedelta(hours=start_time.hour, minutes=start_time.minute))
            end_times.append(timedelta(hours=end_time.hour, minutes=end_time.minute))
    start_times.sort(), end_times.sort()
    start_time, end_time = start_times[1:], end_times[:-1]
    free_times = sum([(x-y).total_seconds() for x, y in zip(start_time, end_time)])
    early_time = datetime.strptime('7:00:00', '%H:%M:%S')
    et = timedelta(hours=early_time.hour, minutes=early_time.minute)
    bed_time = datetime.strptime('22:00:00', '%H:%M:%S')
    bt = timedelta(hours=bed_time.hour, minutes=bed_time.minute)
    boundary_free_time = ((start_times[0]-et) + (bt-end_times[-1])).total_seconds()
    total_free_time = format_timespan(free_times + boundary_free_time)
    return total_free_time

def check_events_txt():
    ''' This function checks if the events.txt file has been modified--in a sense that tomorrow events have been added. If not, the program aborts so that it does not create a mess in the schedule and notifies the user.'''
    current_status = subprocess.run(['stat -c %Y ~/Timemanagement/events.txt'], shell=True, capture_output=True, text=True).stdout.splitlines()[0]
    pre_status = 0
    f = open('status.txt', 'r')
    pre_status = f.readline()
    f.close()
    if current_status == pre_status:
        ''' File has not been changed --> Events have not been added '''
        return False
    else:
        g = open('status.txt', 'w')
        g.write(str(current_status))
        g.close()
        return True

def timesheet_update():
    ''' Updates the timesheet '''
    os.system(timesheet_tomorrow('Deep Work'))
    os.system(timesheet_tomorrow('Shallow Work'))
    os.system('Time-sheet successfully updated for tomorrow. Printing . . .')
    os.system('t s Deep Work && t week')
    os.system('t s Shallow Work && t week')

timesheet_update()
