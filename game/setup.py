import main
import pygame
from pygame.locals import *


# Button class
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
# Makes a button object
start_button = Button("freesansbold.ttf", 50, "Start Game", (255, 255, 255), (250, 75))
# Gets the image surface and then scales it up
img_surf = pygame.image.load("images/game_background.png").convert_alpha()
img_surf = pygame.transform.scale(img_surf, (500, 500))
running = True
while running:
    # blits the image onto the screen and then the button
    screen.blit(img_surf, [0, 0])
    screen.blit(start_button.surf, start_button.rect)
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            # if the user quits
            if event.type == pygame.QUIT or event.key == K_ESCAPE:
                running = False
    if pygame.mouse.get_pressed()[0] == 1:
        mouse = pygame.mouse.get_pos()
        # If the user left clicks on the button the game class from the main.py file is called and this
        # pygame is quit
        if start_button.rect.collidepoint(mouse):
            main.Game()
            pygame.quit()
    pygame.display.update()
pygame.quit()
