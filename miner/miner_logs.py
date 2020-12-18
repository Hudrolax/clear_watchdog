from datetime import datetime
from config import MINER_PATH, MINER_LOG_MASK
import os


class MinerLogs:
    @staticmethod
    def modification_date(filename):
        t = os.path.getmtime(filename)
        return datetime.fromtimestamp(t)

    @staticmethod
    def get_logs(seconds):
        dirs = os.listdir(MINER_PATH)
        file_list = []
        for file in dirs:
            if file.find(MINER_LOG_MASK) > -1 and (datetime.now()-MinerLogs.modification_date(MINER_PATH+file)).total_seconds() < seconds:
                file_list.append(MINER_PATH+file)
        return file_list

    @staticmethod
    def parse_logs(seconds):
        """
        :param seconds: рассматривать логи, измененные не раньше, чем seconds от текущей даты
        :return: список списков
        """
        logs = MinerLogs.get_logs(seconds)
        crashes = []
        types = []
        for log in logs:
            with open(log) as file:
                lines = file.readlines()
                for line in lines:
                    if line.find('not responding') > -1 or line.find('Incorrect ETH share from ') > -1:
                        pieces = line.split(' ')
                        for piece in pieces:
                            if piece.find('GPU') > -1:
                                gpu = int(piece.replace('GPU',''))
                        crashes.append(gpu)
                    elif line.find('Radeon') > -1 and line.find('RX') > -1 and line.find('GPU') > -1:
                        initial_line = line
                        pieces = line.split(' ')
                        for piece in pieces:
                            if piece.find('GPU') > -1:
                                gpu = piece.replace('GPU', '')
                                gpu = gpu.replace(':', '')
                                gpu = int(gpu)
                                model = 'RX'
                                if initial_line.find('570') > -1:
                                    model = 'RX 570'
                                elif initial_line.find('580') > -1:
                                    model = 'RX 580'
                                elif initial_line.find('470') > -1:
                                    model = 'RX 470'
                                elif initial_line.find('480') > -1:
                                    model = 'RX 480'
                                el = [gpu, model]
                                if not el in types:
                                    types.append(el)
        return [crashes, types]