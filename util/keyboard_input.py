import threading
import logging
from util.logger_super import LoggerSuper


class Keyboard(LoggerSuper):
    """
    Класс реализует поток чтение и обработку команд из консоли
    """
    logger = logging.getLogger('Keyboard')

    def __init__(self, wd):
        # Start keyboart queue thread
        self.wd = wd

        self.inputThread = threading.Thread(target=self.read_kbd_input, args=(), daemon=True)
        self.inputThread.start()
        self.logger.info('start keyboard thread')


    # Function of input in thread
    def read_kbd_input(self):
        while True:
            # Receive keyboard input from user.
            try:
                input_str = input()
                print('Enter command: ' + input_str)
                cmd_list = input_str.split(' ')
                if len(cmd_list) > 0:
                    if 'cards' in cmd_list:
                        self.wd.miner.print_cards_list()

            except:
                continue