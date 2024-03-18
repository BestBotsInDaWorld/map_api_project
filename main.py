import sys
from io import BytesIO
from math import cos
# Этот класс поможет нам сделать картинку из потока байт
import pygame
import requests
from get_by_coords import get_by_coords
import pygame_gui
from constants import *


def make_fields(coord_values, name_values):
    labels = [pygame_gui.elements.UILabel(pygame.Rect(-50, 500 + i * 40, 200, 30), text=value, manager=manager)
              for i, value in zip(range(len(coord_values)), coord_values)] + [
              pygame_gui.elements.UILabel(pygame.Rect(235, 500 + i * 40, 200, 30), text=value, manager=manager)
              for i, value in zip(range(len(coord_values)), name_values)]
    input_fields = {key: pygame_gui.elements.UITextEntryLine(pygame.Rect(100, 500 + i * 40, 200, 30), manager=manager)
                    for i, key in zip(range(len(coord_values)), coord_values)} | {
                    key: pygame_gui.elements.UITextEntryLine(pygame.Rect(385, 500 + i * 40, 200, 30), manager=manager)
                    for i, key in zip(range(len(coord_values)), name_values)}
    return input_fields


def get_coord_parameters(input_fields):
    longitude, latitude = input_fields["longitude"].get_text(), input_fields["latitude"].get_text()
    span_long, span_lat = input_fields["span_long"].get_text(), input_fields["span_lat"].get_text()
    try:
        longitude, latitude, span_long, span_lat = float(longitude), float(latitude), float(span_long), float(span_lat)
    except Exception:
        return 0
    return {"longitude": longitude, "latitude": latitude, "span_long": span_long, "span_lat": span_lat}


def get_delta(toponym):
    delta_corneres = toponym["boundedBy"]["Envelope"]
    upper_corner = list(map(float, delta_corneres["upperCorner"].split()))
    lower_corner = list(map(float, delta_corneres["lowerCorner"].split()))
    return [str(upper_corner[0] - lower_corner[0]), str(upper_corner[1] - lower_corner[1])]


def get_by_name(input_fields):
    geocoder_server = "https://geocode-maps.yandex.ru/1.x/"
    toponym_to_find = input_fields["toponym"].get_text()
    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": toponym_to_find,
        "format": "json"
    }

    response = requests.get(geocoder_server, params=geocoder_params)
    if not response:
        return 0
    json_response = response.json()
    try:
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"]
        longitude, latitude = list(map(float, toponym_coodrinates.split(" ")))
        span_long, span_lat = list(map(float, get_delta(toponym)))
        return {"longitude": longitude, "latitude": latitude, "span_long": span_long, "span_lat": span_lat}
    except Exception:
        return 0


def zoom(parameters, mouse_y):
    try:
        if mouse_y < 0:
            parameters["span_long"] = min(parameters["span_long"] + parameters["span_long"] / 5, 50)
            parameters["span_lat"] = min(parameters["span_lat"] + parameters["span_lat"] / 5, 50)
        else:
            parameters["span_long"] = max(parameters["span_long"] - parameters["span_long"] / 5, 0.005)
            parameters["span_lat"] = max(parameters["span_lat"] - parameters["span_lat"] / 5, 0.005)
        return parameters
    except Exception:
        return 0


def get_sign_coords(parameters, mouse_coords):
    try:
        x, y = mouse_coords
        long_degree = parameters["span_long"] / width * 2
        lat_degree = parameters["span_lat"] / height
        delta_long, delta_lat = width // 2 - x, height // 4 - y
        print([parameters["longitude"] - delta_long * long_degree, parameters["latitude"] + delta_lat * lat_degree])
        return [parameters["longitude"] - delta_long * long_degree, parameters["latitude"] + delta_lat * lat_degree]
    except Exception:
        return 0


def update_params(input_fields, parameters):
    for key in parameters.keys():
        input_fields[key].set_text(str(parameters[key]))


def update_map(params):
    global cur_parameters, input_fields, sign_coords, screen
    cur_parameters = params
    update_params(input_fields, cur_parameters)
    result = get_by_coords(cur_parameters, sign_coords)
    if result:
        screen.blit(result, (0, 0))


if __name__ == '__main__':
    fps = 60
    running = True
    sign_coords = []
    clock = pygame.time.Clock()
    coord_button = pygame_gui.elements.UIButton(pygame.Rect(100, 700, 200, 50), text="Coord Search", manager=manager)
    name_button = pygame_gui.elements.UIButton(pygame.Rect(350, 700, 200, 50), text="Name Search", manager=manager)
    input_fields = make_fields(["longitude", "latitude", "span_long", "span_lat"], ["toponym"])
    cur_parameters = {"longitude": None, "latitude": None, "span_long": None, "span_lat": None}
    screen.fill('white')
    while running:
        for event in pygame.event.get():
            manager.process_events(event)

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == coord_button:  # поиск по координатам
                    params = get_coord_parameters(input_fields)
                    if params:
                        update_map(params)
                elif event.ui_element == name_button:  # поиск по названию
                    params = get_by_name(input_fields)
                    if params:
                        sign_coords = [params["longitude"], params["latitude"]]
                        update_map(params)

            if event.type == pygame.MOUSEWHEEL:  # зум
                params = zoom(cur_parameters.copy(), event.precise_y)
                if params:
                    update_map(params)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                if event.pos[1] < height // 2:
                    new_sign_coords = get_sign_coords(cur_parameters, event.pos)
                    if new_sign_coords:
                        sign_coords = new_sign_coords
                        print(sign_coords)
                        update_map(cur_parameters)
        manager.draw_ui(screen)
        manager.update(1 / fps)
        pygame.display.flip()
        clock.tick(fps)
