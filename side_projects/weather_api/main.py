from flask import Flask, render_template

app = Flask("website", static_folder='/Users/akhil_p/Desktop/personal/coding/ML_portfolio/side_projects/weather_api/static', template_folder='/Users/akhil_p/Desktop/personal/coding/ML_portfolio/side_projects/weather_api/templates')

@app.route("/")
def home():
    return render_template("weather.html")


app.run(debug=True)