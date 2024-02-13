import requests
import sys
from io import BytesIO
import pygame
map_api_server = "http://static-maps.yandex.ru/1.x/"


def get_place(input_fields):
    longitude, latitude = input_fields["longitude"].get_text(), input_fields["longitude"].get_text()
    span1, span2 = input_fields["span1"].get_text(), input_fields["span2"].get_text()
    try:
        longitude, latitude, span1, span2 = float(longitude), float(latitude), float(span1), float(span2)
    except Exception:
        return 0
    geocoder_params = {
        "ll": ",".join([str(longitude), str(latitude)]),
        "spn": ",".join([str(span1), str(span2)]),
        "l": "sat",
    }

    response = requests.get(map_api_server, params=geocoder_params)
    print(response.content)
    return pygame.image.load(BytesIO(response.content)).convert()