# https://gpiozero.readthedocs.io/en/stable/remote_gpio.html
# Check link for possibilities of using GPIO inputs accross the network
# May turn out that yeti's can know about GPIO states of the other yeti, which can come in handy

class GPIOPins:
    # GPIO numbers corresponding to pins on raspberry Pi
    RED_LED = 26
    YELLOW_LED = 19

    SWITCH_LEFT = 16   # Probably change these names
    SWITCH_RIGHT = 23  # Probably change these names

    ULTRASOUND_SENSOR = 17            # US sensor