import main
import pygame
from pygame.locals import *


# Button class
class Button(pygame.sprite.Sprite):
    def __init__(self, text_font: str, size: int, text: str, color: list, pos: tuple):
        super().__init__()
        # Makes the surface and the rectangle
        self.color = color
        self.text = text
        self.font = pygame.font.Font(text_font, size)
        self.surf = self.font.render(self.text, False, self.color)
        self.rect = self.surf.get_rect()
        self.rect.center = pos

    def set_text(self, text):
        self.text = text
        self.surf = self.font.render(self.text, False, self.color)
        if len(text) > 13:
            self.rect.centerx = 180
        if len(text) > 10:
            self.rect.centerx = 200
        else:
            self.rect.centerx = 250


pygame.init()
screen = pygame.display.set_mode((500, 500))
screen.fill((255, 255, 255))
# Makes a button object
modes = ["AI Only", "Player Only", "AI and Player"]
start_button = Button("freesansbold.ttf", 50, "Start Game", (255, 255, 255), (250, 75))
mode_button = Button("freesansbold.ttf", 40, modes[0], (255, 255, 255), (250, 125))
# Gets the image surface and then scales it up
img_surf = pygame.image.load("images/game_background.png").convert_alpha()
img_surf = pygame.transform.scale(img_surf, (500, 500))
click_delay = 0
running = True
while running:
    click_delay -= 1
    # blits the image onto the screen and then the button
    screen.blit(img_surf, [0, 0])
    screen.blit(start_button.surf, start_button.rect)
    screen.blit(mode_button.surf, mode_button.rect)
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
            main.Game(modes.index(mode_button.text))
            pygame.quit()
        elif mode_button.rect.collidepoint(mouse) and click_delay < 0:
            click_delay = 60
            try:
                mode_button.set_text(modes[modes.index(mode_button.text) + 1])
            except IndexError:
                mode_button.set_text(modes[0])
    pygame.display.update()
pygame.quit()
