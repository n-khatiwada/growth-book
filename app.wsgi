import sys
sys.path.insert(0, '/srv/http/Xnk')

activate_this = '/home/nkhatiwada/.local/share/virtualenvs/Xnk-xEdMNavr/bin/activate_this.py'

with open(activate_this) as file_:
	exec(file_.read(), dict(__file__=activate_this))

from app import app as application
