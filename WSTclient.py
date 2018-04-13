"""
Author:         William Trelawny
Date:           4/10/18
Last Updated:
Name:           laundryDetector
"""


"""
Import libraries
"""

import time
import datetime as dt
# import logging
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import RPi.GPIO as GPIO
from functools import partial


"""
Function definitions:
"""

def setup():
    print('{} - Running setup script...'.format(time.strftime(timefmt, time.localtime())))
    min_start_delta = 5               
    min_stop_delta = 5                   
    topic = "me/home/laundry"           # AWS IoT topic to publish to:
    pin = 23
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # Detect both Rising/Falling edge (GPIO LOW to HIGH and vice versa).
    # Callback is on its own thread, will trigger regardless what else is going on in program.
    # Bouncetime prevents quick multiple edge detections.
    print('{} - Adding edge detection on GPIO pin {!s}...'.format(time.strftime(timefmt, time.localtime()), pin))                          # debug
    GPIO.add_event_detect(pin, GPIO.BOTH, callback=partial(machine_state_change, topic, min_start_delta, min_stop_delta), bouncetime=(min_start_delta * 1000))

def machine_state_change(topic, min_start_delta, min_stop_delta, pin):
    if not GPIO.input(pin):             # if GPIO is LOW (button PRESSED/DOWN) at time of edge detection
        machine_starting(topic, min_start_delta, min_stop_delta, pin)
    else:
        machine_stopping(topic, min_start_delta, min_stop_delta, pin)
            

def machine_starting(topic, min_start_delta, min_stop_delta, pin):
    print('{} - Button is pressed.'.format(time.strftime(timefmt, time.localtime())))
    min_start_delta = dt.timedelta(seconds = 5)           # Min vibration time to declare washer has started
    min_stop_delta = dt.timedelta(seconds = 5)            # Min vibration time to declare washer has finished
    t1 = dt.datetime.now()                                # Set temp var 't1' as time vibration started.
    t2 = t1 + min_start_delta  
    while (t1 <= t2) and not GPIO.input(pin):
        t1 = dt.datetime.now()
        pass
    else:                                                              # Do nothing until 't1' is greater than min start vibration time
        if not GPIO.input(pin):
            print('{} - Machine has started.'.format(time.strftime(timefmt, time.localtime())))     # AND GPIO is still reading LOW (still vibrating),
            # msg = _________                                              # then print message and publish to AWS.
            # aws_publish(topic, msg)
        else:
            print('{} - False start alarm...'.format(time.strftime(timefmt, time.localtime())))


def machine_stopping(topic, min_start_delta, min_stop_delta, pin):
    print('{} - Button is not pressed.'.format(time.strftime(timefmt, time.localtime())))
    min_start_delta = dt.timedelta(seconds = 5)           # Min vibration time to declare washer has started
    min_stop_delta = dt.timedelta(seconds = 5)            # Min vibration time to declare washer has finished
    t1 = dt.datetime.now()
    t2 = t1 + min_stop_delta
    while (t1 <= t2) and GPIO.input(pin):
        t1 = dt.datetime.now()
        pass
    else:
        if GPIO.input(pin):
            print('{} - Machine has stopped.'.format(time.strftime(timefmt, time.localtime())))
            # msg = __________________
            # aws_publish(topic, msg)
        else:
            print('{} - False stop alarm...'.format(time.strftime(timefmt, time.localtime())))


# Publish message to AWS IoT topic
def aws_publish(topic, payload):
    myMQTTClient = AWSIoTMQTTClient("laundryDetector")
    myMQTTClient.configureEndpoint("a2bgly5s92f7bm.iot.us-east-1.amazonaws.com", 8883)
    myMQTTClient.configureCredentials("/opt/omni/aws/certs/rootCA", "/opt/omni/aws/certs/cbb0d2f3f1-private.pem.key",
                                      "/opt/omni/aws/certs/cbb0d2f3f1-certificate.pem.crt")
    myMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
    myMQTTClient.connect()
    myMQTTClient.publishAsync(topic, payload, 1, ackCallback=custom_puback_callback)
    myMQTTClient.unsubscribe(topic)
    myMQTTClient.disconnect()
    setup()


# Custom PUBACK callback
def custom_puback_callback(mid, topic):
    print("\n" + "=" * 20)
    print("Received PUBACK packet id {} on Topic {}".format(mid, topic))
    print("=" * 20 + "\n")


# Main program loop
def main():
    print('{} - Launching program...'.format(time.strftime(timefmt, time.localtime())))                                                    # debug
    setup()
    try:
        # Loop forever
        print('{} - Sensor initialized. Ready for input...'.format(time.strftime(timefmt, time.localtime())))                                               # debug
        while True:
            continue
    except:
        # Keyboard Interrupt, clear GPIO states
        print('{} Exiting, clearing GPIO states...'.format(time.strftime(timefmt, time.localtime())))
        GPIO.cleanup()


"""
Initialize variables
"""

# # Configure AWS debug logging:
# logger = logging.getLogger("AWSIoTPythonSDK.core")
# logger.setLevel(logging.DEBUG)
# streamHandler = logging.StreamHandler()
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# streamHandler.setFormatter(formatter)
# logger.addHandler(streamHandler)

timefmt = "%Y-%m-%d %H:%M:%S"

# start the program execution:
main()
