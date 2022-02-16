import os
import sys

from flask import Flask, flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_sqlalchemy import SQLAlchemy

from utils import get_weather_at

app = Flask(__name__, template_folder="templates")

# file_path = os.path.dirname(sys.argv[0])  # path to directory app.py is in
# app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{file_path}/weather.db"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config.update(SECRET_KEY=os.urandom(10))
db = SQLAlchemy(app)


# os.path.dirname(sys.argv[0])

class City(db.Model):
    __tablename__ = "cities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    current_temp = db.Column(db.Integer, nullable=False)
    current_state = db.Column(db.String(30), default="Unknown")

    def __repr__(self) -> str:
        return f"City(id={self.id}, name={self.name}," \
               f" current_temp={self.current_temp}, current_state={self.current_state})"

    @staticmethod
    def find_all() -> list["City"]:
        return City.query.all()

    @staticmethod
    def add(city: "City") -> None:
        db.session.add(city)
        db.session.commit()


db.create_all()


@app.route("/")
def index():
    # Get the data from the database
    data = City.find_all()

    return render_template("index.html", weather=data if data else None)


@app.route("/add", methods=["POST"])
def add_city():
    if request.method == "POST":
        # Get city name from POST request and capitalize the first letter of each word
        city = request.form["city"].title()
        data = get_weather_at(city)

        print(City.query.filter_by(name=city).first())
        print(get_weather_at(city).status_code)

        # print(db.session.query(City.name))

        if get_weather_at(city).status_code == 404:
            flash("The city doesn't exist!")
            return redirect('/')

        lst = City.query.all()
        cities = [i.name.lower() for i in lst]
        if city.lower() in cities:
            flash("The city has already been added to the list!")
            return redirect('/')

        if data:
            weather_data = data.json()
            # Create an instance of City with weather data and commit to the database

            City.add(City(name=city,
                          current_temp=int(weather_data["main"]["temp"]),
                          current_state=weather_data["weather"][0]["main"]))

    return redirect(url_for("index"))


@app.route('/delete/<city_id>', methods=['GET', 'POST'])
def delete(city_id):
    city = City.query.filter_by(id=city_id).first()
    db.session.delete(city)
    db.session.commit()
    return redirect('/')


def main() -> None:
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()

# if __name__ == "__main__":
#     main()
