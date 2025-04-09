import pygame
import sys
from pygame import Rect

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
BG_COLOR = (40, 40, 60)

# Colors
MENU_BG = (60, 60, 90)
MENU_TEXT = (220, 220, 220)
MENU_HIGHLIGHT = (100, 150, 200)
DIALOG_BG = (50, 50, 80)
DIALOG_BORDER = (100, 100, 150)
DIALOG_TITLE = (255, 255, 255)
DIALOG_OPTION = (200, 200, 200)
DIALOG_SELECTED = (100, 200, 255)

class DialogBox:
    def __init__(self, rect, title, options):
        self.rect = rect
        self.title = title
        self.options = options
        self.active = False
        self.selected_index = 0
        self.font = pygame.font.SysFont('Arial', 24)
        self.title_font = pygame.font.SysFont('Arial', 28, bold=True)
        self.option_rects = self._calculate_option_rects()
    
    def _calculate_option_rects(self):
        rects = []
        option_height = 40
        for i in range(len(self.options)):
            rect = Rect(
                self.rect.x + 10,
                self.rect.y + 60 + i * (option_height + 5),
                self.rect.width - 20,
                option_height
            )
            rects.append(rect)
        return rects
    
    def draw(self, surface):
        if not self.active:
            return
        
        # Draw background and border
        pygame.draw.rect(surface, DIALOG_BG, self.rect)
        pygame.draw.rect(surface, DIALOG_BORDER, self.rect, 3)
        
        # Draw title
        title_surf = self.title_font.render(self.title, True, DIALOG_TITLE)
        title_rect = title_surf.get_rect(center=(self.rect.centerx, self.rect.y + 30))
        surface.blit(title_surf, title_rect)
        
        # Draw options
        for i, (option, rect) in enumerate(zip(self.options, self.option_rects)):
            color = DIALOG_SELECTED if i == self.selected_index else DIALOG_OPTION
            pygame.draw.rect(surface, (70, 70, 100), rect)
            pygame.draw.rect(surface, color, rect, 2)
            
            option_surf = self.font.render(option, True, color)
            option_rect = option_surf.get_rect(center=rect.center)
            surface.blit(option_surf, option_rect)
    
    def handle_event(self, event):
        if not self.active:
            return None
        
        if event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(event.pos):
                    self.selected_index = i
                    break
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(event.pos):
                    return i
            if not self.rect.collidepoint(event.pos):
                self.active = False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = max(0, self.selected_index - 1)
            elif event.key == pygame.K_DOWN:
                self.selected_index = min(len(self.options) - 1, self.selected_index + 1)
            elif event.key == pygame.K_RETURN:
                return self.selected_index
            elif event.key == pygame.K_ESCAPE:
                self.active = False
        
        return None

class MenuBar:
    def __init__(self, rect, menus):
        self.rect = rect
        self.menus = menus
        self.active_menu = None
        self.font = pygame.font.SysFont('Arial', 20)
        self.menu_rects = self._calculate_menu_rects()
    
    def _calculate_menu_rects(self):
        rects = []
        x = self.rect.x + 10
        for menu in self.menus:
            text_surf = self.font.render(menu['title'], True, MENU_TEXT)
            text_rect = text_surf.get_rect(topleft=(x, self.rect.y + 10))
            rects.append((menu['title'], text_rect))
            x += text_rect.width + 20
        return rects
    
    def draw(self, surface):
        pygame.draw.rect(surface, MENU_BG, self.rect)
        for title, rect in self.menu_rects:
            color = MENU_HIGHLIGHT if title == self.active_menu else MENU_TEXT
            text_surf = self.font.render(title, True, color)
            surface.blit(text_surf, rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            for title, rect in self.menu_rects:
                if rect.collidepoint(event.pos):
                    self.active_menu = title
                    break
            else:
                self.active_menu = None
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for title, rect in self.menu_rects:
                if rect.collidepoint(event.pos):
                    return title
        return None

class DialogSystem:
    def __init__(self, screen_rect):
        self.screen_rect = screen_rect
        self.dialog = None
        self.menu_bar = self._create_menu_bar()
    
    def _create_menu_bar(self):
        menus = [
            {'title': 'File', 'options': ['New', 'Open', 'Save', 'Save As', 'Exit']},
            {'title': 'Edit', 'options': ['Undo', 'Redo', 'Cut', 'Copy', 'Paste']},
            {'title': 'View', 'options': ['Zoom In', 'Zoom Out', 'Grid Toggle']},
            {'title': 'Help', 'options': ['About', 'Documentation']}
        ]
        return MenuBar(Rect(0, 0, self.screen_rect.width, 50), menus)
    
    def create_dialog(self, title, options):
        dialog_width = 300
        dialog_height = 100 + len(options) * 45
        dialog_rect = Rect(
            (self.screen_rect.width - dialog_width) // 2,
            (self.screen_rect.height - dialog_height) // 2,
            dialog_width,
            dialog_height
        )
        self.dialog = DialogBox(dialog_rect, title, options)
        self.dialog.active = True
        return self.dialog
    
    def draw(self, surface):
        self.menu_bar.draw(surface)
        if self.dialog and self.dialog.active:
            # Dim background
            s = pygame.Surface((self.screen_rect.width, self.screen_rect.height), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            surface.blit(s, (0, 0))
            self.dialog.draw(surface)
    
    def handle_event(self, event):
        result = None
        
        # Handle dialog first if active
        if self.dialog and self.dialog.active:
            result = self.dialog.handle_event(event)
            if result is not None:
                self.dialog.active = False
                return ('dialog', result)
        
        # Then handle menu bar
        menu_result = self.menu_bar.handle_event(event)
        if menu_result and event.type == pygame.MOUSEBUTTONDOWN:
            for menu in self.menu_bar.menus:
                if menu['title'] == menu_result:
                    self.create_dialog(menu_result, menu['options'])
                    break
        
        return None

class MainApplication:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pygame Menu System")
        self.clock = pygame.time.Clock()
        self.dialog_system = DialogSystem(self.screen.get_rect())
        self.running = True
        self.message = "Select an option from the menu"
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            result = self.dialog_system.handle_event(event)
            if result:
                menu_title, option_index = result
                selected_option = self.dialog_system.dialog.options[option_index]
                self.message = f"Selected: {menu_title} > {selected_option}"
                
                # Handle specific actions
                if selected_option == "Exit":
                    self.running = False
    
    def update(self):
        pass
    
    def draw(self):
        self.screen.fill(BG_COLOR)
        
        # Draw main content
        font = pygame.font.SysFont('Arial', 32)
        text_surf = font.render(self.message, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(text_surf, text_rect)
        
        # Draw UI
        self.dialog_system.draw(self.screen)
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = MainApplication()
    app.run()