from settings import *

class GUI():
    def __init__(self):
        self.image = None
        self.image_index = 0
        self.rect = None

        self.is_active = False
    
    def _load_animation_frames(self, base_path):
        sprite_images = []
        sprite_image_directory = os.listdir(os.path.join(base_path))

        for image in sprite_image_directory:
            image_surface = pygame.image.load(os.path.join(base_path, image))
            sprite_images.append(image_surface)
        
        return sprite_images

class GUIManager():
    def __init__(self):
        # Buttons
        self.BUTTON_setting = Button('SettingIcon', (990,45))
        self.BUTTON_continue = Button('ContinueIcon', (1024 // 2,500 // 2), (200,100))
        self.BUTTON_mainmenu = Button('MainMenuIcon', (1024 // 2,700 // 2), (200,100))
        self.BUTTON_restart = Button('RestartIcon', (1024 // 2,900 // 2), (200,100))

        self.mainmenu_surface = pygame.image.load(os.path.join('assets', 'GUI', 'MenuSurface.png'))
        self.mainmenu_surface = pygame.transform.scale(self.mainmenu_surface, (1024,768))
        self.mainmenu_rect = self.mainmenu_surface.get_frect(center = (1024 // 2,768 // 2))
        self.is_mainmenu_active = False

        self.healthbar_status = 'Full'
        self.healthbar_surface = {
            'Full':pygame.image.load(os.path.join('assets', 'GUI', 'HealthBar', 'Full.png')),
            'Half':pygame.image.load(os.path.join('assets', 'GUI', 'HealthBar', 'Half.png')),
            'Low': pygame.image.load(os.path.join('assets', 'GUI', 'HealthBar', 'Low.png')),
            'Empty':pygame.image.load(os.path.join('assets', 'GUI', 'HealthBar', 'Empty.png'))
        }
        self.healthbar_surface[self.healthbar_status] = pygame.transform.scale(self.healthbar_surface[self.healthbar_status], (250,80))
        self.healthbar_rect = self.healthbar_surface[self.healthbar_status].get_frect(topleft = (10,10))

        self.level_status = 0
        self.level_surface = {
            0 : pygame.image.load(os.path.join('assets', 'GUI', 'LevelIcon', 'LVL0','1.png'))
        }
        self.level_surface[self.level_status] = pygame.transform.scale(self.level_surface[self.level_status], (150, 45))
        self.level_rect = self.level_surface[self.level_status].get_frect(center = (1024 // 2,55))

    def _handle_gui_inputs(self):
        mouse_click = pygame.mouse.get_pressed()
        mouse_just_clicked = pygame.mouse.get_just_pressed()
        mouse_pos = pygame.mouse.get_pos()

        self.BUTTON_setting.handle_events(mouse_pos, mouse_click, mouse_just_clicked)
        if self.is_mainmenu_active:
            self.BUTTON_mainmenu.handle_events(mouse_pos, mouse_click, mouse_just_clicked)
            self.BUTTON_restart.handle_events(mouse_pos, mouse_click, mouse_just_clicked)
            self.BUTTON_continue.handle_events(mouse_pos, mouse_click, mouse_just_clicked)

    def _handle_active_state(self):
        print(f'Settings: {self.BUTTON_setting.get_active_state()}')
        if self.BUTTON_setting.get_active_state():
            self.is_mainmenu_active = True
        else:
            self.is_mainmenu_active = False

    def handle_gui(self, screen_surface):
        self._handle_gui_inputs()
        self._handle_active_state()

        screen_surface.blit(self.healthbar_surface[self.healthbar_status], self.healthbar_rect)
        screen_surface.blit(self.level_surface[self.level_status], self.level_rect)
        screen_surface.blit(self.BUTTON_setting.get_surface(), self.BUTTON_setting.get_rect())
        if self.is_mainmenu_active:
            screen_surface.blit(self.mainmenu_surface, self.mainmenu_rect)
            screen_surface.blit(self.BUTTON_mainmenu.get_surface(), self.BUTTON_mainmenu.get_rect())
            screen_surface.blit(self.BUTTON_restart.get_surface(), self.BUTTON_restart.get_rect())
            screen_surface.blit(self.BUTTON_continue.get_surface(), self.BUTTON_continue.get_rect())

class Button(GUI):
    def __init__(self, path_to_image, position, scale = (42,42)):
        super().__init__()
        self.image_frame = self._load_animation_frames(os.path.join('assets', 'GUI', path_to_image))
        self.image_frame = [pygame.transform.scale(image, scale) for image in self.image_frame]
        self.image = self.image_frame[self.image_index]
        self.rect = self.image.get_frect(center = position)
    
    def get_surface(self):
        self.image = self.image_frame[self.image_index]
        return self.image
    
    def get_rect(self):
        return self.rect
    
    def get_active_state(self):
        return self.is_active
    
    def handle_events(self, mouse_pos, mouse_click, mouse_just_clicked):
        if self.rect.collidepoint(mouse_pos):
            if mouse_just_clicked[0] and not self.is_active:
                self.is_active = True
                return
            elif mouse_just_clicked[0] and self.is_active:
                self.is_active = False
                return
            
            self.image_index = 1
        else:
            self.image_index = 0


