import threading
import logging
from util.logger_super import LoggerSuper
from util.base_class import BaseClass


class Keyboard(LoggerSuper):
    """
    Класс реализует поток чтение и обработку команд из консоли
    """
    logger = logging.getLogger('Keyboard')

    def __init__(self, wd):
        # Start keyboart queue thread
        self.wd = wd

        self.inputThread = threading.Thread(target=self.read_kbd_input, args=(), daemon=False)
        self.inputThread.start()
        self.logger.info('start keyboard thread')


    # Function of input in thread
    def read_kbd_input(self):
        while BaseClass.working():
            # Receive keyboard input from user.
            try:
                input_str = input()
                print('Enter command: ' + input_str)
                cmd_list = input_str.split(' ')
                if len(cmd_list) > 0:
                    if 'cards' in cmd_list:
                        self.wd.miner.print_cards_list()
                    elif 'crashes' in cmd_list:
                        self.wd.miner.print_crashes()

            except:
                continue