from flask import Flask, render_template, jsonify, send_file
import requests
from datetime import datetime
from scipy.stats import norm
import statistics
import os
import io
import base64
import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

# date -> YYYY-MM-DD
@app.get('/api/weather-prediction/<date>/<time>/<lat>/<long>')
def weather_prediction(date, time, lat, long):
    url = f"https://api.meteomatics.com/{date}T00:00:00Z--{date}T23:59:59Z:PT30M/t_2m:C,wind_speed_10m:ms,precip_24h:mm/{lat},{long}/json"
    
    data = requests.get(url=url, auth=(os.getenv("METEOMATICS_USERNAME"), os.getenv("METEOMATICS_PASSWORD"))).json()

    # Reformat data
    organized = {}
    for parameter in data["data"]:
        param_name = parameter["parameter"]
        coord = parameter["coordinates"][0]
        values = [entry["value"] for entry in coord["dates"]]
        organized[param_name] = values
    


    #calculate mean, standard deviation, convert x value to z value
    mean_temperature = sum(organized['t_2m:C'])/len(organized['t_2m:C'])
    standard_deviation_temperature = statistics.stdev(organized['t_2m:C'])
    x_hot = 18
    x_cold = 7
    z_temp_hot = (x_hot-mean_temperature)/(standard_deviation_temperature)
    z_temp_cold = (x_cold-mean_temperature)/(standard_deviation_temperature)
    area_hot_temp = 1- norm.cdf(z_temp_hot)
    area_cold_temp = norm.cdf(z_temp_cold)
    probability_very_hot = round(area_hot_temp * 100, 2)
    probability_very_cold = round(area_cold_temp * 100, 2)

    mean_windspeed = sum(organized["wind_speed_10m:ms"])/len(organized["wind_speed_10m:ms"])
    standard_deviation_windspeed = statistics.stdev(organized["wind_speed_10m:ms"])
    x_windspeed = 7
    z_windspeed = (x_windspeed-mean_windspeed)/(standard_deviation_windspeed)
    area_windspeed = 1 - norm.cdf(z_windspeed)
    probability_very_windy = round(area_windspeed * 100, 2)

    mean_wet = sum(organized["precip_24h:mm"])/len(organized["precip_24h:mm"])
    standard_deviation_wet = statistics.stdev(organized["precip_24h:mm"])
    x_wet = 10
    try:
        z_wet = (x_wet-mean_wet)/(standard_deviation_wet)
        area_wet = 1-norm.cdf(z_wet)
        probability_very_wet = round(area_wet * 100, 2)

    except ZeroDivisionError:
        probability_very_wet = 0

    risk_score = round((probability_very_hot + probability_very_cold + probability_very_windy + probability_very_wet)/4, 2)
    comfort_score = 100 - risk_score

    return jsonify({'data': {'very_hot': str(probability_very_hot)+"%", 'very_cold': str(probability_very_cold)+"%", 'very_windy': str(probability_very_windy)+"%", 'very_wet': str(probability_very_wet)+"%",
                             'risk_score': str(risk_score)+"%", 'comfort_score': str(comfort_score) + "%"}}), 200


def simplify_list(data):
    try:
        values = data["data"][0]["coordinates"][0]["dates"]
        simplified = []
        for v in values:
            # Extract just the time
            dt = datetime.fromisoformat(v["date"].replace("Z", "+00:00"))
            time_str = dt.strftime("%H:%M:%S")
            simplified.append({
                "time": time_str,
                "value": round(v["value"], 2) 
            })
    except (KeyError, IndexError, ValueError):
        simplified = []
    return simplified

#Get Temp, windspeed, humidity, rainfall and atmospheric pressure for given date time
@app.get('/api/current-data/<date>/<time>/<lat>/<long>')
def get_current_data(date, time, lat, long):
    url = f'https://api.meteomatics.com/{date}T{time}:00Z/t_2m:C,wind_speed_10m:ms,precip_24h:mm,msl_pressure:hPa,absolute_humidity_2m:gm3/{lat},{long}/json'
    json_data = requests.get(url=url, auth=(os.getenv("METEOMATICS_USERNAME"), os.getenv("METEOMATICS_PASSWORD"))).json()
    simplify_list = {}
    for data in json_data['data']:
        name=data['parameter']
        value = data['coordinates'][0]['dates'][0]['value']
        simplify_list[name] = value
    return simplify_list


@app.get('/api/rainfall_chart/<date>/<lat>/<long>')
def rainfall_graph(date, lat, long):
    url = f"https://api.meteomatics.com/{date}T00:00:00Z--{date}T23:59:59Z:PT30M/precip_24h:mm/{lat},{long}/json"
    data = requests.get(url=url, auth=(os.getenv("METEOMATICS_USERNAME"), os.getenv("METEOMATICS_PASSWORD"))).json()
    simplified = simplify_list(data)
    x = []
    y = []
    for data in simplified:
        x.append(data['time'])
        y.append(data['value'])
    print(x)
    print(y)
    plt.figure()
    plt.plot(x, y)
    plt.xlabel("Time")
    plt.ylabel("Rainfall (mm)")
    # Save it to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()

    # Encode image to base64
    img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return jsonify({"image": img_base64})


@app.get('/api/sunshine-data/<date>/<lat>/<long>')
def sunshine_graph(date, lat, long):
    url = f"https://api.meteomatics.com/{date}T00:00:00Z--{date}T23:59:59Z:PT1H/sunshine_duration_1h:h/{lat},{long}/json"
    data = requests.get(url=url, auth=(os.getenv("METEOMATICS_USERNAME"), os.getenv("METEOMATICS_PASSWORD"))).json()
    simplified = simplify_list(data)
    return jsonify(simplified)

@app.get('/api/temp-data/<date>/<lat>/<long>')
def temp_graph(date, lat, long):
    url = f"https://api.meteomatics.com/{date}T00:00:00Z--{date}T23:59:59Z:PT30M/t_2m:C/{lat},{long}/json"
    data = requests.get(url=url, auth=(os.getenv("METEOMATICS_USERNAME"), os.getenv("METEOMATICS_PASSWORD"))).json()
    simplified = simplify_list(data)
    return jsonify(simplified)

@app.get('/api/wind-data/<date>/<lat>/<long>')
def wind_graph(date, lat, long):
    url = f"https://api.meteomatics.com/{date}T00:00:00Z--{date}T23:59:59Z:PT30M/wind_speed_10m:ms/{lat},{long}/json"
    data = requests.get(url=url, auth=(os.getenv("METEOMATICS_USERNAME"), os.getenv("METEOMATICS_PASSWORD"))).json()
    simplified = simplify_list(data)
    return jsonify(simplified)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
