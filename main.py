import os
import sys

import pygame
import requests

server_address = 'https://static-maps.yandex.ru/v1?'
api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
ll_one = 37.530887  # Долгота
ll_two = 55.703118  # Широта
spn_one = 0.002  # Разность долгота
spn_two = 0.002  # Разность широта
map_file = 'map_png'


def request():
    map_request = f"{server_address}ll={str(ll_one)},{str(ll_two)}&spn={str(spn_one)},{str(spn_two)}&apikey={api_key}"
    response = requests.get(map_request)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)

    with open(map_file, "wb") as file:
        file.write(response.content)


pygame.init()
running = True
screen = pygame.display.set_mode((600, 450))
request()
screen.blit(pygame.image.load(map_file), (0, 0))
pygame.display.flip()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                spn_one -= spn_one / 2
                spn_two -= spn_two / 2
                if spn_one < 0.0001 or spn_two < 0.0001:
                    spn_one = 0.0001
                    spn_two = 0.0001
            elif event.key == pygame.K_s:
                spn_one += spn_one
                spn_two += spn_two

    keys = pygame.key.get_pressed()
    if any(keys):
        if keys[pygame.K_DOWN]:
            ll_two -= spn_two / 4
            if ll_two < 0:
                ll_two = 0

        if keys[pygame.K_UP]:
            ll_two += spn_two / 4
            if ll_two > 90:
                ll_two = 90

        if keys[pygame.K_RIGHT]:
            ll_one += spn_one / 4
            if ll_one > 180:
                ll_one = 180

        if keys[pygame.K_LEFT]:
            ll_one -= spn_one / 4
            if ll_one < -180:
                ll_one = -180

        request()

    screen.blit(pygame.image.load(map_file), (0, 0))

    pygame.display.flip()

pygame.quit()

os.remove(map_file)