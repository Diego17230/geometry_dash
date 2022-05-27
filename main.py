import pygame
from pygame.locals import *

pygame.init()

screen = pygame.display.set_mode((500, 500))
pressed_keys = pygame.key.get_pressed()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((20, 20))
        self.rect = self.surf.get_rect()
        self.surf.fill((0, 255, 0))


class Game():
    def __init__(self):
        self.running = True

        self.player = Player()

        while self.running:
            self.update()

    def update(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
            elif event.type == QUIT:
                self.running = False

        screen.fill((100, 110, 110))
        screen.blit(self.player.surf, self.player.rect)
        pygame.display.flip()


if __name__ == "__main__":
    Game()
