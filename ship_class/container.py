from abc import ABC, abstractmethod


TRANSMIT_POWER = 0


class Container(ABC):
    @abstractmethod
    def __init__(self, length, width, height, transmit_power=TRANSMIT_POWER):
        self.length = length
        self.width = width
        self.height = height
        self.transmit_power = transmit_power
        self.malicious = False
        self.jammer = False
        self.x = None
        self.y = None
        self.z = None


class Standard_Container(Container):
    def __init__(self, transmit_power=TRANSMIT_POWER):
        super().__init__(length=12, width=3, height=5, transmit_power=transmit_power)


class Small_Container(Container):
    def __init__(self, transmit_power=TRANSMIT_POWER):
        super().__init__(length=6, width=3, height=5, transmit_power=transmit_power)
