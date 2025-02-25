import sys,pygame
from os.path import join
from random import randint, uniform

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('assets/images', 'player.png')).convert_alpha()
        self.rect = self.image.get_frect(center = (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2))
        self.direction = pygame.math.Vector2(0,0)
        self.speed = 300

        # Cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cd_duration = 400

        # Mask
        self.mask = pygame.mask.from_surface(self.image)
    
    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cd_duration:
                self.can_shoot = True
                self.laser_shoot_time = current_time
    
    def update(self, dt):
        # Movement 
        self.rect.center += self.direction * self.speed * dt

        # Input
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        self.direction =  self.direction.normalize() if self.direction else self.direction
        
        # Press Once
        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf,self.rect.midtop, (all_sprite, laser_sprite))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()

        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, star_surf):
        super().__init__(groups)
        self.image = star_surf
        self.rect = self.image.get_frect(center = (randint(0,DISPLAY_WIDTH), randint(0, DISPLAY_HEIGHT)))

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)
        self.mask = pygame.mask.from_surface(self.image)
    
    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_surface = surf
        self.image = self.original_surface
        self.rect = self.image.get_frect(center = pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.start_time = pygame.time.get_ticks()
        self.pause_time = 0
        self.lifetime = 3000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(400, 500)
        self.rotation = 0
        self.image = pygame.transform.grayscale(self.image)
    
    def update(self, dt):
        # Meteor Movement
        self.rect.center += self.direction * self.speed * dt

        if self.rect.centery >= DISPLAY_HEIGHT:
            self.kill()

        # Rotation
        self.rotation += 100 * dt
        self.image = pygame.transform.rotozoom(self.original_surface, self.rotation, 1)
        self.rect = self.image.get_frect(center=self.rect.center)

class AnimatedExplosion (pygame.sprite.Sprite):
    def __init__ (self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)
    
    def update(self, dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index) % len(self.frames)]
        else:
            self.kill()

# Functions
def collision(): 
    global running

    # Player and Meteor Collision
    player_collision = pygame.sprite.spritecollide(player,meteor_sprite, True, pygame.sprite.collide_mask)
    if player_collision:
        running = False
     
     # Laser and Meteor Collision
    for laser in laser_sprite: 
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprite, True, pygame.sprite.collide_mask)
        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprite)
            explosion_sound.play()

def display_distance():
    global paused_time, paused_duration, distance

    current_time = pygame.time.get_ticks()  # Get the current game time (in milliseconds)

    if menu_mode:
        if paused_time is None: # This Ensures that the paused time is not updating even on menu mode
            paused_time = current_time  # Stores the time when the game was paused.
        elapsed_time = paused_time - paused_duration
    else:
        if paused_time is not None:  # If game was paused
            paused_duration += current_time - paused_time  # Calculate the total pause duration
            paused_time = None  # Reset the pause time to None after resuming
        elapsed_time = current_time - paused_duration
    
    distance = elapsed_time // 50

    # Display the time
    text_surf = font.render(f'{str(distance)}m', True, (240, 240, 240))
    text_rect = text_surf.get_frect(midbottom=(DISPLAY_WIDTH / 2, DISPLAY_HEIGHT - 50))
    display_window.blit(text_surf, text_rect)
    pygame.draw.rect(display_window, 'white', text_rect.inflate(20, 16).move(0, -5), 5, 10)

def menu():
    global menu_mode, music_counter, music_state, music_str

    display_window.fill('Black')

    if pygame.mouse.get_just_pressed()[0] and resume_txtrect.collidepoint(pygame.mouse.get_pos()):
        print('Menu Exit')
        menu_mode = False
    if pygame.mouse.get_just_pressed()[0] and sound_txtrect.collidepoint(pygame.mouse.get_pos()):
        if music_counter >= len(music_sound) - 1:
            music_counter = 0
        else:
            music_counter += 1

        laser_sound.set_volume(music_sound[music_counter])
        explosion_sound.set_volume(music_sound[music_counter])
        game_music.set_volume(music_sound[music_counter])
        laser_sound.play()
    if pygame.mouse.get_just_pressed()[0] and music_txtrect.collidepoint(pygame.mouse.get_pos()):
        music_state *= -1

        if music_state == 1:
            music_str = 'ON'
            game_music.set_volume(music_sound[music_counter])
            game_music.play()
        else:
            music_str = 'OFF'
            game_music.stop()


    volume_surf = menu_font.render(f'{music_percent[music_counter]}', True, 'white')    
    musicset_surf = menu_font.render(music_str, True, 'white')    
    display_window.blit(resume_txtsurf,resume_txtrect)
    display_window.blit(sound_surf, sound_txtrect)
    display_window.blit(music_surf, music_txtrect)
    display_window.blit(volume_surf, (DISPLAY_WIDTH / 2 + 35, DISPLAY_HEIGHT / 2 - 10))
    display_window.blit(musicset_surf, (music_txtrect.centerx + 65, music_txtrect.centery - 20))


# Setup
pygame.init()
DISPLAY_WIDTH, DISPLAY_HEIGHT, = 1280 , 720
display_window = pygame.display.set_mode((DISPLAY_WIDTH,DISPLAY_HEIGHT))
pygame.display.set_caption('Space Shooter')
running = True
menu_mode = False
clock = pygame.time.Clock()

# Import 
star_surf = pygame.image.load(join('assets/images', 'star.png')).convert_alpha()
meteor_surf = pygame.image.load(join('assets/images', 'meteor.png')).convert_alpha()
laser_surf = pygame.image.load(join('assets/images', 'laser.png')).convert_alpha()
font = pygame.font.Font(join('assets/images', 'Oxanium-Bold.ttf'), 20)
menu_font = pygame.font.Font(join('assets/images', 'Oxanium-Bold.ttf'), 30)
explosion_frames = [pygame.image.load(join('assets/images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]

laser_sound = pygame.mixer.Sound(join('assets/audio', 'laser.wav'))
explosion_sound = pygame.mixer.Sound(join('assets/audio', 'explosion.wav'))
damage_sound = pygame.mixer.Sound(join('assets/audio', 'damage.ogg'))
game_music = pygame.mixer.Sound(join('assets/audio', 'game_music.wav'))

# Pre Render Menu Text
resume_txtsurf = menu_font.render('Resume', True, 'white')
resume_txtrect = resume_txtsurf.get_frect(center = (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2 - 40))
sound_surf = menu_font.render('Sound :', True, 'white')
sound_txtrect = sound_surf.get_frect(center = (DISPLAY_WIDTH / 2 - 30, DISPLAY_HEIGHT / 2 + 10))
music_surf = menu_font.render('Music  :', True, 'white')
music_txtrect = music_surf.get_frect(center = (DISPLAY_WIDTH / 2 - 32, DISPLAY_HEIGHT / 2 + 60))


# Instanciate Class
all_sprite = pygame.sprite.Group()
laser_sprite = pygame.sprite.Group()
meteor_sprite = pygame.sprite.Group()
for i in range(20):
    Star(all_sprite, star_surf)
player = Player(all_sprite) 

# Game States
music_sound = [0.1,0.5,0.7,1]
music_percent = [25, 50, 75, 100]
music_counter = 1
music_state = 1
music_str = 'ON'
paused_time = None
paused_duration = 0
distance = 0
meteor_spawn_timer = 500
game_music.set_volume(music_sound[music_counter])
laser_sound.set_volume(music_sound[music_counter])
explosion_sound.set_volume(music_sound[music_counter])
game_music.play()


# Meteor Event
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event,500)

while running:
    dt = clock.tick() / 1000
    # Event Handler 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event and not menu_mode:
            Meteor(meteor_surf, (randint(0,1200), 0), (all_sprite, meteor_sprite))
            #print('Create Meteor')
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                menu_mode = True
                print('Menu Mode: On')

    display_window.fill('#3a2a3f')

    if menu_mode:
        all_sprite.draw(display_window)
        display_distance()
        menu()
    else:
        collision()
        all_sprite.update(dt)   
        display_distance()
        all_sprite.draw(display_window)

    pygame.display.update()


pygame.quit()
 