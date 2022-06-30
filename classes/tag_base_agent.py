from concurrent.futures import thread
from typing import Tuple
from .base_agent import BaseAgent
from .grove_utlrasonic_ranger import GroveUltrasonicRanger
import threading
from time import sleep
from gpiozero import PWMLED, Button # PWMLED allows to set brightsness
from gpiozero.pins.pigpio import PiGPIOFactory
from utils import GPIOPins, is_yeti_07

class TagBaseAgent(BaseAgent):
    def __init__(self, it, remote_ip) -> None:
        """A base class for agents that play tag. Inherits BaseAgent.
        
        This class contains functions for the game mechanics. It tracks the
        role of the robot (whether is is 'it'), controls the LEDs, listens
        to button presses (tags), and contains the logic for handling these
        tag events."""
        super().__init__()

        # local
        self.red_light= PWMLED(GPIOPins.RED_LED) 
        self.yellow_light = PWMLED(GPIOPins.YELLOW_LED)
        self.sonar = GroveUltrasonicRanger(GPIOPins.ULTRASOUND_SENSOR)
        self.btn_left = Button(GPIOPins.SWITCH_LEFT)
        self.btn_right = Button(GPIOPins.SWITCH_RIGHT)

        # remote
        if remote_ip is not None:
            self.remoteBotFactory = PiGPIOFactory(host=remote_ip)
            self.remote_red_light = PWMLED(GPIOPins.RED_LED, pin_factory=self.remoteBotFactory)
            self.remote_yellow_light = PWMLED(GPIOPins.YELLOW_LED, pin_factory=self.remoteBotFactory)
            self.remote_btn_left = Button(GPIOPins.SWITCH_LEFT, pin_factory=self.remoteBotFactory) 
            self.remote_btn_right = Button(GPIOPins.SWITCH_RIGHT, pin_factory=self.remoteBotFactory)

        self.btn_left.when_pressed = self._perform_role_changes
        self.btn_right.when_pressed = self._perform_role_changes

        # Not sure exactly how to achieve this
        # To update 'it' status if there is a switch hit miss on one of the either robots
        # self.remote_btn_left.when_pressed = self._change_it
        # self.remote_btn_right.when_pressed = self._change_it

        self.it = it
        self.name = "Yeti07" if is_yeti_07() else "Yeti05" 
        print("TBA  : this robot is named: ", self.name)

        self.sleeping = False

        self.role_changed = False
        self.running = False
        self.led_change_detector = threading.Thread(target=self._detect_LED_change())

    @property
    def sonar_distance(self) -> float:
        """Returns the distance measured by the ultrasonic sensor in cm."""
        return self.sonar.get_distance()
    
    def _change_it(self) -> None:
        """Change the it state of the yeti to whatever it currently is not"""
        global role_changed
        self.yeti.StopMotors()
        self.it = not self.it
        print("TBA  : switching roles! This robot is now", "it" if self.it else "not it")
        self.role_changed = True
        if self.it: 
            print("TBA  : sleeping to give the hider some time")
            self.sleeping = True
            sleep(10)
            self.sleeping = False

    def _initialise_hide(self) -> None:
        """Sets the LEDs and calls 'self.hide' until tagged. Should run in a seperate thread."""
        print("TBA  : initialising hide")
        self.red_light.value = 1    
        self.yellow_light.value = 0 
        self.running = True
        self.led_change_detector.start()
        while not self.it:
            if self.image is not None:          
                self.hide()
            sleep(0.3)

    def _initialise_chase(self) -> None:
        """Sets the LEDs and calls 'self.chase' until tagged. Should run in a seperate thread."""
        print("TBA  : initialising chase")
        self.red_light.value = 0
        self.yellow_light.blink()
        self.running = True
        self.led_change_detector.start()
        while self.it:
            if not self.sleeping and self.image is not None: 
                self.chase()
            sleep(0.3)

    def _detect_LED_change(self) -> None:
        """Update it status when a remote LED update is detected"""
        while self.running:
            if not self.role_changed:
                if self.it and self.red_light.is_lit:
                    print("Updating it from remote update - red is on")
                    self._change_it()
                elif not self.it and self.yellow_light.is_lit:
                    print("Updating it from remote update - yellow is on")
                    self._change_it()

    def change_remote_led_on_button_press(self, red_led, yellow_led) -> None:
        """Update remote led on self button press"""
        print("Updated red to {red} and yellow to {yellow}".format(red=red_led, yellow=yellow_led))
        self.remote_red_light.value = red_led
        if yellow_led == 1:
            self.remote_yellow_light.blink()
        else:
            self.remote_yellow_light.value = 0

    def _perform_role_changes(self) -> None:
        """Update it and remote LED 'IF a switch press miss occurs during a tag'"""
        self._change_it()
        remote_red, remote_yellow = self._get_remote_led_status()
        if remote_red and not self.it:
            self.change_remote_led_on_button_press(0, 1)
        elif remote_yellow and self.it:
            self.change_remote_led_on_button_press(1, 0)

    def hide(self) -> None:
        """The logic for deciding where to move when not 'it'. To be overriden."""
        pass

    def chase(self) -> None:
        """The logic for deciding where to move when 'it'. To be overriden."""
        pass

    def _get_remote_led_status(self) -> Tuple[bool, bool]:
        """Returns the LED status on remote yetiborg"""
        return (self.remote_red_light.is_lit, self.remote_yellow_light.is_lit)

    def play(self, num_games=5):
        """Play tag 'num_games' amount of times.
        
        Whenever a robot is tagged, the roles reverse."""
        print("TBA  : playing tag. Starting as", "it" if self.it else "not it")
        self.processor.start()
        self.capture_thread.start()
        for i in range(num_games):
            print("TBA  : started game ", i+1)
            self.role_changed = False # reset role changed status before a new game
            if self.it:
                print("TBA  : starting chase thread")
                chase = threading.Thread(target=self._initialise_chase())
                chase.start()
            else:
                print("TBA  : started hide thread")
                hide = threading.Thread(target=self._initialise_hide())
                hide.start()
        print("TBA  : finished all games")
        self.running = False
        self.led_change_detector.join() # terminate the led change detector thread
