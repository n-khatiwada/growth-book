from flask import Flask, render_template
from flaskwebgui import FlaskUI
from flask import current_app, g
import os
import sqlite3

app = Flask(__name__)
app.config.from_object('config')

################             CONFIGURATION           #######################

main_menu = {
        'Home': ['bi bi-house-fill', ['Overview', 'To-do']],
        'Quantum Mechanics': ['bi bi-bullseye', ['Overview', 'Notes']],
        'Calendar': ['bi bi-calendar-week-fill'],
        'Growth Book': ['bi bi-book-half', ['Previous', 'To-dos']]
        }


menu = list(main_menu.keys())
routes = [x[:4].lower() for x in menu]
dict_routes = dict(zip(routes, menu))
icons = [x[0] for x in list(main_menu.values())]
nav_menu = list(zip(menu, icons))

###############             ROUTING                ##########################

@app.route("/<page>")
def home(page):
    if page in dict_routes.keys():
        title = dict_routes[page]
        try:
            nav_item = main_menu[title][1]
        except IndexError:
            nav_item = None
        return render_template('content.html', 
                title = title,
                nav_bar = nav_menu,
                nav_item = nav_item,
                content_type = page)
    return "unknown"


##############               MAIN MENU              #########################

if __name__ == "__main__":
    app.run(debug=True)
    # ui.run() # For UI Application/deployment


################        USED ONLY IN PRODUCTION    ##########################
# import jinja2
# jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
# template = jinja_env.get_template('/content.html')

# jinja_var = {
#         'nav_bar': ['X', 'Y', 'Z']
#         }

# print(template.render(jinja_var))

# ui = FlaskUI(app, width=500, height=500) # For UI Application/deployment

