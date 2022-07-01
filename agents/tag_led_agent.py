from classes import TagBaseAgent
from utils import is_vision_enabled
import numpy as np

import cv2

class TagLedAgent(TagBaseAgent):
    def __init__(self, it, remote_ip) -> None:
        super().__init__(it, remote_ip)

    def hide(self) -> None:
        return super().hide()

    def chase(self) -> None:
        return super().chase()

    def detect_robot_led(self) -> None:
        return