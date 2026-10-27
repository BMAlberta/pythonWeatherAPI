import flask, random, time, logging, os, json
from flask import request, jsonify
from mqttClient import MQTTClient

# broker = 'cluster01.ad.bmalberta.com'
# port = 1883
# topic = "weather/"
# broker = os.environ['BROKER_HOST']
# port = os.environ['BROKER_PORT']
# topic = os.environ['MESSAGE_TOPIC']
def load_options():
    # HA add-on runtime config
    try:
        with open("/data/options.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback for local dev runs
        return {}

opts = load_options()

broker = opts.get("broker_host") or os.environ.get("BROKER_HOST", "core-mosquitto")
port = int(opts.get("broker_port") or os.environ.get("BROKER_PORT", 1883))
topic = opts.get("message_topic") or os.environ.get("MESSAGE_TOPIC", "weather")

mqtt_username = opts.get("mqtt_username")
mqtt_password = opts.get("mqtt_password")

listen_port = int(opts.get("listen_port") or os.environ.get("LISTEN_PORT", 4000))

app = flask.Flask(__name__)
app.config["DEBUG"] = False
   

def run():
    global client
    client = MQTTClient(broker, port, topic, mqtt_username, mqtt_password)
    from waitress import serve
    serve(app, host="0.0.0.0", port=listen_port)
    # app.run(host="0.0.0.0", port=4000)

@app.route('/data/report', methods=['GET'])
def processsWeatherData():
    publishWeatherStats(request.args)
    return "Success", 201

@app.get("/")
def health():
    return "OK", 200
    
def publishWeatherStats(data):
    
    # Outdoor
    client.publish('outdoorTemp', data.get('tempf'))
    client.publish('outdoorHumidity', data.get('humidity'));
    client.publish('outdoorBaromasbin', data.get('baromabsin'));
    client.publish('outdoorBaromrelin', data.get('baromrelin'));

    # Indoor
    client.publish('indoorTemp', data.get('tempinf'));
    client.publish('indoorHumidity', data.get('humidityin'));

    # Wind
    client.publish('winddir', data.get('winddir'));
    client.publish('windgustmph', data.get('windgustmph'));
    client.publish('windspeedmph', data.get('windspeedmph'));
    client.publish('windmaxdailygust', data.get('maxdailygust'));

    # Rain
    client.publish('hourlyrainin', data.get('hourlyrainin'));
    client.publish('eventrainin', data.get('eventrainin'));
    client.publish('dailyrainin', data.get('dailyrainin'));
    client.publish('weeklyrainin', data.get('weeklyrainin'));
    client.publish('monthlyrainin', data.get('monthlyrainin'));
    client.publish('totalrainin', data.get('totalrainin'));

    # Solar
    client.publish('solarradiation', data.get('solarradiation'));
    client.publish('uvindex', data.get('uv'));

if __name__ == '__main__':
    run()
    
