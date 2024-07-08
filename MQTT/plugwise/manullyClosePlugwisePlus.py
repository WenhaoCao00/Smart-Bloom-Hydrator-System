from plugwise.api import *

DEFAULT_PORT = "/dev/ttyUSB0"
mac = "000D6F0005690BAB"   #circle+ 
stick = Stick(DEFAULT_PORT)
circle = Circle(mac, stick)
circle.switch_off() 