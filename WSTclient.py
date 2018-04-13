"""
Author:         William Trelawny
Date:           4/10/18
Last Updated:   4/13/18
Name:           LaundryDetector
"""

"""
Import libraries
"""

import time
import datetime as dt
import logging
from pytz import timezone, utc
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import RPi.GPIO as GPIO
from functools import partial

# Create logger object:
log = logging.getLogger(__name__)

"""
Configure logging:
"""

def custom_logger():
    # Setup global logger params:
    logging.basicConfig(
        filename='/opt/omni/var/log/LaundryDetector.log',
        level=logging.DEBUG,
        format='%(asctime)s : %(levelname)s : %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.Formatter.converter = time.gmtime
    # Start program execution:
    log.debug('Launching program...')
    return log 

"""
Function definitions:
"""


def setup(log):
    log.debug('Running setup script...')
    min_start_delta = 5               
    min_stop_delta = 5                   
    topic = "me/home/laundry"           # AWS IoT topic to publish to:
    pin = 14
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # Detect both Rising/Falling edge (GPIO LOW to HIGH and vice versa).
    # Callback is on its own thread, will trigger regardless what else is going on in program.
    # Bouncetime prevents quick multiple edge detections.
    log.debug('Adding edge detection on GPIO pin...')                          
    GPIO.add_event_detect(pin, GPIO.BOTH, callback=partial(machine_state_change, topic, min_start_delta, min_stop_delta), bouncetime=(min_start_delta * 5000))
    log.debug('Sensor initialized. Ready for input...')                                               


def machine_state_change(log, topic, min_start_delta, min_stop_delta, pin):
    if not GPIO.input(pin):             # if GPIO is LOW (button PRESSED/DOWN) at time of edge detection
        machine_starting(log, topic, min_start_delta, min_stop_delta, pin)
    else:
        machine_stopping(log, topic, min_start_delta, min_stop_delta, pin)

        
def machine_starting(topic, min_start_delta, min_stop_delta, pin, log):
    log.debug('Button is pressed.')
    min_start_delta = dt.timedelta(seconds = 5)           # Min vibration time to declare washer has started
    min_stop_delta = dt.timedelta(seconds = 5)            # Min vibration time to declare washer has finished
    t1 = dt.datetime.now()                                # Set temp var 't1' as time vibration started.
    t2 = t1 + min_start_delta  
    while (t1 <= t2) and not GPIO.input(pin):
        t1 = dt.datetime.now()
        pass
    else:                                                              # Do nothing until 't1' is greater than min start vibration time
        if not GPIO.input(pin):
            log.info('Machine has started.')     # AND GPIO is still reading LOW (still vibrating),
            # msg = _________                                              # then print message and publish to AWS.
            # aws_publish(topic, msg)
        else:
            log.info('False start alarm...')


def machine_stopping(topic, min_start_delta, min_stop_delta, pin, log):
    log.debug('Button is not pressed.')
    min_start_delta = dt.timedelta(seconds = 5)           # Min vibration time to declare washer has started
    min_stop_delta = dt.timedelta(seconds = 5)            # Min vibration time to declare washer has finished
    t1 = dt.datetime.now()
    t2 = t1 + min_stop_delta
    while (t1 <= t2) and GPIO.input(pin):
        t1 = dt.datetime.now()
        pass
    else:
        if GPIO.input(pin):
            log.info('Machine has stopped.')
            # msg = __________________
            # aws_publish(topic, msg)
        else:
            log.info('False stop alarm...')


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
def custom_puback_callback(mid, topic):
    print("Received PUBACK packet id {} on Topic {}".format(mid, topic))


# Main program loop
def main(log):
    custom_logger()                                        
    setup(log)
    try:
        # Loop forever
        while True:
            continue
    except:
        # Keyboard Interrupt, clear GPIO states
        log.debug('Exiting, clearing GPIO states...')
        GPIO.cleanup()

# start the program execution:
main(log)
