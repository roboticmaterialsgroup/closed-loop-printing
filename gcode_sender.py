from printrun.printcore import printcore
from printrun import gcoder
import time

class GcodeSender:
    """
    Class for establishing connection with printer
    """ 
    def __init__(self, port = '/dev/tty.usbmodem14201'):
        self.print_core = printcore(port, 115200)

    def disconnect(self):
        self.print_core.disconnect()

    # Read in a .gcode file and send command to printer line by line
    def send_gcode(self, gcode_path):
        gcode0 = [i.strip() for i in open(gcode_path)]
        gcode = gcoder.LightGCode(gcode0)

        while not self.print_core.online:
            time.sleep(0.1)

        self.print_core.startprint(gcode)
        while (self.print_core.printing == True) or (not self.print_core.priqueue.empty()):
            time.sleep(0.1)

