import random
import pygame
from pygame.locals import *


# Button class
class Button(pygame.sprite.Sprite):
    def __init__(self, text_font: str, size: int, text: str, color: list,
                 pos: tuple):
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


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Player Setup
        self.surf = pygame.image.load("images/sprite.png").convert_alpha()
        # Changes the 16x16 square image to 20x20 since that is the size we tested the AI with
        self.surf = pygame.transform.scale(self.surf, (20, 20))
        self.rect = self.surf.get_rect(center=(x, y))
        # Sets x and y velocity to 0
        self.vel = [0, 0]
        self.on_ground = True
        self.dead = False
        """Adds a sepereate surface and hitbox above the player to check if 
        there is a platform above the player"""
        self.platform_check = pygame.Surface((20, 40))
        self.platform_hitbox = self.platform_check.get_rect(
            center=(self.rect.centerx, self.rect.centery - 30))

    def update(self, space, screen, platform_group):
        # Sets space (Jump) to whatever was inputted in the update function
        # Checks for collisions
        collision = self.ground_collision_detector(platform_group)
        if collision:
            self.on_ground = True
        else:
            self.on_ground = False

        # Jumping
        if space and self.on_ground:
            self.jump()

        # On ground
        if self.on_ground and not space:
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
                    self.dead = True
                if abs(self.rect.right - platform.rect.left) in range(1, 15):
                    self.dead = True
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
    def __init__(self, width, height, x, y, ground=False):
        super().__init__()
        # Sets width and height using parameter values
        if not ground:
            self.surf = pygame.image.load(
                "images/platform.png").convert_alpha()
            # Scales up the image
            self.surf = pygame.transform.scale(self.surf, (width, height))
        else:
            self.surf = pygame.Surface((width, height))
            self.surf.fill((120, 120, 120))
        # Sets hitbox and location
        self.rect = self.surf.get_rect(center=(x, y))
        # Sets the color of the platform to grey using RGB scale

    def update(self, dt):
        # Moves the platform towards the player
        # Moves at a constant rate by multiplying it by delta time
        self.rect.move_ip(-0.175 * dt, 0)


class Game:
    def __init__(self, mode):
        self.mode = mode
        self.clock = pygame.time.Clock()
        # Will run the game while this is true
        self.running = True
        # Sets the screen
        self.screen = pygame.display.set_mode((500, 500))

        # Creates the ground as a giant platform
        self.ground = Platform(500, 20, 250, 310, True)
        # Adds the ground to the platforms group
        self.platforms = pygame.sprite.Group(self.ground)
        # Adds player and ground to all sprites group
        self.all_sprites = pygame.sprite.Group(self.ground)
        self.score = 0

        # Creates the player
        if mode != 1:
            self.AI = Player(200, 250)
            self.AI.add(self.all_sprites)
        if mode != 0:
            self.player = Player(250, 250)
            self.player.add(self.all_sprites)
        # Initializes the space variable (space = whether AI should jump or not)
        self.space = False
        # Creates spikes group
        self.spikes = pygame.sprite.Group()

        # Creates delays for the platform and spikes (number = amount of frames)
        self.platform_delay = 60
        self.spike_delay = 45
        self.incoming_obstacles = []

        while self.running:
            if mode == 0:
                self.mode1_update()
            elif mode == 1:
                self.mode2_update()
            elif mode == 2:
                self.mode3_update()
            
            if mode != 0 and self.player.dead:
                pygame.quit()
                End()

            if mode != 0 and self.player.dead:
                pygame.quit()
                End(self.score)

    def update_score(self):
        self.score += 1
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render('Score: ' + str(self.score), True, (0, 255, 0))

        textRect = text.get_rect()

        # set the center of the rectangular object.
        textRect.center = (250, 100)
        self.screen.blit(text, textRect)

    def check_distance(self, obj1, obj2):
        """This function returns a tuple (x, y)
        of the distance between two objects"""
        return obj2.rect.centerx - obj1.rect.centerx, obj2.rect.y - obj1.rect.y

    def manage_obstacle_delay(self, spike_delay=61, platform_delay=60,
                              random_platforms=False):
        # Lowers the spike and platform delay by 1 every frame
        self.platform_delay -= 1
        self.spike_delay -= 1

        # Checks and adds obstacles if delay is <= 0
        if self.platform_delay <= 0:
            # Checks if random platforms are enabled (Only for single player)
            if random_platforms:
                platform = Platform(random.randint(25, 100), 10, 500,
                                    random.randint(240, 260))
            else:
                platform = Platform(50, 10, 500, 250)
            platform.add(self.platforms, self.all_sprites)
            self.incoming_obstacles.append(platform)
            self.platform_delay = platform_delay

        if self.spike_delay <= 0:
            spike = Spike(500, 290)
            spike.add(self.spikes, self.all_sprites)
            self.incoming_obstacles.append(spike)
            self.spike_delay = spike_delay

    def update_obstacles(self, dt):
        # Updates every platform in the platform group (except the ground)
        for platform in self.platforms:
            if platform != self.ground:
                platform.update(dt)

        # Updates every spike and checks for collisions with player
        for spike in self.spikes:
            spike.update(dt)

    def mode1_update(self):
        """This function is run every frame of the game and returns nothing"""
        # Sets delta time to the clock tick (will help catch up if application lags)
        dt = self.clock.tick(30)

        # Checks if there are two or more obstacles coming towards the player
        if len(self.incoming_obstacles) >= 2:
            # Gets the first two obstacles
            obstacle1 = self.incoming_obstacles[0]
            obstacle2 = self.incoming_obstacles[1]

            """Checks if the x distance between the first and second obstacle
            is greater than 75 pixels (meaning the objects are too far away
            to be jumped over using only one jump) Also checks if the player is
            close enough to the first object to jump"""
            if self.check_distance(obstacle1, obstacle2)[0] >= 75:
                if isinstance(obstacle1, Spike) and \
                        self.check_distance(self.AI, obstacle1)[0] < 100 \
                        and not self.AI.platform_hitbox.colliderect(
                    obstacle2.rect):
                    self.space = True
                    self.incoming_obstacles.remove(obstacle1)
                elif isinstance(obstacle1, Platform) and \
                        self.check_distance(obstacle1, self.AI)[0] > 5:
                    """
                    Removes platform once it's slightly behind the player
                    so the platform dectector attached to the player
                    can check if its collding with a platform in the 
                    incoming_obstacles list (used for stopping AI from jumping
                    when there is a platform above it)
                    """
                    self.incoming_obstacles.remove(obstacle1)

            elif self.check_distance(obstacle1, obstacle2)[0] < 75:
                if isinstance(obstacle1, Spike):
                    """
                    Checks if the distance between the spike and the platform
                    is greater than 40 meaning the platform is fairly far
                    and the AI should jump later
                    """
                    if self.check_distance(obstacle1, obstacle2)[0] > 40:
                        """Checks for when the object is close
                        (can't be an addon to the other if statement because
                        if this is false it will run the elif which is to
                        jump earlier)"""
                        if self.check_distance(self.AI, obstacle1)[0] < 40:
                            self.space = True
                            self.incoming_obstacles.remove(obstacle1)
                            self.incoming_obstacles.remove(obstacle2)
                    elif self.check_distance(self.AI, obstacle1)[0] < 80:
                        self.space = True
                        self.incoming_obstacles.remove(obstacle1)
                        self.incoming_obstacles.remove(obstacle2)
                # The platform is ahead of the spike meaning the AI needs to
                # jump earlier since the platform is wider and higher in the
                # y position than a spike
                # (The bot can fall off from the platform and still get over the spike as well)
                elif isinstance(obstacle1, Platform) and \
                        self.check_distance(self.AI, obstacle1)[0] < 120:
                    self.space = True
                    self.incoming_obstacles.remove(obstacle1)
                    self.incoming_obstacles.remove(obstacle2)

        elif len(self.incoming_obstacles) == 1:
            obstacle1 = self.incoming_obstacles[0]
            # Jumps over a single spike at correct timing
            if isinstance(obstacle1, Spike) and \
                    self.check_distance(self.AI, obstacle1)[0] < 100:
                self.space = True
                self.incoming_obstacles.remove(obstacle1)
            # Stays on ground and removes single platform from the incoming_obstacles
            # once it passes
            elif isinstance(obstacle1, Platform) and \
                    self.check_distance(obstacle1, self.AI)[0] > -25:
                self.incoming_obstacles.remove(obstacle1)

        # Manages everything to do with the obstacle delay (check function for more details)
        self.manage_obstacle_delay()

        # Checks if player has clicked any keys to end the game
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.type == QUIT:
                    self.running = False

        self.update_obstacles(dt)

        # Updates the AI
        self.AI.update(self.space, self.screen, self.platforms)
        # Resets space to false
        self.space = False

        # Sets the background to black
        self.screen.fill((0, 0, 0))

        # Adds all sprites on screen
        for sprite in self.all_sprites:
            self.screen.blit(sprite.surf, sprite.rect)
        # Displays the new screen
        pygame.display.flip()

    def mode2_update(self):
        """This function is run every frame of the game and returns nothing"""
        # Sets delta time to the clock tick (will help catch up if application lags)
        dt = self.clock.tick(30)

        # Manages everything to do with the obstacle delay (check function for more details)
        self.manage_obstacle_delay(random.randint(20, 50),
                                   random.randint(45, 100), True)

        # Checks if player has clicked any keys to end the game
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.type == QUIT:
                    self.running = False
                if event.key == K_SPACE:
                    self.space = True

        self.update_obstacles(dt)

        for spike in self.spikes:
            if spike.rect.colliderect(self.player.rect):
                self.player.dead = True

        # Updates the player
        self.player.update(self.space, self.screen, self.platforms)
        self.space = False

        # Sets the background to black
        self.screen.fill((0, 0, 0))

        # Runs score manager
        self.update_score()

        # Adds all sprites on screen
        for sprite in self.all_sprites:
            self.screen.blit(sprite.surf, sprite.rect)
        # Displays the new screen
        pygame.display.flip()

    def mode3_update(self):
        """This function is run every frame of the game and returns nothing"""
        # Sets delta time to the clock tick (will help catch up if application lags)
        dt = self.clock.tick(30)
        self.score += 1

        # Checks if there are two or more obstacles coming towards the player
        if len(self.incoming_obstacles) >= 2:
            # Gets the first two obstacles
            obstacle1 = self.incoming_obstacles[0]
            obstacle2 = self.incoming_obstacles[1]

            """Checks if the x distance between the first and second obstacle
            is greater than 75 pixels (meaning the objects are too far away
            to be jumped over using only one jump) Also checks if the player is
            close enough to the first object to jump"""
            if self.check_distance(obstacle1, obstacle2)[0] >= 75:
                if isinstance(obstacle1, Spike) and \
                        self.check_distance(self.AI, obstacle1)[0] < 100 \
                        and not self.AI.platform_hitbox.colliderect(
                    obstacle2.rect):
                    self.space = True
                    self.incoming_obstacles.remove(obstacle1)
                elif isinstance(obstacle1, Platform) and \
                        self.check_distance(obstacle1, self.AI)[0] > 5:
                    """
                    Removes platform once it's slightly behind the player
                    so the platform dectector attached to the player
                    can check if its collding with a platform in the 
                    incoming_obstacles list (used for stopping AI from jumping
                    when there is a platform above it)
                    """
                    self.incoming_obstacles.remove(obstacle1)

            elif self.check_distance(obstacle1, obstacle2)[0] < 75:
                if isinstance(obstacle1, Spike):
                    """
                    Checks if the distance between the spike and the platform
                    is greater than 40 meaning the platform is fairly far
                    and the AI should jump later
                    """
                    if self.check_distance(obstacle1, obstacle2)[0] > 40:
                        """Checks for when the object is close
                        (can't be an addon to the other if statement because
                        if this is false it will run the elif which is to
                        jump earlier)"""
                        if self.check_distance(self.AI, obstacle1)[0] < 40:
                            self.space = True
                            self.incoming_obstacles.remove(obstacle1)
                            self.incoming_obstacles.remove(obstacle2)
                    elif self.check_distance(self.AI, obstacle1)[0] < 80:
                        self.space = True
                        self.incoming_obstacles.remove(obstacle1)
                        self.incoming_obstacles.remove(obstacle2)
                # The platform is ahead of the spike meaning the AI needs to
                # jump earlier since the platform is wider and higher in the
                # y position than a spike
                # (The bot can fall off from the platform and still get over the spike as well)
                elif isinstance(obstacle1, Platform) and \
                        self.check_distance(self.AI, obstacle1)[0] < 120:
                    self.space = True
                    self.incoming_obstacles.remove(obstacle1)
                    self.incoming_obstacles.remove(obstacle2)

        elif len(self.incoming_obstacles) == 1:
            obstacle1 = self.incoming_obstacles[0]
            # Jumps over a single spike at correct timing
            if isinstance(obstacle1, Spike) and \
                    self.check_distance(self.AI, obstacle1)[0] < 100:
                self.space = True
                self.incoming_obstacles.remove(obstacle1)
            # Stays on ground and removes single platform from the incoming_obstacles
            # once it passes
            elif isinstance(obstacle1, Platform) and \
                    self.check_distance(obstacle1, self.AI)[0] > -25:
                self.incoming_obstacles.remove(obstacle1)

        # Manages everything to do with the obstacle delay (check function for more details)
        self.manage_obstacle_delay()

        player_jump = False
        # Checks if player has clicked any keys to end the game
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.type == QUIT:
                    self.running = False
                if event.key == K_SPACE:
                    player_jump = True

        self.update_obstacles(dt)

        for spike in self.spikes:
            if spike.rect.colliderect(self.player.rect):
                self.player.dead = True

        # Updates the player
        self.AI.update(self.space, self.screen, self.platforms)
        self.player.update(player_jump, self.screen, self.platforms)
        # Resets space to false
        self.space = False

        # Sets the background to black
        self.screen.fill((0, 0, 0))

        # Runs score manager
        self.update_score()

        # Adds all sprites on screen
        for sprite in self.all_sprites:
            self.screen.blit(sprite.surf, sprite.rect)
        # Displays the new screen
        pygame.display.flip()


class Menu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((500, 500))
        # Makes a button object
        self.modes = ["AI Only", "Player Only", "AI and Player"]
        self.start_button = Button("freesansbold.ttf", 50, "Start Game",
                                   (255, 255, 255), (250, 75))
        self.mode_button = Button("freesansbold.ttf", 40, self.modes[0],
                                  (255, 255, 255),
                                  (250, 125))
        # Gets the image surface and then scales it up
        self.img_surf = pygame.image.load(
            "images/game_background.png").convert_alpha()
        self.img_surf = pygame.transform.scale(self.img_surf, (500, 500))
        self.click_delay = 0
        self.running = True
        while self.running:
            self.update()

    def update(self):
        self.click_delay -= 1
        # blits the image onto the screen and then the button
        self.screen.blit(self.img_surf, [0, 0])
        self.screen.blit(self.start_button.surf, self.start_button.rect)
        self.screen.blit(self.mode_button.surf, self.mode_button.rect)
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                # if the user quits
                if event.type == pygame.QUIT or event.key == K_ESCAPE:
                    self.running = False
        if pygame.mouse.get_pressed()[0] == 1:
            mouse = pygame.mouse.get_pos()
            # If the user left clicks on the button the game class from the main.py file is called and this
            # pygame is quit
            if self.start_button.rect.collidepoint(mouse):
                Game(self.modes.index(self.mode_button.text))
                pygame.quit()
            elif self.mode_button.rect.collidepoint(
                    mouse) and self.click_delay < 0:
                self.click_delay = 60
                try:
                    self.mode_button.set_text(
                        self.modes[
                            self.modes.index(self.mode_button.text) + 1])
                except IndexError:
                    self.mode_button.set_text(self.modes[0])
        pygame.display.update()
    pygame.quit()


class End:
    def __init__(self):
        pygame.init()
        self.died_button = Button("freesansbold.ttf", 40, "You Died!", (255, 255, 255), (250, 75))
        self.continue_button = Button("freesansbold.ttf", 40, "Continue?", (255, 255, 255), (250, 300))
        self.screen = pygame.display.set_mode((500, 500))
        self.img_surf = pygame.image.load(
            "images/game_background.png").convert_alpha()
        self.img_surf = pygame.transform.scale(self.img_surf, (500, 500))
        self.running = True
        while self.running:
            self.update()

    def update(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                # if the user quits
                if event.type == pygame.QUIT or event.key == K_ESCAPE:
                    self.running = False
        if pygame.mouse.get_pressed()[0] == 1:
            mouse = pygame.mouse.get_pos()
            # If the user left clicks on the button the game class from the main.py file is called and this
            # pygame is quit
            if self.continue_button.rect.collidepoint(mouse):
                Menu()
                pygame.quit()
        self.screen.blit(self.img_surf, [0, 0])
        self.screen.blit(self.died_button.surf, self.died_button.rect)
        self.screen.blit(self.continue_button.surf, self.continue_button.rect)
        pygame.display.flip()

    pygame.quit()


class End:
    def __init__(self, score):
        pygame.init()

        # Adds the text
        font = pygame.font.Font('freesansbold.ttf', 32)
        self.text = font.render('Score: ' + str(score), True, (0, 255, 0))
        self.textRect = self.text.get_rect()
        # set the center of the rectangular object.
        self.textRect.center = (425, 25)


        self.died_button = Button("freesansbold.ttf", 40, "You Died!",
                                  (255, 255, 255), (250, 125))
        self.continue_button = Button("freesansbold.ttf", 40, "Continue?",
                                      (255, 255, 255), (250, 300))
        self.screen = pygame.display.set_mode((500, 500))
        self.img_surf = pygame.image.load(
            "images/game_background.png").convert_alpha()
        self.img_surf = pygame.transform.scale(self.img_surf, (500, 500))
        self.running = True
        while self.running:
            self.update()

    def update(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                # if the user quits
                if event.type == pygame.QUIT or event.key == K_ESCAPE:
                    self.running = False
        if pygame.mouse.get_pressed()[0] == 1:
            mouse = pygame.mouse.get_pos()
            # If the user left clicks on the button the game class from the main.py file is called and this
            # pygame is quit
            if self.continue_button.rect.collidepoint(mouse):
                Menu()
                pygame.quit()
        self.screen.blit(self.img_surf, [0, 0])
        self.screen.blit(self.died_button.surf, self.died_button.rect)
        self.screen.blit(self.continue_button.surf, self.continue_button.rect)
        self.screen.blit(self.text, self.textRect)
        pygame.display.flip()


if __name__ == "__main__":
    Menu()

