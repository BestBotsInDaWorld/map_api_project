import os

import pygame
import pygame_gui
import requests


if __name__ == "__main__":
    pygame.init()
    size = width, height = 600, 450
    screen = pygame.display.set_mode(size)
    manager = pygame_gui.UIManager(size)
    screen.fill('black')
    input_rect = pygame.rect.Rect(20, 20, 400, 50)
    input_box = pygame_gui.elements.UITextEntryLine(input_rect, manager)
    running = True
    view_map = False
    map_file = "map.png"
    while running:
        for event in pygame.event.get():
            manager.process_events(event)
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                api_server = "https://geocode-maps.yandex.ru/1.x/"

                apikey = "40d1649f-0493-4b70-98ba-98533de7710b"
                geocode = '+'.join(input_box.get_text().split())
                format = 'json'

                params = {
                    "apikey": apikey,
                    "geocode": geocode,
                    "format": format
                }
                response = requests.get(api_server, params=params)
                if not response:
                    print("Ошибка выполнения запроса:")
                    print("Http статус:", response.status_code, "(", response.reason, ")")
                else:
                    json_response = response.json()
                    static_server = 'http://static-maps.yandex.ru/1.x/'
                    lon = json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split()[0]
                    lat = json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split()[1]
                    spn = '0.02'
                    map = 'map'
                    params = {
                        'll': ','.join([lon, lat]),
                        'spn': ','.join([spn, spn]),
                        'l': map
                    }
                    response_map = requests.get(static_server, params=params)
                    if response_map:
                        map_file = "map.png"
                        with open(map_file, "wb") as file:
                            file.write(response_map.content)
                        view_map = True
                    else:
                        print('error')
        if view_map:
            screen.blit(pygame.image.load(map_file), (0, 0))
        manager.draw_ui(screen)
        manager.update(1 / 60)
        pygame.display.flip()
    pygame.quit()

