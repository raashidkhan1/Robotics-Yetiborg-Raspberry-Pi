vision_enabled = False

yeti_07 = False

def enable_vision():
    global vision_enabled
    vision_enabled = True

def is_vision_enabled() -> bool:
    """Whether to show plots/images from the robot on the client device."""
    return vision_enabled

def set_yeti_07():
    global yeti_07
    yeti_07 = True

def is_yeti_07() -> bool:
    return yeti_07
