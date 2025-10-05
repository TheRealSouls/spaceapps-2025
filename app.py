from flask import Flask, render_template, jsonify
import requests
from datetime import datetime
from scipy.stats import norm
import statistics
import os
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
    
    data = requests.get(url=url, auth=("malik_asher", "Gk3fQbD9p6FoCcAdUD0U")).json()

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
    x_hot = 20
    x_cold = 7
    z_temp_hot = (x_hot-mean_temperature)/(standard_deviation_temperature)
    z_temp_cold = (x_cold-mean_temperature)/(standard_deviation_temperature)
    area_hot_temp = 1- norm.cdf(z_temp_hot)
    area_cold_temp = norm.cdf(z_temp_cold)
    probability_very_hot = round(area_hot_temp * 100, 3)
    probability_very_cold = round(area_cold_temp * 100, 3)

    mean_windspeed = sum(organized["wind_speed_10m:ms"])/len(organized["wind_speed_10m:ms"])
    standard_deviation_windspeed = statistics.stdev(organized["wind_speed_10m:ms"])
    x_windspeed = 7
    z_windspeed = (x_windspeed-mean_windspeed)/(standard_deviation_windspeed)
    area_windspeed = 1 - norm.cdf(z_windspeed)
    probability_very_windy = round(area_windspeed * 100, 3)

    mean_wet = sum(organized["precip_24h:mm"])/len(organized["precip_24h:mm"])
    standard_deviation_wet = statistics.stdev(organized["precip_24h:mm"])
    x_wet = 10
    try:
        z_wet = (x_wet-mean_wet)/(standard_deviation_wet)
        area_wet = 1-norm.cdf(z_wet)
        probability_very_wet = round(area_wet * 100, 3)

    except ZeroDivisionError:
        probability_very_wet = 0

    return jsonify({'data': {'very_hot': str(probability_very_hot)+"%", 'very_cold': str(probability_very_cold)+"%", 'very_windy': str(probability_very_windy)+"%", 'very_wet': str(probability_very_wet)+"%"}}), 200


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

@app.get('/api/rainfall_chart/<date>/<lat>/<long>')
def rainfall_data(date, lat, long):
    url = f"https://api.meteomatics.com/{date}T00:00:00Z--{date}T23:59:59Z:PT30M/precip_24h:mm/{lat},{long}/json"
    data = requests.get(url=url, auth=(os.getenv("METEOMATICS_USERNAME"), os.getenv("METEOMATICS_PASSWORD"))).json()
    simplified = simplify_list(data)
    return jsonify(simplified)


@app.get('/api/sunshine-data/<date>/<lat>/<long>')
def sunshine_data(date, lat, long):
    url = f"https://api.meteomatics.com/{date}T00:00:00Z--{date}T23:59:59Z:PT1H/sunshine_duration_1h:h/{lat},{long}/json"
    data = requests.get(url=url, auth=(os.getenv("METEOMATICS_USERNAME"), os.getenv("METEOMATICS_PASSWORD"))).json()
    simplified = simplify_list(data)
    return jsonify(simplified)

@app.get('/api/temp-data/<date>/<lat>/<long>')
def temp_data(date, lat, long):
    url = f"https://api.meteomatics.com/{date}T00:00:00Z--{date}T23:59:59Z:PT30M/t_2m:C/{lat},{long}/json"
    data = requests.get(url=url, auth=(os.getenv("METEOMATICS_USERNAME"), os.getenv("METEOMATICS_PASSWORD"))).json()
    simplified = simplify_list(data)
    return jsonify(simplified)

@app.get('/api/wind-data/<date>/<lat>/<long>')
def wind_data(date, lat, long):
    url = f"https://api.meteomatics.com/{date}T00:00:00Z--{date}T23:59:59Z:PT30M/wind_speed_10m:ms/{lat},{long}/json"
    data = requests.get(url=url, auth=(os.getenv("METEOMATICS_USERNAME"), os.getenv("METEOMATICS_PASSWORD"))).json()
    simplified = simplify_list(data)
    return jsonify(simplified)


if __name__ == '__main__':
    app.run(debug=True)
