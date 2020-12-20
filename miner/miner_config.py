from config import MINER_PATH


class MinerConfig:
    def __init__(self):
        self.cclock = []
        self.mclock = []
        self.cvddc = []
        self.mvddc = []
        self.set_cclock = []
        self.set_mclock = []
        self.min_speed = 0

    @staticmethod
    def _str_list_to_int(lst):
        lst_int = []
        for el in lst:
            lst_int.append(int(el))
        return lst_int

    def _write_config_to_file(self, lines, path):
        with open(path, 'w') as file:
            file.writelines(lines)


    def update_config(self, cards):
        with open(MINER_PATH+'config.txt') as config:
            old_lines = config.readlines()

        new_lines = []
        for line in old_lines:
            if line.find('-cvddc') > -1:
                _new_line = '-cvddc '
                for card in enumerate(cards):
                    if card[1].set_cvddc != 0:
                        _new_line += f'{card[1].set_cvddc}'
                    else:
                        _new_line += f'{card[1].cvddc}'
                    if card[0] < len(cards)-1:
                        _new_line+= ','
                new_lines.append(_new_line+'\n')
            elif line.find('-mvddc') > -1:
                _new_line = '-mvddc '
                for card in enumerate(cards):
                    if card[1].set_mvddc != 0:
                        _new_line += f'{card[1].set_mvddc}'
                    else:
                        _new_line += f'{card[1].mvddc}'
                    if card[0] < len(cards) - 1:
                        _new_line += ','
                new_lines.append(_new_line+'\n')
            elif line.find('-cclock') > -1:
                _new_line = '-cclock '
                for card in enumerate(cards):
                    if card[1].set_cclock != 0:
                        _new_line += f'{card[0]+1}:{card[1].set_cclock}'
                    else:
                        _new_line += f'{card[0]+1}:{card[1].cclock}'
                    if card[0] < len(cards)-1:
                        _new_line += ','
                new_lines.append(_new_line+'\n')
            elif line.find('-mclock') > -1:
                _new_line = '-mclock '
                for card in enumerate(cards):
                    if card[1].set_mclock != 0:
                        _new_line += f'{card[0] + 1}:{card[1].set_mclock}'
                    else:
                        _new_line += f'{card[0] + 1}:{card[1].mclock}'
                    if card[0] < len(cards) - 1:
                        _new_line += ','
                new_lines.append(_new_line + '\n')
            # elif line.find('-minRigSpeed ') > -1:
            #     line = line.replace('\n', '')
            #     bites = line.split(' ')
            #     try:
            #         _min_speed = int(bites[1])
            #     except:
            #         _min_speed = 0
            #
            #     _min_speed_by_cards = -10
            #     for card in cards:
            #         _min_speed_by_cards += card.normal_speed
            #
            #     if _min_speed > _min_speed_by_cards:
            #         _new_line = f'-minRigSpeed {_min_speed_by_cards}\n'
            #     else:
            #         _new_line = f'-minRigSpeed {_min_speed}\n'
            #     new_lines.append(_new_line)
            else:
                new_lines.append(line)
        self._write_config_to_file(new_lines, MINER_PATH+'config.txt')

    def read_config(self):
        with open(MINER_PATH+'config.txt') as config:
            lines = config.readlines()
            for line in lines:
                line = line.replace('\n', '')
                if line.find('-cvddc ') > -1:
                    line = line.replace('-cvddc ', '')
                    self.cvddc  = MinerConfig._str_list_to_int(line.split(','))
                elif line.find('-mvddc ') > -1:
                    line = line.replace('-mvddc ', '')
                    self.mvddc  = MinerConfig._str_list_to_int(line.split(','))
                elif line.find('-minRigSpeed ') > -1:
                    line = line.replace('-minRigSpeed ', '')
                    self.min_speed = int(line)
                elif line.find('-cclock ') > -1:
                    line = line.replace('-cclock ', '')
                    pieces = line.split(',')
                    for piece in pieces:
                        constituents = piece.split(':')
                        self.cclock.append(constituents)
                elif line.find('-mclock ') > -1:
                    line = line.replace('-mclock ', '')
                    pieces = line.split(',')
                    for piece in pieces:
                        constituents = piece.split(':')
                        self.mclock.append(constituents)

if __name__ == '__main__':
    config = MinerConfig()
    config.read_config()
    config.update_config()