from flask import Flask, render_template, g, request, redirect, url_for, Response
from flask_mysqldb import MySQL
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import os, calendar, io, math, datetime as dt, matplotlib.pyplot as plt
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

app = Flask(__name__, template_folder='./Xnk/templates', static_folder='./Xnk/static')
app.config.from_pyfile('config.py')

mysql, DATE = MySQL(app), date.today()

@app.route('/')
def index():
    global DATE, habit_packed
    DATE = date.today()
    return render_template("index.html")

def date_mgmt(offset=0):
    global DATE
    date_ = DATE
    if offset == 1:
        date_ += timedelta(days=1)
        DATE = date_
    elif offset == -1:
        date_ -= timedelta(days=1)
        DATE = date_
    elif offset == -30:
        date_ -= relativedelta(months=1)
        DATE = date_
    elif offset == 30:
        date_ += relativedelta(months=1)
        DATE = date_
    else:
        pass
    dateSqlFormat = date_.strftime("%Y-%m-%d")
    day = calendar.day_name[date_.weekday()]
    return dateSqlFormat, date_

def read_query(query, params=()):
    cur = mysql.connection.cursor()
    resultValue = cur.execute(query, params)
    if resultValue > 0:
        entries = cur.fetchall()
        return entries
    cur.close()
    return None

def write_query(query, params):
    cur = mysql.connection.cursor()
    cur.execute(query, params)
    mysql.connection.commit()
    cur.close()
    return 1

def growthbook_db(offset=0):
    global DATE
    dateSqlFormat, date_ = date_mgmt(offset=offset)
    gb_entries = read_query('SELECT * FROM GrowthBook WHERE Date = %s', (dateSqlFormat, ))
    notes_entries = read_query('SELECT Notes FROM Notes WHERE Date = %s', (dateSqlFormat, ))
    resultsValue = read_query('SELECT WakeupTime, SleepTime FROM WorkType WHERE Date = %s', (dateSqlFormat, ))
    wakeup_time, sleep_time = None, None
    if resultsValue is not None:
        wakeup_time, sleep_time = resultsValue[0][0], resultsValue[0][1]
    return dateSqlFormat, date_, gb_entries, notes_entries, wakeup_time, sleep_time

@app.route('/growth_book', methods=['GET', 'POST'])
def growth_book():
    dateSqlFormat, date_, gb_entries, notes_entries, wakeup_time, sleep_time = growthbook_db()
    dateRegFormat, day = date_.strftime("%d. %b, %Y"), calendar.day_name[date_.weekday()]
    todo_entries = read_query('SELECT ID, SUBSTRING(`Entry`, 1, 25) FROM ToDo LIMIT 7')
    resultsValue = read_query('SELECT * FROM WorkType WHERE Date = %s', (dateSqlFormat,))
    if resultsValue is None:
        write_query("INSERT INTO WorkType(Date, DeepWork, ShallowWork, Break, WakeupTime, SleepTime) VALUES(%s, 0, 0, 0, '0:00', '0:00')", (dateSqlFormat,))
    return render_template("growth_book.html", day=day, date=dateRegFormat, entries=gb_entries, todo_entries=todo_entries, notes_entries=notes_entries, wakeup_time=wakeup_time, sleep_time=sleep_time)

@app.route('/update_book', methods=['GET', 'POST'])
def update_book():
    data = request.get_json()
    time, entry = data[0].get('time'), data[1].get('entry')
    dateSqlFormat, date_ = date_mgmt()
    resultsValue = read_query('SELECT * FROM GrowthBook WHERE Date = %s AND Time = %s', (dateSqlFormat, time))
    if resultsValue is None:
        write_query("INSERT INTO GrowthBook(Date, Time, Entry) VALUES(%s, %s, %s)", (dateSqlFormat, time, entry))
    else:
        write_query("UPDATE GrowthBook SET Entry = %s WHERE Date = %s AND Time = %s", (entry, dateSqlFormat, time))
    return redirect(url_for('growth_book'))

@app.route('/growth_book_<prne>', methods=['GET', 'POST'])
def growth_book_previous(prne):
    offset = -1 if prne == "previous" else 1
    dateSqlFormat, date_, gb_entries, notes_entries, wakeup_time, sleep_time = growthbook_db(offset=offset)
    dateRegFormat, day = date_.strftime("%d. %b, %Y"), calendar.day_name[date_.weekday()]
    todo_entries = read_query('SELECT ID, SUBSTRING(`Entry`, 1, 25) FROM ToDo LIMIT 7')
    return render_template("growth_book.html", day=day, date=dateRegFormat, entries=gb_entries, todo_entries=todo_entries, notes_entries=notes_entries, wakeup_time=wakeup_time, sleep_time=sleep_time)

@app.route('/update_todo', methods=['GET', 'POST'])
def update_todo():
    todo = str(request.form['add_todo'])
    write_query("INSERT INTO ToDo(Entry) VALUES(%s)", (todo,))
    return redirect(url_for('growth_book'))

@app.route('/todo_finished', methods=['GET', 'POST'])
def todo_finished():
    todo = request.form['todo']
    write_query("DELETE FROM ToDo WHERE ID = %s", (todo,))
    return redirect(url_for('growth_book'))

@app.route('/all_todo')
def all_todo():
    dateSqlFormat, date_ = date_mgmt()
    dateRegFormat, day = date_.strftime("%d. %b, %Y"), calendar.day_name[date_.weekday()]
    cur = mysql.connection.cursor()
    count = cur.execute('SELECT ID, Entry FROM ToDo')
    todo_entries = None
    if count > 0:
        todo_entries = cur.fetchall()
    cur.close()
    return render_template("all_todo.html", day=day, date=date, count=count, todo_entries=todo_entries)

@app.route('/update_notes', methods=['GET', 'POST'])
def update_notes():
    dateSqlFormat, date_ = date_mgmt()
    notes = request.form['notes']
    resultsValue = read_query('SELECT * FROM Notes WHERE Date = %s', (dateSqlFormat,))
    if resultsValue is None:
        write_query("INSERT INTO Notes(Date, Notes) VALUES(%s, %s)", (dateSqlFormat, notes))
    else:
        write_query("UPDATE Notes SET Notes = %s WHERE Date = %s", (notes, dateSqlFormat))
    return redirect(url_for('growth_book'))

@app.route('/work_type', methods=['GET', 'POST'])
def work_type():
    dateSqlFormat, date_ = date_mgmt()
    data = request.get_json()
    workType = data[0].get('worktype')
    print(workType)
    if workType == "deep":
        write_query("UPDATE WorkType SET DeepWork = DeepWork + 0.5 WHERE Date = %s", (dateSqlFormat,)) 
    elif workType == "shallow":
        write_query("UPDATE WorkType SET ShallowWork = ShallowWork + 0.5 WHERE Date = %s", (dateSqlFormat,))
    else:
        write_query("UPDATE WorkType SET Break = Break + 0.5 WHERE Date = %s", (dateSqlFormat,))
    return redirect(url_for('growth_book'))

def get_workType_data(month=DATE.month, year=DATE.year):
    global packed_data
    data = read_query("SELECT * FROM WorkType WHERE MONTH(Date) = %s AND YEAR(Date) = %s", (month, year))
    month, deep, shallow, break_, sleep = [], [] , [], [], []
    if data is not None:
        data = list(data)
        for x in data:
            month.append(x[0].day)
            deep.append(x[1])
            shallow.append(x[2])
            break_.append(x[3])
            if x[4] is not None and x[5] is not None:
                hours_ = x[5]-x[4]
                sleep.append(24-(hours_.seconds)/3600)
            else:
                sleep.append(0)
    packed_data = [month, deep, shallow, break_, sleep]
    return 1 

@app.route('/growth_book/overview')
def gb_overview():
    dateSqlFormat, date_ = date_mgmt()
    dateRegFormat, day = date_.strftime("%d. %b, %Y"), calendar.day_name[date_.weekday()]
    month = date_.strftime("%B")
    get_workType_data()
    return render_template("overview.html", day=day, month=month, date=dateRegFormat)


@app.route('/plotting_<workType>.png')
def plotting(workType):
    global packed_data
    month, deep, shallow, break_, sleep = packed_data[0], packed_data[1], packed_data[2], packed_data[3], packed_data[4]
    fig = Figure(facecolor='#F6F0EF')
    axis = fig.add_subplot(1, 1, 1)
    x, y = month, []
    if workType == "deep":
        y = deep 
        axis.set_title("Deep Work", fontsize=20) 
    elif workType == "shallow":
        y = shallow
        axis.set_title("Shallow Work", fontsize=20)
    elif workType == "break":
        y = break_
        axis.set_title("Break", fontsize=20)
    elif workType == "sleep":
        y = sleep
        axis.set_title("Sleep", fontsize=20)
    axis.yaxis.grid()
    axis.set_facecolor('#F6F0EF')
    axis.plot(x, y)
    output = io.BytesIO()
    FigureCanvasAgg(fig).print_png(output)
    return Response(output.getvalue(), mimetype="image/png")

@app.route('/update_<wase>', methods=['GET', 'POST'])
def wake_up_time(wase):
    time = 'WakeupTime' if wase == 'wakeup' else 'SleepTime'
    dateSqlFormat, date_ = date_mgmt()
    wakeup = request.form['add_'+wase]
    print(wakeup)
    resultsValue = read_query('SELECT * FROM WorkType WHERE Date = %s', (dateSqlFormat,))
    if resultsValue is None:
        write_query("INSERT INTO WorkType(Date, {}) VALUES({}, {})".format(time, dateSqlFormat, wakeup))
    else:
        cur = mysql.connection.cursor()
        cur.execute("UPDATE WorkType SET {} = '{}' WHERE Date = '{}'".format(time, wakeup, dateSqlFormat))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('growth_book'))

@app.route('/overview_<prne>')
def overview_previous(prne):
    offset = -30 if prne == 'previous' else 30
    dateSqlFormat, date_ = date_mgmt(offset=offset)
    dateRegFormat, day = date_.strftime("%d. %b, %Y"), calendar.day_name[date_.weekday()]
    month = date_.strftime("%B")
    get_workType_data(date_.month)
    return render_template("overview.html", day=day, date=dateRegFormat, month=month)

@app.route('/habit_tracker')
def habit_tracker():
    global habit_packed
    habit_packed = get_habits()
    habit_id, habit_name, habit_last_date, habit_count, habit_streak, habit_section, highest_count, lowest_count, highest_streak, lowest_streak, habit_status = habit_packed
    return render_template('habit_tracker.html', **locals(), total_habits=len(habit_id), date_today = date.today().strftime("%Y-%m-%d"))

def get_habits():
    # Assuming there are always some habits
    global habit_packed
    entries = read_query('SELECT * FROM HabitTracker')
    habit_id, habit_name, habit_last_date, habit_count, habit_streak, habit_section, habit_status, habit_pin_number = [], [], [], [], [], [], [], []
    for x in entries:
        habit_id.append(x[0])
        habit_name.append(x[1])
        if x[2] is not None:
            habit_last_date.append(x[2].strftime("%Y-%m-%d"))
        else:
            habit_last_date.append(None)
        habit_count.append(x[3])
        habit_streak.append(x[4])
        habit_section.append(x[5])
        habit_status.append(x[6])
    highest_count = read_query('SELECT HabitName FROM HabitTracker ORDER BY Count DESC LIMIT 3')
    lowest_count = read_query('SELECT HabitName FROM HabitTracker ORDER BY Count ASC LIMIT 3')
    highest_streak = read_query('SELECT HabitName FROM HabitTracker ORDER BY Streak DESC LIMIT 3')
    lowest_streak = read_query('SELECT HabitName FROM HabitTracker ORDER BY Streak ASC LIMIT 3')
    habit_packed = [habit_id, habit_name, habit_last_date, habit_count, habit_streak, habit_section, highest_count, lowest_count, highest_streak, lowest_streak, habit_status]
    return habit_packed

@app.route('/habit_add', methods=['GET', 'POST'])
def habit_add():
    habit_section = request.form['habit_section']
    habit_name = request.form['habit_name']
    write_query('INSERT INTO HabitTracker(HabitName, Section, Count, Streak) VALUES(%s, %s, 0, 0)', (habit_name, habit_section))
    return redirect(url_for('habit_tracker'))

@app.route('/habit_pin', methods=['GET', 'POST'])
def habit_pin():
    habit_id = request.form['habit_id']
    min_id = read_query('SELECT MIN(ID) FROM HabitTracker')[0][0]
    write_query('UPDATE HabitTracker SET ID = %s, Status = %s WHERE ID = %s', (min_id - 1, 'Pinned', habit_id,))
    return redirect(url_for('habit_tracker'))

@app.route('/habit_unpin', methods=['GET', 'POST'])
def habit_unpin():
    habit_id = request.form['habit_id']
    max_id = read_query('SELECT MAX(ID) FROM HabitTracker')[0][0]
    write_query('UPDATE HabitTracker SET ID = %s, Status = %s WHERE ID = %s', (max_id + 1, 'Unpinned', habit_id))
    return redirect(url_for('habit_tracker'))


@app.route('/habit_update', methods=['GET', 'POST'])
def habit_update():
    dateSqlFormat, date_ = date_mgmt()
    habit_number, habit_last_date = request.form['habit_number'], request.form['habit_last_date']
    write_query('UPDATE HabitTracker SET Count = Count + 1 WHERE ID = %s', (habit_number, ))
    if habit_last_date == (date.today() - timedelta(days=1)).strftime("%Y-%m-%d"):
        write_query('UPDATE HabitTracker SET Streak = Streak + 1 WHERE ID = %s', (habit_number, ))
    write_query('UPDATE HabitTracker SET Date = %s WHERE ID = %s', (dateSqlFormat, habit_number))
    return redirect(url_for('habit_tracker'))

if __name__ == "__main__":
    app.run(debug=True)
