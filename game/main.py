import random
import sys

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
        """This function changes the text of the button"""
        self.text = text
        self.surf = self.font.render(self.text, False, self.color)
        # Changes the center of the text depending on how long it is
        # (This function is only used for the mode settings in the main menu
        # and if I had more time I would fix this up to be less sloppy and hardcodded)
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
        """
        This function:
         - Checks for collisions with platforms (on ground)
         - Applies gravity to player
         - Sees if player can/should jump
        """
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

    # Jump function
    def jump(self):
        self.vel[1] = -10
        self.on_ground = False

    # Gravity function
    def gravity(self):
        self.vel[1] += .7

    # Collision detector
    def ground_collision_detector(self, platform_group):
        """This function checks if the player collides with platforms:
        Note: If it hits either side of the platform or the bottom it dies
        """
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
        """
        This function checks the mode and adds the appropriate features accordingly
        """
        # This is the mode which will effect how the game is player
        # There are 3 modes: AI Only (0), Player Only (1), Player and AI (2)
        # The mode is just one of the numbers listed above: 0, 1, or 2
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

        # Checks the mode to see what needs to be in the game
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
            # Checks what mode the game should be played in and updates accordingly
            if mode == 0:
                self.mode1_update()
            elif mode == 1:
                self.mode2_update()
            elif mode == 2:
                self.mode3_update()

            # Checks if it's not the AI only mode and if the player is dead to move on to the end screen
            if mode != 0 and self.player.dead:
                End(self.score)

    def update_score(self):
        """This function updates the score of the Player/AI"""
        # Adds 1 to the score when called (called every frame)
        self.score += 1
        font = pygame.font.Font('freesansbold.ttf', 32)
        # Sets the text to the updated score
        text = font.render('Score: ' + str(self.score), True, (0, 255, 0))

        textRect = text.get_rect()

        # set the center of the rectangular object.
        textRect.center = (250, 100)
        # Adds the text to the screen
        self.screen.blit(text, textRect)

    def check_distance(self, obj1, obj2):
        """This function returns a tuple (x, y)
        of the distance between two objects"""
        return obj2.rect.centerx - obj1.rect.centerx, obj2.rect.y - obj1.rect.y

    def manage_obstacle_delay(self, spike_delay=61, platform_delay=60,
                              random_platforms=False):
        # Lowers the spike and platform delay by 1 every frame
        # Basically a countdown for when the next spike/platform should come
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
        """This function takes in delta time (dt) to keep a constant rate of the game even if you lose frames"""
        # Updates every platform in the platform group (except the ground)
        for platform in self.platforms:
            if platform != self.ground:
                # moves platforms with dt
                platform.update(dt)

        # Updates every spike and checks for collisions with player
        for spike in self.spikes:
            # moves spikes with dt
            spike.update(dt)

    def mode1_update(self):
        """This function is run every frame of the game and returns nothing"""
        """This mode of the game is AI ONLY"""
        # Sets delta time to the clock tick (will help catch up if application lags)
        dt = self.clock.tick(30)

        # Checks if there are two or more obstacles coming towards the AI
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
                    # A little overkill on quitting the game perhaps
                    # but everything is stopped
                    self.running = False
                    pygame.quit()
                    # More of a brute force method because there was a problem
                    # with the pygame.font (Still not sure why)
                    sys.exit()
                    return

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
        """This mode is PLAYER ONLY"""
        # Sets delta time to the clock tick (will help catch up if application lags)
        dt = self.clock.tick(30)

        # Manages everything to do with the obstacle delay (check function for more details)
        self.manage_obstacle_delay(random.randint(20, 50),
                                   random.randint(45, 100), True)

        # Checks if player has clicked any keys to end the game
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.type == QUIT:
                    # A little overkill on quitting the game perhaps
                    # but everything is stopped
                    self.running = False
                    pygame.quit()
                    # More of a brute force method because there was a problem
                    # with the pygame.font (Still not sure why)
                    sys.exit()
                    return
                if event.key == K_SPACE:
                    self.space = True

        # Updates obstacles
        self.update_obstacles(dt)

        # Checks if player has collided with a spike
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
        """This mode is for PLAYER AND AI"""
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
                    # A little overkill on quitting the game perhaps
                    # but everything is stopped
                    self.running = False
                    pygame.quit()
                    # More of a brute force method because there was a problem
                    # with the pygame.font (Still not sure why)
                    sys.exit()
                    return
                if event.key == K_SPACE:
                    player_jump = True

        # Updates the obstacles
        self.update_obstacles(dt)

        # If the user collides with spikes, it gets set to dead
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
        self.screen = pygame.display.set_mode((500, 500))
        # Makes the modes
        self.modes = ["AI Only", "Player Only", "AI and Player"]
        # Makes button objects
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
        """This function runs every frame while this screen is on and returns nothing"""
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
                    pygame.quit()
                    sys.exit()
                    return
            # Checks if user is clicking down mouse
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Checks if user clicked on start_button
                if self.start_button.rect.collidepoint(event.pos):
                    self.running = False
                    Game(self.modes.index(self.mode_button.text))
                    return
                # Checks if user clicked on mode_button (to change the mode)
                elif self.mode_button.rect.collidepoint(event.pos) and self.click_delay < 0:
                    # Click delay since it will rapid fire click otherwise
                    self.click_delay = 30
                    try:
                        # Will try and go to next mode in list
                        self.mode_button.set_text(
                            self.modes[
                                self.modes.index(self.mode_button.text) + 1])
                    except IndexError:
                        # If there is no more modes it will reset back to the first mode
                        self.mode_button.set_text(self.modes[0])
            # If the user left clicks on the button the game class is called and this pygame is quit
            # Changes the mode and blits the text onto the screen
        # Updates visuals of screen
        pygame.display.flip()


class End:
    def __init__(self, score):
        # Adds the text
        font = pygame.font.Font('freesansbold.ttf', 32)
        # Addes the score to the screen
        self.text = font.render('Score: ' + str(score), True, (0, 255, 0))
        self.textRect = self.text.get_rect()
        # set the center of the rectangular object.
        # Moves the score over to the left more the higher the number is
        self.textRect.center = (425 - (len(str(score)) * 10), 25)

        # Adds dead text
        self.dead_text = font.render('You Died!', True, (255, 255, 255))
        self.dead_textRect = self.dead_text.get_rect()
        self.dead_textRect.center = (250, 125)

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
        """This function runs every frame while this screen is on and returns nothing"""
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                # if the user quits
                if event.type == pygame.QUIT or event.key == K_ESCAPE:
                    self.running = False
                    pygame.quit()
                    sys.exit()
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Checks if user clicks continue button
                if self.continue_button.rect.collidepoint(event.pos):
                    self.running = False
                    # Runs menu
                    Menu()
                    return

        # Puts background, buttons, and text on screen
        self.screen.blit(self.img_surf, [0, 0])
        self.screen.blit(self.dead_text, self.dead_textRect)
        self.screen.blit(self.continue_button.surf, self.continue_button.rect)
        self.screen.blit(self.text, self.textRect)
        # Shows the new screen
        pygame.display.flip()


if __name__ == "__main__":
    # Initializes pygame
    pygame.init()
    # Runs __init__ of menu class
    Menu()

