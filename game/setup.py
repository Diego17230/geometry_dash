import main
import pygame
from pygame.locals import *


class Button(pygame.sprite.Sprite):
    def __init__(self, text_font: str, size: int, text: str, color: list, pos: tuple):
        super().__init__()
        # Makes the surface and the rectangle
        self.text = text
        font = pygame.font.Font(text_font, size)
        self.surf = font.render(self.text, False, color)
        self.rect = self.surf.get_rect()
        self.rect.center = pos


pygame.init()
screen = pygame.display.set_mode((500, 500))
screen.fill((255, 255, 255))
start_button = Button("freesansbold.ttf", 50, "Start Game", (255, 255, 255), (250, 75))
img_surf = pygame.image.load("images/game_background.png").convert_alpha()
img_surf = pygame.transform.scale(img_surf, (500, 500))
running = True
while running:
    screen.blit(img_surf, [0,0])
    screen.blit(start_button.surf, start_button.rect)
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.type == pygame.QUIT or event.key == K_ESCAPE:
                running = False
    if pygame.mouse.get_pressed()[0] == 1:
        mouse = pygame.mouse.get_pos()
        if start_button.rect.collidepoint(mouse):
            main.Game()
            pygame.quit()
    pygame.display.update()
pygame.quit()
