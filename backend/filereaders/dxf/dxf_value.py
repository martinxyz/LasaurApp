
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'


class DXFValue:

    def __init__(self, value):
        self.value = value;

    def getDouble(self):
        return float(self.value)

    def getInt(self):
        return int(self.value)

    def getString(self):
        return self.value

    def __repr__(self):
        return self.value
