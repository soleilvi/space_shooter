# Tutorial followed: https://www.youtube.com/watch?v=Q-__8Xw9KTM&t=1265s
# bdy_venv\Scripts\activate.bat
# Laser there = bullet here
import pygame
import os
import time
import random
pygame.font.init()

# LOAD PYGAME
WIDTH, HEIGHT = 700, 800  # *2
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Space shooter')

# LOAD IMAGES
BACKGROUND = pygame.transform.scale(
             pygame.image.load(os.path.join('images', 'background.png')),
             (WIDTH, HEIGHT))

SPACESHIP_BADSIZE = pygame.image.load(os.path.join('images', 'spaceship.png'))
SPACESHIP_W = SPACESHIP_BADSIZE.get_width()
SPACESHIP_H = SPACESHIP_BADSIZE.get_height()

SPACESHIP = pygame.transform.scale(SPACESHIP_BADSIZE,
                                   (int(SPACESHIP_W * 0.8),
                                   int(SPACESHIP_H * 0.8)))

ALIEN = pygame.image.load(os.path.join('images', 'alien.png'))
PALIEN = pygame.image.load(os.path.join('images', 'palien.png'))
RALIEN = pygame.image.load(os.path.join('images', 'ralien.png'))
YALIEN = pygame.image.load(os.path.join('images', 'yalien.png'))

PLAYER_BULLET = pygame.image.load(os.path.join('images', 'wullet.png'))
ALIEN_BULLET = pygame.image.load(os.path.join('images', 'bullet.png'))
PALIEN_BULLET = pygame.image.load(os.path.join('images', 'pullet.png'))
RALIEN_BULLET = pygame.image.load(os.path.join('images', 'rullet.png'))
TRANSPARENT_IMG = pygame.image.load(os.path.join('images', 'transparent.png'))

MUSIC_FILE = pygame.image.load(os.path.join('images', 'music_file.png'))
ART_FILE = pygame.image.load(os.path.join('images', 'art_file.png'))
POEM_FILE = pygame.image.load(os.path.join('images', 'poem_file.png'))
CARD_FILE = pygame.image.load(os.path.join('images', 'card_file.png'))

# ALIEN GLOW GLOBALS (it didn't work otherwise)
glow_switch = False
g_num = 240


# INITIATING CLASSES
class Ship:  # *4
    COOLDOWN = 25  # 5/12th of a second

    def __init__(self, x, y, health=100):
        # x and y are not the width and height, but the coordinates
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None  # *5
        self.bullet_img = None
        self.bullets = []
        # Prevents the user from spamming bullets:
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for bullet in self.bullets:
            bullet.draw(window)

    def cooldown(self):
        '''Have the counter count up until it reaches the cooldown time.'''
        if self.cool_down_counter >= self.COOLDOWN: self.cool_down_counter = 0
        elif self.cool_down_counter > 0: self.cool_down_counter += 1

    def shoot(self, y):
        '''
        If the bullets aren't in the process of cooling down, then initiate the
        bullets and start the cool down timer.
        '''
        if self.cool_down_counter == 0:
            bullet = Bullet(self.x + (self.width() / 2), y,
                            self.bullet_img)
            self.bullets.append(bullet)
            # Start counting up
            self.cool_down_counter = 1

    def width(self):
        return self.ship_img.get_width()

    def height(self):
        return self.ship_img.get_height()


class Player(Ship): # *6
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)  # *7
        self.ship_img = SPACESHIP
        self.bullet_img = PLAYER_BULLET

        # Masking prevents the hitbox from being square (molds it to the
        # image)
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_bullets(self, objs, lvl):  # *12, where objs = enemies (DON'T FORGET TO ADD A LEVEL ARGUMENT)
        '''
        Move the bullets while checking if they're off-screen or if they have
        collided with the player.
        '''
        self.cooldown()
        for bullet in self.bullets:
            bullet.move(-5)  # *11
            if bullet.off_screen(HEIGHT):
                self.bullets.remove(bullet)
            else:
                for obj in objs:
                    if bullet.collision(obj):
                        # Check if the obj is a FileEnemy class instance
                        if isinstance(obj, FileEnemy):
                            if lvl < 5:
                                global file
                                FILE_ICON = {1: POEM_FILE,
                                             2: CARD_FILE,
                                             3: ART_FILE,
                                             4: MUSIC_FILE}

                                # File is now visible
                                file = File(obj.x + (obj.width() / 2),
                                        obj.y + (obj.height() / 2),
                                        FILE_ICON[lvl])
                        objs.remove(obj)

                        # Make sure the bullet is in the list before
                        # removing it
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)

                    # Check if bullets have collided
                    for obj_bullet in obj.bullets:
                        if bullet.collision(obj_bullet):
                            if obj_bullet in obj.bullets:
                                obj.bullets.remove(obj_bullet)
                            if bullet in self.bullets:
                                self.bullets.remove(bullet)

    def draw(self, window):
        super().draw(window)
        # Attach the health bar to the player
        self.health_bar(window)

    def health_bar(self, window):
        # Red bar
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.height() + 5,
                         self.width(), 10))
        # Green bar
        pygame.draw.rect(window, (0, 255, 0),
                         (self.x, self.y + self.height() + 5,
                         self.width() * (self.health / self.max_health), 10))


class Enemy(Ship):
    ENEMY_VEL = 1
    BULLET_VEL = 5

    TYPE_REF = {'alien': (ALIEN, ALIEN_BULLET, ENEMY_VEL, BULLET_VEL),
                'palien': (PALIEN, PALIEN_BULLET, ENEMY_VEL, BULLET_VEL + 2),
                'ralien': (RALIEN, RALIEN_BULLET, ENEMY_VEL, BULLET_VEL + 2),
                'yalien': (YALIEN, TRANSPARENT_IMG, ENEMY_VEL + 3, BULLET_VEL)}

    def __init__(self, x, y, type, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.bullet_img, self.vel, self.bullet_vel = self.TYPE_REF[type]  # *8
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self):
        '''
        Makes the enemy move down the screen according to a velocity passed.
        '''
        self.y += self.vel

    # Placer for the num passed to glow() in FileEnemy
    def draw(self, window, placer=None):
        super().draw(window)

    def move_bullets(self, obj):  # Where obj is the player
        '''
        Move the bullets while checking if they're off-screen or if they have
        collided with something (that isn't the enemies).
        '''
        # Cooldown: check if you can send another bullet
        self.cooldown()
        for bullet in self.bullets:
            bullet.move(self.bullet_vel)  # *11
            if bullet.off_screen(HEIGHT):
                self.bullets.remove(bullet)
            elif bullet.collision(obj):
                obj.health -= 10
                self.bullets.remove(bullet)


class FileEnemy(Enemy):
    '''
    Class for the special enemy carrying the file. It is like the regular
    enemy class, but it allows the aliens to glow and drop an item after you
    kill them.
    '''
    def __init__(self, x, y, type, health=100):
        super().__init__(x, y, type, health)

    def draw(self, window, num):
        super().draw(window)
        self.glow(window, num)

    def glow(self, window, num):
        RECT = pygame.Surface((self.width(), self.height()))
        RECT.fill((248, 248, 2))
        RECT.set_alpha(num)
        window.blit(RECT, (self.x, self.y))


class File:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def if_collected(self, player):
        '''
        Turns the image transparent and downloads the file it carried.
        '''
        if collide(player, self):
            self.img = TRANSPARENT_IMG
            return True  # level change?


class Bullet:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x - (self.img.get_width() / 2),
                               self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        '''Return False if the bullet is on the screen and True if it's off.'''
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        # Returns the "return" of the collide function (I think, this was
        # from the tutorial).
        return collide(obj, self)


# INITIATING FUNCTIONS
def collide(obj1, obj2):
    '''
    Returns true or false based on wheter the pixels of two objects (not just
    their hitboxes) are colliding.
    '''
    offset_x = int(obj2.x - obj1.x)
    offset_y = int(obj2.y - obj1.y)

    # if they are not overlapping, return None. Else, return a (x, y) tuple."
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def instructions_window():
    '''Make a similar interface as the one you made for your AP CS project'''
    INSTRUCTIONS_FONT = pygame.font.SysFont('comicsans', 50)
    run = True

    while run:
        WIN.blit(BACKGROUND, (0, 0))
        INSTRUCTIONS = INSTRUCTIONS_FONT.render('Here are some instructions, ' \
                                                'peepee poopoo', 1,
                                                (255, 255, 255))
        WIN.blit(INSTRUCTIONS, (0, HEIGHT / 2))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONDOWN:
                run = False


# Defined outside of the function because it needs to be global in order to
# change the image in player.move_bullets()
file = File(0, 0, TRANSPARENT_IMG)
def main():
    '''
    60x every second, loop through all the events that pygame knows and check
    if something has occurred.
    '''
    run = True
    FPS = 60
    level = 0
    lives = 3

    main_font = pygame.font.SysFont('comicsans', 40)
    lost_font = pygame.font.SysFont('comicsans', 80)

    you_lost = False
    lost_count = 0

    player = Player((WIDTH / 2) - (SPACESHIP_W / 2),
                    HEIGHT - (SPACESHIP_H * 1.15))  # Where it will spawn
    PLAYER_VEL = 5
    BULLET_VEL = 5

    SPAWN_LENGTH = 4  # How many more enemies spawn when the level increases
    wave_length = 6  # Enemy num that will be added to SPAWN_LENGTH @ beginning
    enemies = []

    clock = pygame.time.Clock()  # Prevents the program from running at a \
    # different rate on another device


    def change_num():
        global g_num
        global glow_switch

        if glow_switch is False:
            g_num -=4
            if g_num == -4:
                glow_switch = True
        elif glow_switch is True:
            g_num += 4
            if g_num == 240:
                glow_switch = False


    def redraw_window():  # *1
        '''
        Draws everything into the screen. Repeated 60x every second because
        it's on the while loop.
        '''

        WIN.blit(BACKGROUND, (0, 0))

        # Drawing labels
        level_label = main_font.render(f'Level: {level}', 1, (255, 255, 255))
        lives_label = main_font.render(f'Lives: {lives}', 1, (255, 255, 255))
        WIN.blit(level_label, (15, 10))
        WIN.blit(lives_label, (WIDTH - level_label.get_width() - 15, 10))  # *3

        for enemy in enemies:
            enemy.draw(WIN, g_num)

        # The file is always drawn because it would be a pain to make it
        # appear if we draw it in the FileEnemy draw() method
        file.draw(WIN)
        player.draw(WIN)

        if you_lost:
            lost_label = lost_font.render('GAME OVER', 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()


    # POLISH: FIX REDUNDANCY IN THESE FUNCTIONS LATER
    def create_enemy(multiple, type1, *more_types):
        type_list = [type1]

        for type in more_types:  # Non-pythonic???
            type_list.append(type)

        if multiple < 4:
            if wave_length == (multiple * SPAWN_LENGTH) + 6:
                enemy = Enemy(random.randrange(20, WIDTH - 20),
                              random.randrange(-1500, -100),
                              random.choice(type_list))
        else:
            if wave_length >= (multiple * SPAWN_LENGTH) + 6:
                enemy = Enemy(random.randrange(20, WIDTH - 20),
                              random.randrange(-1500, -100),
                              random.choice(type_list))
        try:
            enemies.append(enemy)
        # Error happens because "enemy" wouldn't be defined if the "if"
        # statements were false.
        except UnboundLocalError:
            pass


    # Redundant?
    def create_file_enemy(multiple, type1, *more_types):
        type_list = [type1]

        for type in more_types:
            type_list.append(type)

        if multiple < 4:
            if wave_length == (multiple * SPAWN_LENGTH) + 6:
                enemy = FileEnemy(random.randrange(20, WIDTH - 20),
                              random.randrange(-1500, -100),
                              random.choice(type_list))
        else:
            if wave_length >= (multiple * SPAWN_LENGTH) + 6:
                enemy = FileEnemy(random.randrange(20, WIDTH - 20),
                              random.randrange(-1500, -100),
                              random.choice(type_list))
        try:
            enemies.append(enemy)
        except UnboundLocalError:
            pass


    while run:
        clock.tick(FPS)
        change_num()
        redraw_window()

        if lives <= 0 or player.health <=0:
            you_lost = True
            lost_count += 1

        if you_lost:
            if lost_count > FPS * 3:  # Sets a 3-second timer. \
                # Lost count = 181 when it ends the program.
                run = False
            else:
                continue  # *10

        # Next wave once all enemies are killed
        if len(enemies) == 0:
            # if file.if_collected(player):
            #     level += 1
            level += 1
            wave_length += SPAWN_LENGTH

            # Spawns the enemies according to the wave length value.
            # -1 because of the special alien we are appending to the list.
            for i in range(wave_length - 1):
                # I wonder if calling in the funcitons repeatedly here makes
                # it take longer than if it were just the raw if-elif
                # statements...
                create_enemy(1, 'alien')
                create_enemy(2, 'alien', 'palien')
                create_enemy(3, 'alien', 'palien', 'ralien')
                create_enemy(4, 'alien', 'palien', 'ralien', 'yalien')

            create_file_enemy(1, 'alien')
            create_file_enemy(2, 'alien', 'palien')
            create_file_enemy(3, 'alien', 'palien', 'ralien')
            create_file_enemy(4, 'alien', 'palien', 'ralien', 'yalien')

        for event in pygame.event.get():
            # If 'X' button pressed (window)
            if event.type == pygame.QUIT:
                quit()

        # Outside of the for loop since that would only make the ship move once
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            # Don't let the player go out of the screen
            if player.x + (player.width() / 2) > 0:
                player.x -= PLAYER_VEL

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            if player.x + (player.width() / 2) < WIDTH:
                player.x += PLAYER_VEL

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            if player.y + (player.height() / 2) < HEIGHT:
                player.y += PLAYER_VEL

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            if player.y > 0:
                player.y -= PLAYER_VEL
        if keys[pygame.K_SPACE]:
            player.shoot(player.y)

        # Moves the enemies downward
        for enemy in enemies[:]:  # *9
            enemy.move()
            enemy.move_bullets(player)

            if random.randrange(0, 3*60) == 1:  # Probability of 1/3 every sec.
                enemy.shoot(enemy.y + enemy.height())

            # -1 life if the enemies reach the bottom of the screen
            if enemy.y + enemy.height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
                '''
                The wave_length (according to the level) is supposed to reset
                here if the class of the enemy is FileEnemy.
                '''

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
                '''
                Display a game_over if the class of the enemy is FileEnemy.
                '''

        file.if_collected(player)
        player.move_bullets(enemies, level)


def main_menu():
    '''Need to create two buttons and a title (pull in an image?)'''
    TITLE_IMAGE = pygame.image.load(os.path.join('images', 'pg_title.png'))
    START_BUTTON = pygame.image.load(os.path.join('images',
                                                  'start_button.png'))
    INSTRUCTIONS_BUTTON = pygame.image.load(os.path.join
                                           ('images',
                                            'instructions_button.png'))

    START_RECT = START_BUTTON.get_rect()
    INSTRUCTIONS_RECT = INSTRUCTIONS_BUTTON.get_rect()
    START_RECT.center = (WIDTH / 2, 400)  # x & y of the start button
    INSTRUCTIONS_RECT.center = (WIDTH / 2, 590)

    run = True

    while run:
        WIN.blit(BACKGROUND, (0, 0))
        WIN.blit(TITLE_IMAGE, ((WIDTH / 2) - (TITLE_IMAGE.get_width() / 2),
                               100))
        WIN.blit(START_BUTTON, START_RECT)
        WIN.blit(INSTRUCTIONS_BUTTON, INSTRUCTIONS_RECT)

        pygame.display.update()

        mouse_position = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if START_RECT.collidepoint(mouse_position):
                    main()
                elif INSTRUCTIONS_RECT.collidepoint(mouse_position):
                    instructions_window()

    quit()


# CALLING FUNCTIONS
main_menu()

# -----------------------------------------------------------------------------
'''
INCORPORATE:
Programming:
- Have random aliens in each wave carry a random item (file) and drop it once
  you kill them (DONE)
    - They re-spawn (or another alien carries the key) if you don't kill them
      before they get to the bottom of the screen/they hit you
    - The level repeats if they get to the bottom of the screen
    - Have no more aliens appear if you haven't picked up the item dropped
        - Easter egg: have a message appear telling you to hurry up if you
          take longer than 20 seconds in that state
    - The game ends if they touch you ;)
- RESTRICT THE GLOW TO THE NON-ALPHA VALUES OF THE IMAGES GODDAMMIT
- Put the yaliens in a different list with a wider range (and decreased
  spawning probability?)
- Death animations (explosions?)
- Winning screen
    - Cap at level 5
- Sounds and stuff, idk
    - Bullets
    - Enemy down
    - Level up
    - Enemy got through
- Pause button
- Animation stuff

Design:
- Improve start screen
- Improve "game over" screen
- Make it look more 8-bit?
- Make a yellow outline for each alien (for the glow )
    - Also add it to the dictionary
- Actually write the instructions lmao

DONE:
- Make bullets collide with each other
- Make different types of aliens come out as the waves increase
- Give the aliens different abilities
    - 1: nothing
    - 2: shoots faster bullets
    - 3: shoots 'em thicc OWO (maybe also faster?)
    - 4: Moves super fast (but doesn't shoot anything)
- Instructions (coding the screen change)
- Special aliens glow
    1. Make the glow
    2. Have other aliens (apart from the green one) have the glow

-------------------------------------------------------------------------------

WHAT I'VE LEARNED:
- *1: Defining functions inside of other functions can allow you to use the
      variables defined in that function without having to make them all global
      or using many parameters
- *2: Some variable names are in caps because they're constants (it's a python
      convention to name constants in caps)
- *3: Better to do it this way becasue then you can change the size of the
      window and the elements plotted would still stay in the desired place.
- *4: Abstract class: classes that you mainly just use to inherit from them
      later. They don't define a single thing, but rather multiple items of the
      same type (I think?? Look them up later :') ).
- *5: None type allows us to initiate variables without assigning a real value
      to them. Here, wer're initiating them so that we may attach the ships'
      corresponding images to them later.
- *6: Class inheriting: initializes another existing class and allows you to
      use methods from the class you're initializing.
- *7: Super() references the parent class Ship, and putting __init__ after it
      allows you to call everything that was defined in the Ship __init__
      method into your other class (minimizes redundancy).
- *8: Use dictionaries to reduce the complexity of your code (notice how tuples
      are also used in the dictionary so that less parameters would be needed)
- *9: '[:]' Makes a copy of the original list
- *10: "continue" keyword makes a for-loop or while-loop skip anything inside
       the loop that comes after the keyword (it's a bit like a mix between
       "break" and "pass"). In this situation, it makes it seem like the
       program froze in place while the "Game Over" screen is up.
- *11: Ok wait, I don't fucking understand why the methods from a child class
       are working in the parent class :'D blease exblanei
- *12: Defining a method with the same name as a method in the parent class
       overrides the method in the parent class.
'''
