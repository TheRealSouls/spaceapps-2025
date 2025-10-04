from flask import Flask, render_template, jsonify
import requests
from scipy.stats import norm, t
from math import sqrt
import statistics

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.get('/api/weather-prediction/<date>/<time>/<lat>/<long>')
def weather_prediction(date, time, lat, long):
    url = f"https://api.meteomatics.com/{date}T00:00:00Z--{date}T23:59:59Z:PT30M/t_2m:C,wind_speed_10m:ms,precip_48h:mm/{lat},{long}/json"
    data = requests.get(url=url, auth=("malik_asher", "Gk3fQbD9p6FoCcAdUD0U")).json()

    # Reformat data
    organized = {}
    for parameter in data["data"]:
        param_name = parameter["parameter"]
        coord = parameter["coordinates"][0]
        values = [entry["value"] for entry in coord["dates"]]
        organized[param_name] = values
    print(organized)


    #calculate degrees of freedom, mean, standard deviation, convert x value to t value
    df_temperature = len(organized['t_2m:C']) - 1
    mean_temperature = sum(organized['t_2m:C'])/len(organized['t_2m:C'])
    standard_deviation_temperature = statistics.stdev(organized['t_2m:C'])
    x_hot = 25
    x_cold = 5
    t_temp_hot = (x_hot-mean_temperature)/(standard_deviation_temperature/sqrt(len(organized['t_2m:C'])))
    t_temp_cold = (x_cold-mean_temperature)/(standard_deviation_temperature/sqrt(len(organized['t_2m:C'])))
    area_hot_temp = 1- t.cdf(t_temp_hot, df_temperature)
    area_cold_temp = t.cdf(t_temp_cold, df_temperature)
    probability_very_hot = area_hot_temp * 100
    probability_very_cold = area_cold_temp * 100
    print(f"Probability of very hot: {probability_very_hot}%")
    print(f"Probability of very cold: {probability_very_cold}%")

    df_windspeed = len(organized["wind_speed_10m:ms"]) - 1
    mean_windspeed = sum(organized["wind_speed_10m:ms"])/len(organized["wind_speed_10m:ms"])
    standard_deviation_windspeed = statistics.stdev(organized["wind_speed_10m:ms"])
    x_windspeed = 13.9
    t_windspeed = (x_windspeed-mean_windspeed)/(standard_deviation_windspeed/sqrt(len(organized["wind_speed_10m:ms"])))
    area_windspeed = 1 - t.cdf(t_windspeed, df_windspeed)
    probability_very_windy = area_windspeed * 100
    print(f"Probability of very windy: {probability_very_windy}%")

    return 'test'

if __name__ == '__main__':
    app.run(debug=True)
