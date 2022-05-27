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


class Platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((50, 20))
        self.rect = self.surf.get_rect(center=(800 - self.surf.get_width(), 250 - self.surf.get_height()))
        self.surf.fill((255, 255, 0))

    def update(self, dt):
        self.rect.move_ip(-0.1 * dt, 0)


class Game():
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.running = True

        self.player = Player()
        self.platform = Platform()

        while self.running:
            self.update()

    def update(self):
        dt = self.clock.tick(30)

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
            elif event.type == QUIT:
                self.running = False

        self.platform.update(dt)

        screen.fill((100, 110, 110))
        screen.blit(self.player.surf, self.player.rect)
        screen.blit(self.platform.surf, self.platform.rect)
        pygame.display.flip()


if __name__ == "__main__":
    Game()
