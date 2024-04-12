import flask, random, time, logging, os
from flask import request, jsonify
from mqttClient import MQTTClient

# broker = 'cluster01.ad.bmalberta.com'
# port = 1883
# topic = "weather/"
broker = os.environ['BROKER_HOST']
port = os.environ['BROKER_PORT']
topic = os.environ['MESSAGE_TOPIC']

app = flask.Flask(__name__)
app.config["DEBUG"] = False
   

def run():
    global client
    client = MQTTClient(broker, port, topic)
    from waitress import serve
    serve(app, host="0.0.0.0", port=4000)
    # app.run(host="0.0.0.0", port=4000)

@app.route('/data/report', methods=['GET'])
def processsWeatherData():
    publishWeatherStats(request.args)
    return "Success", 201


def publishWeatherStats(data):
    
    # Outdoor
    client.publish('outdoorTemp', data.get('tempf'))
    client.publish('outdoorHumidity', data.get('humidity'));
    client.publish('outdoorBaromasbin', data.get('baromasbsin'));
    client.publish('outdoorBaromrelin', data.get('baraomrelin'));

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
    