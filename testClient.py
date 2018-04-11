# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import datetime


# Suback callback
def custom_suback_callback(mid, data):
    print("\n" + "=" * 20)
    print("Received SUBACK packet id: {} for Topic {} with QoS {}.".format(mid, topic, data))
    print("=" * 20 + "\n")


# Puback callback
def custom_puback_callback(mid):
    print("\n" + "=" * 20)
    print("Received PUBACK packet id {} on Topic {}".format(mid, topic))
    print("=" * 20 + "\n")


# For certificate based connection
myMQTTClient = AWSIoTMQTTClient("laundryDetector")
myMQTTClient.configureEndpoint("a2bgly5s92f7bm.iot.us-east-1.amazonaws.com", 8883)
myMQTTClient.configureCredentials("/opt/omni/aws/certs/rootCA", "/opt/omni/aws/certs/cbb0d2f3f1-private.pem.key",
                                  "/opt/omni/aws/certs/cbb0d2f3f1-certificate.pem.crt")

myMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Configure connection & subscription
topic = "me/home/laundry"
payload = "Washer has started at {date:%H:%M:%S}".format(date=datetime.datetime.now())
myMQTTClient.connect()
myMQTTClient.subscribeAsync(topic, 1, ackCallback=custom_suback_callback)
myMQTTClient.publishAsync(topic, payload, 1, ackCallback=custom_puback_callback)
myMQTTClient.unsubscribe(topic)
myMQTTClient.disconnect()
