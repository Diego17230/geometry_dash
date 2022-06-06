import random

import pygame
from pygame.locals import *


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Player Setup
        self.surf = pygame.image.load("images/sprite.png").convert_alpha()
        self.surf = pygame.transform.scale(self.surf, (20, 20))
        self.rect = self.surf.get_rect(center=(250, 250))
        self.vel = [0, 0]
        self.on_ground = True
        self.platform_check = pygame.Surface((20, 40))
        self.platform_hitbox = self.platform_check.get_rect(center=(self.rect.centerx, self.rect.centery - 30))
        # Player has an obstacle hitbox that will detect incoming obstacles
        # This is used for the AI

    def update(self, space, screen, platform_group):
        # Sets space (Jump) to whatever was inputted in the update function
        self.space = space
        # Checks for collisions
        collision = self.ground_collision_detector(platform_group)
        if collision:
            self.on_ground = True
        else:
            self.on_ground = False

        # Jumping
        if self.space and self.on_ground:
            self.jump()

        # On ground
        if self.on_ground and not self.space:
            self.vel[1] = 0

        # Gravity
        if not self.on_ground and self.vel[1] < 10:
            self.gravity()

        self.move()
        self.platform_hitbox.centery = self.rect.centery - 30

    # Move function
    def move(self):
        self.rect.move_ip(*self.vel)

    def jump(self):
        self.vel[1] = -10
        self.on_ground = False

    def gravity(self):
        self.vel[1] += .7

    # Collision detector
    def ground_collision_detector(self, platform_group):
        for platform in platform_group:
            if platform.rect.colliderect(self.rect):
                if abs(self.rect.bottom - platform.rect.top) in range(1, 15):
                    self.rect.bottom = platform.rect.top + 1
                    return platform
                if abs(self.rect.top - platform.rect.bottom) in range(1, 15):
                    self.kill()
                if abs(self.rect.right - platform.rect.left) in range(1, 15):
                    self.kill()
        return False


class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        # Initilizes sprite class
        super().__init__()
        # Sets image of the sprite
        self.surf = pygame.image.load("images/spike.png")
        # Sets the rect (hitbox) and coordinates of where it should be located
        # using the x and y inputted when creating the object
        self.rect = self.surf.get_rect(center=(x, y))

    def update(self, dt):
        # Moves the spike towards the player
        # (since the player doesn't actually move)
        self.rect.move_ip(-0.175 * dt, 0)


class Platform(pygame.sprite.Sprite):
    def __init__(self, width, height, x, y):
        super().__init__()
        # Sets width and height using parameter values
        self.surf = pygame.image.load("images/platform.png").convert_alpha()
        self.surf = pygame.transform.scale(self.surf, (width, height))
        # Sets hitbox and location
        self.rect = self.surf.get_rect(center=(x, y))
        # Sets the color of the platform to grey using RGB scale

    def update(self, dt):
        # Moves the platform towards the player
        # Moves at a constant rate by multiplying it by delta time
        self.rect.move_ip(-0.175 * dt, 0)


class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.running = True
        pygame.init()
        self.screen = pygame.display.set_mode((500, 500))
        self.player = Player()
        self.space = False
        self.ground = Platform(500, 200, 250, 400)
        self.platforms = pygame.sprite.Group(self.ground)
        self.all_sprites = pygame.sprite.Group(self.player, self.ground)
        self.spikes = pygame.sprite.Group()
        self.platform_delay = 45
        self.spike_delay = 60
        self.incoming_obstacles = []
        self.jump_timer = -1

        while self.running:
            self.update()

    def check_distance(self, obj1, obj2):
        return obj2.rect.centerx - obj1.rect.centerx, obj2.rect.y - obj1.rect.y

    def update(self):
        # Sets delta time to the clock tick (will help catch up if application lags)
        dt = self.clock.tick(30)

        # Jump timer (used for a delay in jump when the AI needs to do so)
        if self.jump_timer == 0:
            self.space = True
        self.jump_timer -= 1

        # Checks if there are two or more obstacles coming towards the player
        if len(self.incoming_obstacles) >= 2:
            # Gets the first two obstacles
            obstacle1 = self.incoming_obstacles[0]
            obstacle2 = self.incoming_obstacles[1]

            """Checks if the x distance between the first and second obstacle
            is greater than 80 pixels (meaning the objects are too far away
            to be jumped over using only one jump) Also checks if the player is
            close enough to the first object to jump"""
            if self.check_distance(obstacle1, obstacle2)[0] >= 75:
                if isinstance(obstacle1, Spike) and \
                        self.check_distance(self.player, obstacle1)[0] < 100\
                        and not self.player.platform_hitbox.colliderect(obstacle2.rect):
                    self.space = True
                    self.incoming_obstacles.remove(obstacle1)
                elif isinstance(obstacle1, Platform) and \
                        self.check_distance(obstacle1, self.player)[0] > 5:
                    self.incoming_obstacles.remove(obstacle1)
            elif self.check_distance(obstacle1, obstacle2)[0] < 75:
                if isinstance(obstacle1, Spike):
                    if self.check_distance(obstacle1, obstacle2)[0] > 40:
                        if self.check_distance(self.player, obstacle1)[0] < 40:
                            self.space = True
                            self.incoming_obstacles.remove(obstacle1)
                            self.incoming_obstacles.remove(obstacle2)
                    elif self.check_distance(self.player, obstacle1)[0] < 80:
                        self.space = True
                        self.incoming_obstacles.remove(obstacle1)
                        self.incoming_obstacles.remove(obstacle2)
                elif isinstance(obstacle1, Platform) and self.check_distance(self.player, obstacle1)[0] < 120:
                    self.space = True
                    self.incoming_obstacles.remove(obstacle1)
                    self.incoming_obstacles.remove(obstacle2)
        elif len(self.incoming_obstacles) == 1:
            obstacle1 = self.incoming_obstacles[0]
            if isinstance(obstacle1, Spike) and self.check_distance(self.player, obstacle1)[0] < 100:
                self.space = True
                self.incoming_obstacles.remove(obstacle1)
            elif isinstance(obstacle1, Platform) and self.check_distance(obstacle1, self.player)[0] > -25:
                self.incoming_obstacles.remove(obstacle1)

        self.platform_delay -= 1
        self.spike_delay -= 1

        if self.platform_delay <= 0:
            platform = Platform(50, 10, 500, 250)

            platform.add(self.platforms, self.all_sprites)
            self.incoming_obstacles.append(platform)
            self.platform_delay = 60

        if self.spike_delay <= 0:
            spike = Spike(500, 290)
            spike.add(self.spikes,self.all_sprites)
            self.incoming_obstacles.append(spike)
            self.spike_delay = 61

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                if event.key == K_SPACE:
                    self.space = True
            elif event.type == QUIT:
                self.running = False

        for platform in self.platforms:
            if platform != self.ground:
                platform.update(dt)

        for spike in self.spikes:
            spike.update(dt)

            if spike.rect.colliderect(self.player.rect):
                self.running = False

        self.player.update(self.space, self.screen, self.platforms)
        self.space = False

        self.screen.fill((100, 110, 110))
        self.screen.blit(self.player.surf, self.player.rect)

        self.screen.fill((100, 110, 110))
        for sprite in self.all_sprites:
            self.screen.blit(sprite.surf, sprite.rect)
        pygame.display.flip()


if __name__ == "__main__":
    Game()
