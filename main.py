from open_dev.watchdog import CWatchDog
from miner.miner import Miner
from time import sleep
from config import MINER_IP, MINER_PORT, WATCHDOG_PID
from util.keyboard_input import Keyboard
from util.base_class import BaseClass
import logging

if __name__ == '__main__':
    WRITE_LOG_TO_FILE = False
    LOG_FORMAT = '%(name)s (%(levelname)s) %(asctime)s: %(message)s'
    LOG_LEVEL = logging.INFO
    logger = logging.getLogger('main')

    if WRITE_LOG_TO_FILE:
        logging.basicConfig(filename='watchdog.txt', filemode='w', format=LOG_FORMAT, level=LOG_LEVEL,
                            datefmt='%d/%m/%y %H:%M:%S')
    else:
        logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL, datefmt='%d/%m/%y %H:%M:%S')

    miner = Miner(MINER_IP, MINER_PORT)
    watchdog = CWatchDog(miner, WATCHDOG_PID)
    keyboard_input = Keyboard(watchdog)
    while BaseClass.working():
        sleep(1)