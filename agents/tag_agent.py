from curses.ascii import TAB
from time import sleep, time
from tkinter import N
from turtle import distance
from classes import TagBaseAgent
from utils import is_vision_enabled
import numpy as np

import cv2


class TagAgent(TagBaseAgent):
    def __init__(self, it, remote_ip) -> None:
        """An implementation of an agent playing tag. Inherits TagBaseAgent.
        
        This class overrides the 'hide' and 'chase' methods of TagBaseAgent, and
        contains functions required for deciding how to control the motors."""
        print("\nTA   : initialising the TagAgent")
        super().__init__(it, remote_ip)

        self.iter = 0
        self.robot_counter = 0

    ##########################################################################
    ############################# CORE FUNCTIONS #############################
    ##########################################################################

    def hide(self) -> None:
        print("TA   : ITERATIION", self.iter)
        if self.robot_counter > 0:
            self.robot_counter -= 1
            return
        print("TA   : performing hide sequence")
        robot_detected, x_off, y_off, segmenting_data = self.detect_opponent()

        if not robot_detected:
            self.no_robot_detected_sequence(segmenting_data)
        else:
            print("TA   : ROBOT DETECTED!")
            self.turn_away_from_robot(x_off)
            self.robot_counter = 6
        print("TA   : END ITERATION", self.iter)
        self.iter += 1

    def chase(self) -> None:
        print("TA   : START ITERATION", self.iter)
        if self.robot_counter > 0:
            self.robot_counter -= 1
            return
        print("TA   : performing chase sequence")
        robot_detected, x_off, y_off, segmenting_data = self.detect_opponent()
        
        if not robot_detected:
            self.no_robot_detected_sequence(segmenting_data)
        else:
            print("TA   : ROBOT DETECTED!")
            self.robot_counter = 6
            driveLeft, driveRight = self._offset_to_speeds(x_off)
            self.yeti.SetLeftRightIndefinite(driveLeft, driveRight)
        print("TA   : END ITERATION", self.iter)
        self.iter += 1
        
    ##########################################################################
    ############################ ROBOT DETECTION #############################
    ##########################################################################

    def detect_opponent(self):
        print("TA   : starting segmentation process")
        image = self.image
        gray_image = cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)
        kernel=np.ones((3,3),np.uint8)
        gray_image=cv2.dilate(gray_image,kernel,iterations=1)

        knn_y, knn_x, segmenting_data = self._detect_robot_with_knn(gray_image)
        thres_y, thres_x = self._detect_robot_with_thresholding(gray_image)
        if thres_y is None:
            # Threshold detection did not find any dark pixels
            return False, None, None, segmenting_data
        height, width, _ = image.shape

        knn_y_off = (knn_y - 0.5 * height) / height
        knn_x_off = (knn_x - 0.5 * width) / width
        thres_y_off = (thres_y - 0.5 * height) / height
        thres_x_off = (thres_x - 0.5 * width) / width
        mean_x = int(np.mean([knn_x, thres_x]))
        mean_y = int(np.mean([knn_y, thres_y]))
        mean_y_off = (mean_y - 0.5 * height) / height
        mean_x_off = (mean_x - 0.5 * width) / width

        if is_vision_enabled():
            cv2.circle(image, (knn_x, knn_y), 10, (0, 0, 255), -1) # Red
            cv2.circle(image, (thres_x, thres_y), 10, (255, 0, 0), -1) # Blue
            cv2.circle(image, (mean_x, mean_y), 10, (0, 255, 0), -1) # Green
            self.show_image(image)
            self.show_image(image=segmenting_data[0], use_secondary=True)

        max_diff = 0.08 # Threshold of maximum difference
        if abs(knn_y_off - thres_y_off) > max_diff or \
                abs(knn_x_off - thres_x_off) > max_diff:
            return False, thres_x_off, thres_y_off, segmenting_data

        return True, mean_x_off, mean_y_off, segmenting_data

    def _detect_robot_with_knn(self, image):
        #twoDimage = image.flatten().T
        twoDimage=image.flatten().T
        twoDimage = np.float32(twoDimage)

        label, gray_centers = self._perform_knn(twoDimage)

        # round the rgb centers to integer values
        print("TA   : gray centers:", gray_centers)
        gray_centers = gray_centers.astype(np.uint8)
        robot_index = gray_centers.argmin()
        robot_value = gray_centers[robot_index]
        # Make labels either white or black
        res = gray_centers[label.flatten()]
        segmented_image = res.reshape((image.shape))

        robot_image = segmented_image == robot_value
        normalizer = robot_image.sum()
        y, x = np.argwhere(robot_image).sum(0) / normalizer

        return int(y), int(x), [segmented_image, gray_centers]

    def _detect_robot_with_thresholding(self, image):
        black_region = image < 25
        if not np.any(black_region): return None, None
        normalizer = black_region.sum()
        y, x = np.argwhere(black_region).sum(0) / normalizer
        return int(y), int(x)

    ##########################################################################
    ############################# WALL DETECTION #############################
    ##########################################################################

    def no_robot_detected_sequence(self, segmenting_data):
        print("TA   : no robot detected")
        distance = self.sonar_distance
        print("TA   : wall distance: ", distance)
        facing_wall, safest_off, wall_fraction = self.detect_walls(segmenting_data)
        if distance < 30:
            print("TA   : facing a wall")
            self.yeti.StopMotors()
            sleep(0.2)
            self.yeti._PerformMove(-1, -1, 1)
            sleep(0.1)
            offset = np.random.choice([-0.5, -0.3, 0.3, 0.5])
            driveLeft, driveRight = self._offset_to_speeds(offset, curvature=0.75)
            self.yeti.SetLeftRightIndefinite(driveLeft, driveRight)
        else:
            print("TA   : not facing a wall. Safe direction: ", safest_off)
            if safest_off is None:
                safest_off = np.random.choice([-0.5, -0.3, 0.3, 0.5])
            driveLeft, driveRight = self._offset_to_speeds(safest_off, curvature=0.75)
            self.yeti.SetLeftRightIndefinite(driveLeft, driveRight)

    def detect_walls(self, segmenting_data):
        segmented_image, gray_centers = segmenting_data
        height, width = segmented_image.shape
        
        indices_centers_sorted = np.argsort(gray_centers)
        min_wall_value = None
        for i, index_center in enumerate(reversed(indices_centers_sorted)):
            center_value = gray_centers[index_center]
            wall_image = segmented_image == center_value
            normalizer = wall_image.sum()
            y, x = np.argwhere(wall_image).sum(0) / normalizer
            if y > 0.5 * height: # lower half
                break
            min_wall_value = center_value
        # No colors dominant in upper half: probably something in the way
        if min_wall_value is None: return True, None, None
        wall_image = segmented_image >= min_wall_value
        
        bins = 5
        splits = np.array_split(wall_image, bins, axis=1)
        safest_bin, lowest_fraction = None, np.inf
        for i, split in enumerate(splits):
            wall_fraction = split.sum() / split.size
            print("split: ", i, "fraction: ", wall_fraction)
            if wall_fraction < lowest_fraction:
                safest_bin, lowest_fraction = i, wall_fraction

        if is_vision_enabled():
            image = (wall_image * 255).astype(np.uint8)
            self.show_image(segmented_image)

        if lowest_fraction > 0.5:
            return True, None, None

        bin_width = width / bins
        safest_bin_center_off = (((safest_bin * bin_width) + 0.5 * bin_width) - 0.5 * width) / width
        print("TA   : safe offset: ", safest_bin_center_off)
        return False, safest_bin_center_off, lowest_fraction

    ##########################################################################
    ########################### UTILITY FUNCTIONS ############################
    ##########################################################################

    def look_around(self, min_angle=-50, max_angle=50):
        angle = np.random.randint(min_angle, max_angle)
        self.yeti.PerformSpin(angle=angle)

    def turn_away_from_robot(self, x_off = 0):
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

    def _perform_knn(self, image):
        try:
            _, label, rgb_centers = cv2.kmeans(
                image,
                K=5,
                bestLabels=np.array([[160]*3, [120]*3, [60]*3, [25]*3]),
                criteria=(cv2.TERM_CRITERIA_MAX_ITER, 1, 1.0),
                attempts=2,
                flags=cv2.KMEANS_USE_INITIAL_LABELS)
        except:
            _, label, rgb_centers = cv2.kmeans(
                image,
                K=5,
                bestLabels=np.array([[160]*3, [120]*3, [60]*3, [25]*3]),
                criteria=(cv2.TERM_CRITERIA_MAX_ITER, 1, 1.0),
                attempts=2,
                flags=cv2.KMEANS_PP_CENTERS)

        return label, rgb_centers
        






    
