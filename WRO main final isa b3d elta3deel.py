# WRO- future engineers - By: The pythons 2 - Wed Jul 20 2022

import sensor, image, time, pyb
from pyb import UART
ledblue = pyb.LED(3)
ledred = pyb.LED(1)
ledgreen = pyb.LED(2)
threshold1 = [(35, 59, -63, -22, 5, 41)] #green threshold
threshold2 = [(28, 46, 21, 67, 0, 47)] #red threshold
thresholds_W = [(0, 8, -10, 9, -8, 11)] #wall threshold
thresholds_L=[(53, 78, 1, 29, 14, 66)]#orange line threshold
thresholds2_L = [(24, 52, -1, 91, -53, -17)]#blue line threshold
ROIl = [ (130,30,30,70, 0.7)]#left roi of wall
ROIR = [(0,30,30,70, 0.7)] #right roi of wall
ROI_L = [ (0,100,160,20, 0.7)] # blue orange line roi 20,150,320,70
middle_wall =[(20,40,120,35,0.7)] #middl wall roi
EXPOSURE_TIME_SCALE =2
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
sensor.set_auto_exposure(False,15000)
sensor.skip_frames(time = 500)
#current_exposure_time_in_microsecond  = sensor.get_exposure_o,us()
clock = time.clock()
#sensor.set_auto_exposure(False,  exposure_us=int(current_exposure_time_in_microsecond * EXPOSURE_TIME_SCALE))
sensor.set_auto_exposure(False,15000)
uart = UART(1, 115200)
greenflag = False
flag_orange = False
c =1150
flag_blue = False
left_wallflag = False
right_wallflag = False
redflag = False
blue_wall = False
green_wall = False
red_wall = False
orange_wall = False
boflag = False
vip_flag = False
wallline_flag = False
wall_flag = False
orange_flag = False
blue_flag = False
while(True):

    clock.tick()
    img = sensor.snapshot()
    #img = img.gamma_corr(gamma = 0.3,contrast=18.0,brightness=0.05)
    #img.draw_rectangle(20,40,120,35,color=(0,0,255),thickness =2,fill=False)
    #img.draw_rectangle(0,100,160,20,color=(255,0,0),thickness =2,fill=False) #(200, 60, 120, 90, 0.7)
    #img.draw_rectangle(130,30,30,70,color=(255,0,0),thickness =2,fill=False) #(200, 60, 120, 90, 0.7)            # Note: OpenMV Cam runs about half as fast when connected
    #img.draw_rectangle(0,100,160,20,color=(0,255,0),thickness =2,fill=False) #(20, 180, 320, 40, 0.7)
    for m in middle_wall:
        greenblob = img.find_blobs(threshold1,pixel_threshld=500, area_threshold=400,merge=True)
        if greenblob:
                    #if greenblob[0].area() >= 5000:
                        #uart.write("B")
                        #print("area of blob to large going back")
                    img.draw_rectangle(greenblob[0].rect(),color=(0,255,0))
                    img.draw_cross(greenblob[0].cx(),greenblob[0].cy())
                    print("turn left")
                    uart.write("L")
                    time.sleep(0.1)
                    print("area of greenblob",greenblob[0].area())
                    greenflag = True
                    green_wall = True
                    ledgreen.on()

        else:
                    greenflag = False
                    green_wall = False
                   # print("no green")
                    ledgreen.off()
        redblob = img.find_blobs(threshold2,pixel_threshld=500, area_threshold=400,merge=True)

        if redblob :
                    redflag = True
                    img.draw_rectangle(redblob[0].rect(),color=(255,0,0))
                    img.draw_cross(redblob[0].cx(),redblob[0].cy())
                    print("turn right red")
                    uart.write("R")
                    ledblue.on()
                    ledred.on()
                    time.sleep(0.2)
                    print("area of redblob",redblob[0].area())
                    red_wall = True
        else:
                    red_wall = False
                    redflag = False
                   # print("no red")
                    ledred.off()
                    ledblue.off()

    if redflag or greenflag :
        wallline_flag = False
    else:
        wallline_flag = True

    for r in ROI_L:
        if c>=500:
            orange_wall = False
            blue_wall = False
        orange_lines = img.find_blobs(thresholds_L,roi=r[0:4], pixelthreshold=100, areathreshold=500)
        blue_lines = img.find_blobs(thresholds2_L, roi=r[0:4], pixelthreshold=100, areathreshold=500)
        if orange_lines  and c>=500:
             orange_wall = True
             c=0
             c+=1
             if wallline_flag:

                print("c=",c)
                print("orange line area = ",orange_lines[0].area())
                ledred.on()
                ledgreen.on()
                img.draw_rectangle(orange_lines[0].rect())
                img.draw_cross(orange_lines[0].cx(),orange_lines[0].cy())
                print("orange line found going right")
                uart.write("O")
                #time.sleep(0.1)
                wall_flag = False
        elif blue_lines  and c>=500:
            blue_wall = True
            c=0
            c+=1
            print("i saw blue")
            print("wall line flag = ", wallline_flag)
            print("c = ", c)
            if wallline_flag:
                img.draw_rectangle(blue_lines[0].rect())
                img.draw_cross(blue_lines[0].cx(),blue_lines[0].cy())
                ledblue.on()
                print("blue light found turning left")
                uart.write("B")
                #time.sleep(0.1)

                print("c=",c)
                flag_blue = True
                blue_wall = True
                wall_flag = False
        else:
                ledblue.off()
                ledred.off()
                ledgreen.off()
                wall_flag = True

    if wall_flag == True and wallline_flag == True :
        for l in ROIR:
                left_wall = img.find_blobs(thresholds_W,roi=l[0:4],pixelthreshold=800, areathreshold=450,merge=True)
                if left_wall:
                    maxleftwall = max(left_wall, key=lambda b:b.area())
                    if  maxleftwall.area()>500 and vip_flag == False:
                        area_leftwall = maxleftwall.area()
                        print("area left wall",area_leftwall)
                        img.draw_rectangle(maxleftwall.rect())
                        img.draw_cross(maxleftwall.cx(), maxleftwall.cy())
                        c+=1
                        print("c=",c)
                        left_wallflag = True
                    else:
                        left_wallflag = False
                        area_leftwall = 0

        for s in ROIl :
                right_wall = img.find_blobs(thresholds_W ,roi=s[0:4], pixelthreshold=500, areathreshold=450, merge=True)
                if right_wall:
                    maxrightwall = max(right_wall, key=lambda b:b.area())
                    if  maxrightwall.area()>500 and vip_flag == False:
                        area_rightwall = maxrightwall.area()
                        print("area right wall",area_rightwall)
                        img.draw_rectangle(maxrightwall.rect())
                        img.draw_cross(maxrightwall.cx(), maxrightwall.cy())
                        c+=1
                        print("c=",c)
                        right_wallflag = True
                    else:
                        right_wallflag = False
                        area_rightwall = 0
        if right_wallflag == False and left_wallflag == True:
                c+=1
                if 1100>area_leftwall >760:
                    uart.write("r")
                    print("right without right wall")
                elif area_leftwall >=1100:
                    uart.write("R")
                    print("hard right without right u turn")
                elif 750>=area_leftwall >680:
                    uart.write("F")
                    print("forward without right wall")

        elif right_wallflag == True and left_wallflag == False:
                c+=1
                if 900 > area_rightwall >=650:
                    uart.write("l")
                    print("left without left wall")
                elif area_rightwall >900:
                    uart.write("L")
                    print("hard left without left u turn")
                elif 650>area_rightwall >500:
                    uart.write("F")
                    print("forward without left wall")
        elif right_wallflag == True and left_wallflag == True:
                wall_diff = area_rightwall-area_leftwall
                c+=1
                if area_rightwall >=800 and area_leftwall >= 800:
                    if green_wall:
                        uart.write("b")
                        uart.write("R")
                        time.sleep(0.1)
                        uar.write("F")
                        print("all black infront of me green going left")
                    elif red_wall:
                        uart.write("b")
                        uart.write("L")
                        time.sleep(0.1)
                        uar.write("F")
                        print("all black infront of me red going left")
                    elif blue_wall:
                        uart.write("b")
                        uart.write("B")
                        print("all black infront of me going left")

                    elif orange_wall == True:
                        uart.write("b")
                        uart.write("O")
                        print("all black infront of me going right")

                else:
                    print("wall diff = ",wall_diff)
                    if wall_diff >=700:
                            uart.write("L")
                            print("hard left turn 2 walls present")
                    elif wall_diff <= -500:
                            uart.write("R")
                            print("hard right turn 2 walls present")
                    elif 700>wall_diff >50:
                            print("turn left wall")
                            uart.write("l")
                           # c+=1
                    elif -300>wall_diff > -500:
                            print("turn right wall")
                            uart.write("r")
                            #c+=1
                    elif -300<=wall_diff< 50:
                            print("forward wall")
                            uart.write("F")
                            #c+=1

        else:
             wall_diff =0
