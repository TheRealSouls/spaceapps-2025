from flask import Flask, render_template, jsonify
import requests
from scipy.stats import norm, t
import statistics

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.get('/api/weather-prediction/<date>/<time>/<lat>/<long>')
def weather_prediction(date, time, lat, long):
    url = f"https://api.meteomatics.com/{date}T00:00:00Z--{date}T23:59:59Z:PT30M/t_2m:C,wind_speed_10m:ms/{lat},{long}/json"
    data = requests.get(url=url, auth=("malik_asher", "Gk3fQbD9p6FoCcAdUD0U")).json()

    # Reformat data
    organized = {}
    for parameter in data["data"]:
        param_name = parameter["parameter"]
        coord = parameter["coordinates"][0]
        values = [entry["value"] for entry in coord["dates"]]
        organized[param_name] = values
    print(organized)

    mean_temperature = sum(organized['t_2m:C'])/len(organized['t_2m:C'])
    mean_windspeed = sum(organized["wind_speed_10m:ms"])/len(organized["wind_speed_10m:ms"])

    standard_deviation_temperature = statistics.stdev(organized['t_2m:C'])
    standard_deviation_windspeed = statistics.stdev(organized["wind_speed_10m:ms"])

    print(f"Average temperature: {mean_temperature}")
    print(f"Average windspeed: {mean_windspeed}")

    print(f"Stdv Temperature: {standard_deviation_temperature}")
    print(f"Stdv windspeed: {standard_deviation_windspeed}")

    return 'test'

if __name__ == '__main__':
    app.run(debug=True)
