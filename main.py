import pygame
from pygame.locals import *


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((20, 20))
        self.rect = self.surf.get_rect(center=(250, 250))
        self.surf.fill((0, 255, 0))
        self.vel = [0, 0]
        self.on_ground = True

    def update(self, space, screen):
        if space and self.on_ground:
            self.vel[1] = -10
            self.on_ground = False

        if self.on_ground and not space:
            self.vel[1] = 0

        if not self.on_ground:
            self.vel[1] += .5

        self.move()

    def move(self):
        self.rect.move_ip(*self.vel)


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
        pygame.init()
        self.screen = pygame.display.set_mode((500, 500))
        self.player = Player()
        self.space = False
        self.platform = Platform()

        while self.running:
            self.update()

    def update(self):
        dt = self.clock.tick(30)

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                if event.key == K_SPACE:
                    self.space = True
            elif event.type == QUIT:
                self.running = False

        self.player.update(self.space, self.screen)
        self.space = False

        self.screen.fill((100, 110, 110))
        self.screen.blit(self.player.surf, self.player.rect)
        self.platform.update(dt)

        self.screen.fill((100, 110, 110))
        self.screen.blit(self.player.surf, self.player.rect)
        self.screen.blit(self.platform.surf, self.platform.rect)
        pygame.display.flip()


if __name__ == "__main__":
    Game()
