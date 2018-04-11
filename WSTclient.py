"""
Author:         William Trelawny
Date:           4/10/18
Last Updated:
Name:           laundryDetector
"""

# import libraries
import sys
import time
import datetime
import logging
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import RPi.GPIO as GPIO


"""
# Function definitions:
"""


def machine_state_change(pin):
    if GPIO.RISING:
        time_started = datetime.datetime.now()
        msg = "{} - Machine has started.".format(time_started)
        print(msg)
        # aws_publish(topic, msg)
        main()
    else:
        time_stopped = datetime.datetime.now()
        msg = "{} - Machine has stopped.".format(time_stopped)
        print(msg)
        # aws_publish(topic, msg)
        main()


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


def main():
    sensorPin = 23
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(sensorPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(sensorPin, GPIO.BOTH, callback=machine_state_change, bouncetime=3000)
    if not GPIO.event_detected(sensorPin):
        print('Waiting for button to be pressed...')
        time.sleep(3)

"""
Initialize variables:
"""
# AWS IoT vars:
topic = "me/home/laundry"

# Configure logging:
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# start the program execution:
main()
