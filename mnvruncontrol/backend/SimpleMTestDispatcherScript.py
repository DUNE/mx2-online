

import signal
import sys

import time
import os

def setup():
    signal.signal(signal.SIGTERM, quit)
    
    print("I got the following args:")
    for i, arg in enumerate(sys.argv):
        print("{0:>2}: {1}".format(i, arg))
    print("My process id: %s" % os.getpid())

def loop():
    i = 0
    print("Starting loop")
    while True:
        print("I've been running for %s seconds" % i)
        time.sleep(1)
        i += 1

def quit(signum, frame):
    print("quitting due to signum %s" % signum)
    # Frames can pretty much be ignored in most cases.
    # They're there if you want to know where your code was when it got the signal.
    # You might want to know so you can finish doing something important before quitting.
    # more info: http://stackoverflow.com/questions/18704862/python-frame-parameter-of-signal-handler
    sys.exit()

if __name__ == "__main__":
    setup()
    loop()
