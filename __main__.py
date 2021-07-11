import os
from core import Core
from threading import Event

def main():
    c = Core()
    c.start()

if __name__ == '__main__':
    main()
    Event().wait()