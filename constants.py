import pygame
import pygame_gui
pygame.init()
size = width, height = 600, 800
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Map")
manager = pygame_gui.UIManager(size)
