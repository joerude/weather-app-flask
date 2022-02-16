import os

import requests
from dotenv import load_dotenv
from flask import Response

load_dotenv()
# env variables

API_KEY = os.getenv("API_KEY")
UNITS = "metric"  # Temperature in Celsius


def _get_weather_from_open_weather_api(city: str, key: str, units: str) -> Response:
    url = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units={}" \
        .format(city, key, units)
    return requests.get(url=url)


def get_weather_at(city: str, key: str = API_KEY, units: str = UNITS) -> Response:
    return _get_weather_from_open_weather_api(city, key, units)
