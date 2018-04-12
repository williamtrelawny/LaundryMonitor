"""
Author:         William Trelawny
Date:           4/10/18
Last Updated:
Name:           laundryDetector
"""


"""
Import libraries
"""
import sys
from time import sleep
import datetime
import logging
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import RPi.GPIO as GPIO


"""
Function definitions:
"""
def machine_state_change(pin):
    # AWS IoT topic to publish to:
    topic = "me/home/laundry"
    # Min vibration time to declare washer was running:
    min_delta = datetime.timedelta(seconds = 5)
    if not GPIO.input(pin):     # if GPIO is HIGH (button RELEASED/UP) at time of edge detection
        global time_started
        time_started = datetime.datetime.now()
        msg = "{} - Machine has started.".format(time_started)
        print(msg)
        # aws_publish(topic, msg)
    else:                       # if GPIO is LOW (button PRESSED/DOWN) at time of edge detection
        global time_stopped
        time_stopped = datetime.datetime.now()
        if time_stopped - time_started > min_delta:
            msg = "{} - Machine has stopped.".format(time_stopped)
            print(msg)
            # aws_publish(topic, msg)
        else:
            print('False alarm...')                   
        


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


# Custom PUBACK callback
def custom_puback_callback(mid):
    print("\n" + "=" * 20)
    print("Received PUBACK packet id {} on Topic {}".format(mid, topic))
    print("=" * 20 + "\n")

# Main program loop
def main():
    # init GPIO vars
    pin = 23
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # Detect both Rising/Falling edge (GPIO LOW to HIGH and vice versa).
    # Callback is on its own thread, will trigger regardless what else is going on in program.
    # Bouncetime prevents quick multiple edge detections.
    GPIO.add_event_detect(pin, GPIO.BOTH, callback=machine_state_change, bouncetime=300)
    try:
        # Loop forever
        while True:
            continue
    except:
        # Keyboard Interrupt, clear GPIO states
        print('Exiting, clearing GPIO states...')
        GPIO.cleanup()


"""
Initialize variables
"""

# Configure AWS debug logging:
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# start the program execution:
main()
