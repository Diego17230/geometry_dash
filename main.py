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
            self.vel[1] += .3

        self.move()

    def move(self):
        self.rect.move_ip(*self.vel)


class Game():
    def __init__(self):
        self.running = True
        pygame.init()
        self.screen = pygame.display.set_mode((500, 500))
        self.player = Player()
        self.space = False
        while self.running:
            self.update()

    def update(self):
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
        pygame.display.flip()


if __name__ == "__main__":
    Game()
