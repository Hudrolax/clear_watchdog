from datetime import datetime

class Card:
    def __init__(self, cvddc, mvddc, cclock, mclock, card_type=None):
        self.speed = 0
        self.crashes24h = 0
        self.crashes1m = 0
        self.cvddc = cvddc
        self.mvddc = mvddc
        self.cclock = cclock
        self.mclock = mclock
        self.set_cvddc = 0
        self.set_mvddc = 0
        self.set_cclock = 0
        self.set_mclock = 0
        self.type = card_type
        self.speed_above_0_time = datetime.now()

    def check_speed(self):
        if self.speed > 0:
            self.speed_above_0_time = datetime.now()

    def speed_zero_douring_5min(self):
        if (datetime.now() - self.speed_above_0_time).total_seconds() > 300:
            return True
        else:
            return False

    def time_speed_belov_zero_min(self):
        return  round((datetime.now() - self.speed_above_0_time).total_seconds()/60,1)



    def increase_voltage(self):
        if self.set_cvddc == 0 and (self.cvddc<=900 or self.cclock <= 1090):
            _cvoltage = self.cvddc+10
            if _cvoltage <= 1000:
                self.set_cvddc = _cvoltage
        if self.set_mvddc  == 0 and (self.mvddc <= 920 or self.mclock <= 1950):
            _mvoltage = self.mvddc + 10
            if _mvoltage <= 1000:
                self.set_mvddc = _mvoltage

    def decrease_clocks(self):
        if self.set_cclock == 0 and self.cvddc >= 900:
            _cclock = self.cclock - 5
            if _cclock >= 1080:
                self.set_cclock = _cclock
        if self.set_mclock == 0 and self.mvddc >= 920:
            _mclock = self.mclock - 5
            if _mclock >= 1940:
                self.set_mclock = _mclock

    @property
    def normal_speed(self):
        if self.type == None:
            return 8

        if self.type == 'RX 570' or self.type == 'RX 580' or self.type == 'RX 470' or self.type == 'RX 480':
            return 8
        if self.type == 'P104-100':
            return 35
        else:
            return 35

    def __str__(self):
        return f'speed={self.speed}:crashes={self.crashes24h} ({self.cvddc}/{self.mvddc})'