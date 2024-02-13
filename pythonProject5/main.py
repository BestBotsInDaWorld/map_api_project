import sys
from io import BytesIO
from math import cos
# Этот класс поможет нам сделать картинку из потока байт
import pygame
import requests
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
toponym_to_find = " ".join(sys.argv[1:])

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "geocode": toponym_to_find,
    "format": "json"
}

response = requests.get(geocoder_api_server, params=geocoder_params)
json_response = response.json()

if not response:
    # обработка ошибочной ситуации
    pass

toponym = json_response["response"]["GeoObjectCollection"][
    "featureMember"][0]["GeoObject"]

# Координаты центра топонима:
toponym_coodrinates = toponym["Point"]["pos"]
search_api_server = "https://search-maps.yandex.ru/v1/"
api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
address_ll = ",".join(toponym_coodrinates.split())


search_params = {
    "apikey": api_key,
    "text": "правительство",
    "lang": "ru_RU",
    "ll": address_ll,
    "type": "biz"
}

response = requests.get(search_api_server, params=search_params)

if not response:
    #...
    pass
json_response = response.json()

# Получаем первую найденную организацию.
organization = json_response["features"][0]
# Название организации.
org_name = organization["properties"]["CompanyMetaData"]["name"]
# Адрес организации.
org_address = organization["properties"]["CompanyMetaData"]["address"]

# Получаем координаты ответа.
point = organization["geometry"]["coordinates"]
org_point = "{0},{1}".format(point[0], point[1])
delta = "0.05"

# Собираем параметры для запроса к StaticMapsAPI:
map_params = {
    # позиционируем карту центром на наш исходный адрес
    "l": "map",
    # добавим точку, чтобы указать найденную аптеку
    "pt": "{0},pm2dgl~{1},pm2gnl".format(org_point, address_ll)
}


def get_info(organization, point_initial, point_address):
    longitude = abs(point_address[0] - point_initial[0])
    latitude = abs(point_address[1] - point_initial[1])
    return {"delta_x": longitude * 111000,
            "delta_y": latitude * 111000 * cos(latitude),
            "working_time": organization["properties"]["CompanyMetaData"]["Hours"]["text"]}


map_api_server = "http://static-maps.yandex.ru/1.x/"
# ... и выполняем запрос
response = requests.get(map_api_server, params=map_params)

info = get_info(organization, list(map(float, toponym_coodrinates.split())), point)
coord_text = f"Расстояние по долготе: {info['delta_x']}\n" \
             f"Расстояние по широте: {info['delta_y']}\n" \
             f"Часы работы: {info['working_time']}"

size = width, height = 800, 800
screen = pygame.display.set_mode(size)
image = pygame.image.load(BytesIO(response.content)).convert()

pygame.init()
if __name__ == '__main__':
    running = True
    fps = 60
    clock = pygame.time.Clock()
    while running:
        screen.fill('white')
        screen.blit(image, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        clock.tick(fps)
        pygame.display.flip()
    pygame.quit()