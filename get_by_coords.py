import requests
import sys
from io import BytesIO
import pygame
from constants import *

map_api_server = "http://static-maps.yandex.ru/1.x/"


def get_by_coords(parameters, sign_coords=None):
    longitude, latitude, span_long, span_lat = (parameters["longitude"], parameters["latitude"],
                                                parameters["span_long"], parameters["span_lat"])
    if sign_coords:
        geocoder_params = {
            "ll": ",".join([str(longitude), str(latitude)]),
            "spn": ",".join([str(span_long), str(span_lat)]),
            "l": "map",
            "size": f"{width},{height // 2}",
            "pt": ",".join([str(sign_coords[0]), str(sign_coords[1]), "pm2wtm42"]),
        }
    else:
        geocoder_params = {
            "ll": ",".join([str(longitude), str(latitude)]),
            "spn": ",".join([str(span_long), str(span_lat)]),
            "l": "map",
            "size": f"{width},{height // 2}",
        }

    response = requests.get(map_api_server, params=geocoder_params)
    try:
        img = pygame.image.load(BytesIO(response.content)).convert()
        return img
    except Exception:
        return 0
