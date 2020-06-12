"""
*Before you run the code, do not forget to start the pigpiod daemon
*using "sudo pigpiod"
"""

#import the libraries used
import time
import RPi.GPIO as GPIO
import pigpio

#GPIO.setwarnings(False)

#create an instance of the pigpio library
pi=pigpio.pi()

#define the pin used by the Buzzer
#this pin will be used by the pigpio library
#which takes the pins in GPIO forms
#we will use GPIO18, which is pin 12
buzzer=18

#set the pin used by the buzzer as OUTPUT
pi.set_mode(buzzer, pigpio.OUTPUT)

GPIO.setmode(GPIO.BOARD)

#define the pin used by the Ultrasonic module
trig=10
echo=8

#define the pin used by the leds
redLed=36
yellowLed=38
greenLed=40



delay=0.005

#digits 1,2,3,4
selDigit=[23,29,31,33]

#A,B,C,D,E,F,G
display_list=[3,5,7,11,13,15,19]

#dot GPIO port
digitDP=21




#set the trigger pin as OUTPUT and the echo as INPUT
GPIO.setup(trig,GPIO.OUT)
GPIO.setup(echo,GPIO.IN)


GPIO.setup(redLed,GPIO.OUT)
GPIO.setup(yellowLed,GPIO.OUT)
GPIO.setup(greenLed,GPIO.OUT)

#GPIO.setwarnings(True)

for pin in display_list:
        GPIO.setup(pin,GPIO.OUT) # setting pins for segments
for pin in selDigit:
        GPIO.setup(pin,GPIO.OUT) # setting pins for digit selector
GPIO.setup(digitDP,GPIO.OUT) # setting dot pin

arrSeg = [[1,1,1,1,1,1,0],\
          [0,1,1,0,0,0,0],\
          [1,1,0,1,1,0,1],\
          [1,1,1,1,0,0,1],\
          [0,1,1,0,0,1,1],\
          [1,0,1,1,0,1,1],\
          [1,0,1,1,1,1,1],\
          [1,1,1,0,0,0,0],\
          [1,1,1,1,1,1,1],\
          [1,1,1,1,0,1,1]]


GPIO.output(digitDP,0)



def showDisplay(digit):
        for i in range(0, 4): #loop on 4 digits selectors (from 0 to 3 included)
                sel = [1,1,1,1]
                sel[i] = 0
                GPIO.output(selDigit, sel) # activates selected digit
                if digit[i].replace(".", "") == " ": # space disables digit
                        GPIO.output(display_list,0)
                        continue
                numDisplay = int(digit[i].replace(".", ""))
                GPIO.output(display_list, arrSeg[numDisplay]) # segments are activated according to digit mapping
                if digit[i].count(".") == 1 and i!=3:
                        GPIO.output(digitDP,1)
                else:
                        GPIO.output(digitDP,0)
                time.sleep(delay)

def splitToDisplay (toDisplay): # splits string to digits to display
        arrToDisplay=list(toDisplay)
        for i in range(len(arrToDisplay)):
                if arrToDisplay[i] == ".": arrToDisplay[(i-1)] = arrToDisplay[(i-1)] + arrToDisplay[i] # dots are concatenated to previous array element
        while "." in arrToDisplay: arrToDisplay.remove(".") # array items containing dot char alone are removed
        return arrToDisplay


def red_light():
        GPIO.output(redLed,GPIO.HIGH)
        GPIO.output(yellowLed,GPIO.LOW)
        GPIO.output(greenLed,GPIO.LOW)

def yellow_light():
        GPIO.output(redLed,GPIO.LOW)
        GPIO.output(yellowLed,GPIO.HIGH)
        GPIO.output(greenLed,GPIO.LOW)

def green_light():
        GPIO.output(redLed,GPIO.LOW)
        GPIO.output(yellowLed,GPIO.LOW)
        GPIO.output(greenLed,GPIO.HIGH)

def get_distance():
        #set the trigger to HIGH
        GPIO.output(trig, GPIO.HIGH)

        #sleep 0.00001 s and the set the trigger to LOW
        time.sleep(0.00001)
        GPIO.output(trig, GPIO.LOW)

        #save the start and stop times
        start = time.time()
        stop = time.time()

        #modify the start time to be the last time until
        #the echo becomes HIGH
        while GPIO.input(echo) == 0:
                start = time.time()

        #modify the stop time to be the last time until
        #the echo becomes LOW
        while  GPIO.input(echo) == 1:
	        stop = time.time()

        #get the duration of the echo pin as HIGH
        duration = stop - start

        #calculate the distance
        distance = 34300/2 * duration

        if distance < 0.5 and distance > 400:
                return 0
        else:
                #return the distance
                return distance

try:
    while True:
        distance=get_distance()
        print(distance)
        dist=str(distance)
        timeout=time.time()+0.5
        while True:
                showDisplay(splitToDisplay(dist))
                if distance <=10:
                        #turn on the buzzer at a frequency of 500Hz
                        #turn on the red led
                        pi.hardware_PWM(buzzer,500,10000)
                        red_light()
                elif  20>distance>10:
                        #turn off the buzzer
                        #turn on the yellow led
                        pi.hardware_PWM(buzzer,0,0)
                        yellow_light()

                elif distance>=20:
                        #turn off the buzzer
                        #turn on the green led
                        pi.hardware_PWM(buzzer,0,0)
                        green_light()

                if time.time()>timeout:
                        break
        #wait 100 ms before the next run
        time.sleep(0.1)

except KeyboardInterrupt:
    pass

#stop the PWM signal
pi.write(buzzer, 0)

#stop the connection with the daemon
pi.stop()

#clean all the used ports
GPIO.cleanup()
