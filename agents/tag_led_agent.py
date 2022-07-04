from classes import TagBaseAgent
from utils import is_vision_enabled
import numpy as np
from time import sleep
import cv2
from PIL import Image

COLOR_RED= "RED"
COLOR_YELLOW = "YELLOW"

class TagLedAgent(TagBaseAgent):
    def __init__(self, it, remote_ip) -> None:
        print("initialising the TagAgent")
        super().__init__(it, remote_ip)

        self.iter = 0
        self.robot_counter = 0

    def hide(self) -> None:
        print("TA   : ITERATIION", self.iter)
        if self.robot_counter > 0:
            self.robot_counter -= 1
            return
        robot_led_detected, center_x, center_y, area = self.detect_robot_led(COLOR_YELLOW)
        if(robot_led_detected):
            print("Chaser detected, Performing hide action")
            self.turn_away_from_robot(center_x)
            self.robot_counter = 6
        else:
            print("Hider: Performing move around")
            self.move_around_action()
        print("TA   : END ITERATION", self.iter)
        self.iter += 1


    def chase(self) -> None:
        print("TA   : ITERATIION", self.iter)
        if self.robot_counter > 0:
            self.robot_counter -= 1
            return
        robot_led_detected, center_x, center_y, area = self.detect_robot_led(COLOR_RED)
        if(robot_led_detected):
            print("Hider detected, Performing chase action")
            self.robot_counter = 6
            driveLeft, driveRight = self._offset_to_speeds(center_x)
            self.yeti.SetLeftRightIndefinite(driveLeft, driveRight)
        else:
            print("Chaser: Performing move around")
            self.move_around_action()
        print("TA   : END ITERATION", self.iter)
        self.iter += 1

    def detect_robot_led(self, color):
        if self.image is not None:
            mask = self.segment_colour(self.image, color)
            loct, area = self.find_blob(mask)
            x_cord, y_cord, width, height = loct
            if(width*height) > 10:
                centre_x = x_cord+((width)/2)
                centre_y = y_cord+((height)/2)
                print(centre_x, centre_y)
                if is_vision_enabled:
                    c=cv2.circle(self.image,(int(centre_x),int(centre_y)),3,(0,110,255),-1)
                    c_im=Image.fromarray(c)
                    self.show_image(c_im)

                # centre_x -= 60     #to be tuned
                # centre_y = 6-centre_y
                centre_x = centre_x / width
                print("centre_x after proportion", centre_x)
                return True, centre_x, centre_y, area  
            else:
                return False, 0, 0, 0
    
    #Image analysis work
    def segment_colour(self, frame, color):    #returns only the one color in the frame
        color_range_hsv = []
        color_range_ycrcb = []
        if(color==COLOR_RED):
            color_range_hsv.append(np.array([160, 160, 10]))
            color_range_hsv.append(np.array([190, 200, 200]))
            color_range_ycrcb.append(np.array((0., 185., 0.)))
            color_range_ycrcb.append(np.array((255., 200., 255.)))
        else:
            color_range_hsv = [np.array([25, 50, 70]), np.array([35, 255, 255])]
            color_range_ycrcb = [np.array((20, 142, 20)), np.array((255, 163, 90))]

        hsv_roi =  cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask_1 = cv2.inRange(hsv_roi, color_range_hsv[0], color_range_hsv[1])
        ycr_roi=cv2.cvtColor(frame,cv2.COLOR_BGR2YCrCb)
        mask_2=cv2.inRange(ycr_roi, color_range_ycrcb[0], color_range_ycrcb[1])

        mask = mask_1 | mask_2
        kern_dilate = np.ones((8,8),np.uint8)
        kern_erode  = np.ones((3,3),np.uint8)
        mask= cv2.erode(mask,kern_erode)      #Eroding
        mask=cv2.dilate(mask,kern_dilate)     #Dilating
        #cv2.imshow('mask',mask)
        return mask

    #returns the red colored circle
    def find_blob(self, blob): 
        largest_contour=0
        cont_index=0
        contours, _ = cv2.findContours(blob, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
        
        for idx, contour in enumerate(contours):
            area=cv2.contourArea(contour)
            if (area >largest_contour) :
                largest_contour=area
            
                cont_index=idx
                #if res>15 and res<18:
                #    cont_index=idx
                                
        r=(0,0,2,2)
        if len(contours) > 0:
            r = cv2.boundingRect(contours[cont_index])
        
        return r,largest_contour

    def move_around_action(self) -> None:
        print("no robot detected")
        distance = self.sonar_distance
        print("wall distance: ", distance)
        if distance < 30:
            print("facing a wall/obstacle")
            self.yeti.StopMotors()
            sleep(0.2)
            self.yeti._PerformMove(-1, -1, 1)
            sleep(0.1)
            offset = np.random.choice([-0.5, -0.3, 0.3, 0.5])
            driveLeft, driveRight = self._offset_to_speeds(offset, curvature=0.75)
            self.yeti.SetLeftRightIndefinite(driveLeft, driveRight)
        else:
            print("moving around")
            random_direction = np.random.choice([-0.5, -0.3, 0.3, 0.5])
            driveLeft, driveRight = self._offset_to_speeds(random_direction, curvature=0.75)
            self.yeti.SetLeftRightIndefinite(driveLeft, driveRight)

    def _offset_to_speeds(self, width_frac_offset, curvature=0.25):
        magnitude = abs(width_frac_offset)
        fast_side_speed = 1
        # curvature of 1 results in spinning about the axis when magnitude is 0.5
        slow_side_speed = fast_side_speed - abs(4 * curvature) * magnitude
        if width_frac_offset < 0:
            # Turn to the left
            driveLeft = slow_side_speed
            driveRight = fast_side_speed
        else:
            driveLeft = fast_side_speed
            driveRight = slow_side_speed
        return driveLeft, driveRight

    def turn_away_from_robot(self, x_off = 0) -> None:
        # If the robot is at the edge of the FOV, x_off=0.5, and this should
        # correspond to about 30 degrees
        robot_angle_approximation = abs(60 * x_off)
        print("TA   : robot angle approximation:", robot_angle_approximation)
        # If the robot is to the right (positive x_off), should turn left: negative angle
        angle = -1 * np.sign(x_off) * (180 - robot_angle_approximation)
        print("TA   : making angle", angle)
        self.yeti.PerformSpin(angle)
        offset = np.random.choice([-0.5, -0.3, 0.3, 0.5])
        driveLeft, driveRight = self._offset_to_speeds(offset, curvature=0.0)
        self.yeti.SetLeftRightIndefinite(driveLeft, driveRight)