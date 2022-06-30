
import time
import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

image = cv2.imread('t1.jpg')
image = cv2.flip(image,-1)
#Image analysis work
def segment_colour(frame):    #returns only the red colors in the frame
    hsv_roi =  cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask_1 = cv2.inRange(hsv_roi, np.array([160, 160,10]), np.array([190,255,255]))
    ycr_roi=cv2.cvtColor(frame,cv2.COLOR_BGR2YCrCb)
    mask_2=cv2.inRange(ycr_roi, np.array((0.,165.,0.)), np.array((255.,255.,255.)))

    mask = mask_1 | mask_2
    kern_dilate = np.ones((8,8),np.uint8)
    kern_erode  = np.ones((3,3),np.uint8)
    mask= cv2.erode(mask,kern_erode)      #Eroding
    mask=cv2.dilate(mask,kern_dilate)     #Dilating
    #cv2.imshow('mask',mask)
    return mask

def find_blob(blob): #returns the red colored circle
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

def target_hist(frame):
    hsv_img=cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
   
    hist=cv2.calcHist([hsv_img],[0],None,[50],[0,255])
    return hist


def target_chase(frame):
      #grab the raw NumPy array representing the image, then initialize the timestamp and occupied/unoccupied text
     
      global centre_x
      global centre_y
      centre_x=0.
      centre_y=0.
      hsv1 = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
      mask_red=segment_colour(frame)      #masking red the frame
      # plt.show(mask_red)
      im=Image.fromarray(mask_red)
      im.save("t3.tif")
      loct,area=find_blob(mask_red)
      print(str(area)+":area")
      x,y,w,h=loct
      print(x+y+w+h)
      if (w*h) < 10:
            found=0
      else:
            found=1
            simg2 = cv2.rectangle(frame, (x,y), (x+w,y+h), 255,2)
            centre_x=x+((w)/2)
            centre_y=y+((h)/2)
            c=cv2.circle(frame,(int(centre_x),int(centre_y)),3,(0,110,255),-1)
            c_im=Image.fromarray(c)
            c_im.save("t4.tif")
            centre_x-=80     #to be tuned
            centre_y=6--centre_y   
            print(centre_x,centre_y)
      
      initial=400   #tuning of variable required
      flag=0
            
      if(found==0):
            #if the ball is not found and the last time it sees ball in which direction, it will start to rotate in that direction
            if flag==0:
                  # rightturn()  update
                  time.sleep(0.05)
            else:
                  # leftturn()    update
                  time.sleep(0.05)
            # stop()
            time.sleep(0.0125)
     
      elif(found==1):
            if(area<initial):
                print('not close')
           #forward() update
            elif(area>=initial):
                  initial2=6700    #tuning of variable required
                  if(area<initial2):
                        
                              #it brings coordinates of ball to center of camera's imaginary axis.
                        if(centre_x<=-20 or centre_x>=20):
                              if(centre_x<0):
                                    flag=0
                                    # rightturn() update
                                    time.sleep(0.025)
                              elif(centre_x>0):
                                    flag=1
                                    # leftturn()  update
                                    time.sleep(0.025)
                        # forward() update
                        time.sleep(0.00003125)
                        # stop()  update
                        time.sleep(0.00625)


                  else:
                        
                        # move forward update
                        time.sleep(0.1)
                        # stop()
                        time.sleep(0.1)


target_chase(image)