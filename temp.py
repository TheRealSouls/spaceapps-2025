# from flask import Flask, render_template, jsonify
# import requests

# app = Flask(__name__)

# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.get('/api/weather-prediction/<date>/<time>/<lat>/<long>')
# def weather_prediction(date, time, lat, long):
#     url = f"https://api.meteomatics.com/{date}T00:00:00Z--{date}T23:59:59Z:PT1H/t_2m:C,wind_speed_10m:ms/{lat},{long}/json"
#     data = requests.get(url=url).json()
#     return jsonify({'data': data})


# if __name__ == '__main__':
#     app.run(debug=True)
