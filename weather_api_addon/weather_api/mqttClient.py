import random, time, logging
from paho.mqtt import client as mqtt_client

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

class MQTTClient:
    def __init__(self, broker, port, rootTopic, username=None, password=None):
        self.client_id = f'publish-{random.randint(0, 1000)}'
        self.broker = broker
        self.port = port
        self.rootTopic = rootTopic
        self.username = username
        self.password = password
        self.client = self.connect_mqtt(broker, self.client_id)
        self.client.on_disconnect = self.on_disconnect

    def connect_mqtt(self, broker, client_id):
        
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                client.connected_flag = True
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)
        client = mqtt_client.Client(client_id)
        client.connected_flag = False
        client.on_connect = on_connect
        # ✅ Add auth if provided (Mosquitto add-on requires it in your setup)
        if self.username:
            client.username_pw_set(self.username, self.password or "")
            
        client.loop_start()
        
        # ✅ Use broker + port (you were ignoring port before)
        client.connect(self.broker, self.port)

        # Wait until connected
        while not client.connected_flag:
            time.sleep(1)

        return client   

    def on_disconnect(self, client, userdata, rc):
        logging.info("Disconnected with result code: %s", rc)
        reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
        while reconnect_count < MAX_RECONNECT_COUNT:
            logging.info("Reconnecting in %d seconds...", reconnect_delay)
            time.sleep(reconnect_delay)

            try:
                client.reconnect()
                logging.info("Reconnected successfully!")
                return
            except Exception as err:
                logging.error("%s. Reconnect failed. Retrying...", err)

            reconnect_delay *= RECONNECT_RATE
            reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
            reconnect_count += 1
        logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)


    def publish(self, subTopic, message):
        # print("Publishing to topic " + self.rootTopic + subTopic)
        self.client.publish(self.rootTopic + subTopic, message)

    