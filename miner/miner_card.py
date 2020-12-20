class Card:
    def __init__(self, cvddc, mvddc, cclock, mclock):
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
        self.type = None

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
            return 20

        if self.type == 'RX 570' or self.type == 'RX 580' or self.type == 'RX 470' or self.type == 'RX 480':
            return 20
        else:
            return 35

    def __str__(self):
        return f'speed={self.speed}:crashes={self.crashes24h} ({self.cvddc}/{self.mvddc})'