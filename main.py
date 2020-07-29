from watchdog import CWatchDog
from time import sleep

port = '/dev/ttyACM0'

if __name__ == '__main__':
    watchdog = CWatchDog(port)
    while True:
        sleep(1)