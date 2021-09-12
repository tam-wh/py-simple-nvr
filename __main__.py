import os
from core import Core
from threading import Event
from flask import Flask, render_template
app = Flask(__name__)

core = None

@app.route('/')
def nvr_status():
    cams = core.config.Cameras
    try:
        return render_template("index.html", cams = cams, list_header = "XXX")
    except Exception as e:
        return(str(e))

def main():
    global core
    core = Core()

if __name__ == '__main__':
    main()
    app.run()