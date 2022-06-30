from . import ZeroBorg3 as ZeroBorg # Use python3 instead of 2
import time
import sys
from utils import is_yeti_07

class YetiBorg():
    """A wrapper of the ZeroBorg class.
    
    This class is used for performing movements with the YetiBorg robot.
    """
    def __init__(self) -> None:

        # Movement settings - WE NEED TO TUNE THESE
        self.timeForward1m = 2.3                       # Number of seconds needed to move about 1 meter
        self.timeSpin360   = 2.1                     # Number of seconds needed to make a full left / right spin

        # Power settings
        self.voltageIn = 8.4                         # Total battery voltage to the ZeroBorg (change to 9V if using a non-rechargeable battery)
        self.voltageOut = 6.0                        # Maximum motor voltage

        # Setup the power limits
        if self.voltageOut > self.voltageIn:
            self.maxPower = 1.0
        else:
            self.maxPower = self.voltageOut / float(self.voltageIn)

        # Setup the ZeroBorg
        self.ZB = ZeroBorg.ZeroBorg()
        #ZB.i2cAddress = 0x44                  # Uncomment and change the value if you have changed the board address
        self.ZB.Init()
        if not self.ZB.foundChip:
            boards = ZeroBorg.ScanForZeroBorg()
            if len(boards) == 0:
                print('No ZeroBorg found, check you are attached :)')
            else:
                print('No ZeroBorg at address %02X, but we did find boards:') % (self.ZB.i2cAddress)
                for board in boards:
                    print('    %02X (%d)') % (board, board)
                print('If you need to change the I�C address change the setup line so it is correct, e.g.')
                print('ZB.i2cAddress = 0x%02X') % (boards[0])
            sys.exit()
        #ZB.SetEpoIgnore(True)                 # Uncomment to disable EPO latch, needed if you do not have a switch / jumper
        self.ZB.SetCommsFailsafe(False)             # Disable the communications failsafe
        self.ZB.ResetEpo()

    def _PerformMove(self, driveLeft, driveRight, numSeconds):
        """Internal function to perform a general movement"""
        # Set the motors running
        if is_yeti_07():
            self.ZB.SetMotor1(-driveRight * self.maxPower) # Rear right
            self.ZB.SetMotor2(driveLeft  * self.maxPower)  # Front left
            self.ZB.SetMotor3(driveRight * self.maxPower)  # Front right
            self.ZB.SetMotor4(-driveLeft  * self.maxPower) # Rear left
        else:
            self.ZB.SetMotor1(-driveRight * self.maxPower) # Rear right
            self.ZB.SetMotor2(-driveRight * self.maxPower) # Front right
            self.ZB.SetMotor3(-driveLeft  * self.maxPower) # Front left
            self.ZB.SetMotor4(-driveLeft  * self.maxPower) # Rear left
        # Wait for the time
        time.sleep(numSeconds)
        # Turn the motors off
        self.ZB.MotorsOff()

    def SetLeftRightIndefinite(self, driveLeft, driveRight):
        if is_yeti_07():
            self.ZB.SetMotor1(-driveRight * self.maxPower) # Rear right
            self.ZB.SetMotor2(driveLeft  * self.maxPower)  # Front left
            self.ZB.SetMotor3(driveRight * self.maxPower)  # Front right
            self.ZB.SetMotor4(-driveLeft  * self.maxPower) # Rear left
        else:
            self.ZB.SetMotor1(-driveRight * self.maxPower) # Rear right
            self.ZB.SetMotor2(-driveRight * self.maxPower) # Front right
            self.ZB.SetMotor3(-driveLeft  * self.maxPower) # Front left
            self.ZB.SetMotor4(-driveLeft  * self.maxPower) # Rear left


    def PerformSpin(self, angle: float):
        """Spin an angle in degrees"""
        if angle < 0.0:     # left turn
            driveLeft  = -1.0
            driveRight = +1.0
        else:               # right turn
            driveLeft  = +1.0
            driveRight = -1.0
        numSeconds = abs((angle / 360.0) * self.timeSpin360) # Calculate the required time delay
        self._PerformMove(driveLeft, driveRight, numSeconds)

    def PerformDrive(self, meters: float):
        """Drive a distance in meters"""
        if meters < 0.0: # reverse
            driveLeft  = -1.0
            driveRight = -1.0
            meters *= -1
        else: # forward
            driveLeft  = +1.0
            driveRight = +1.0
        numSeconds = meters * self.timeForward1m # Calculate the required time delay
        self._PerformMove(driveLeft, driveRight, numSeconds)

    def StopMotors(self):
        self.ZB.MotorsOff()