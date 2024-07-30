# hello sir
# i've used a lot of c# coding conventions (unity) so sorry if it's confusing
# key things are the way i've commented things (using the <summary> tags), calling functions that happen every tick as update & probably more that I can't see yet
# also i have used more modules than just pygame/sys but I believe they come installed with python
# i've copied & pasted this to the top of every script just so you see this
# pls give me bonus marks for not using AI :)

# this script is a "launcher" for the main game AND SHOULD BE RUN AS THE PRIMARY SCRIPT, however everything will work if you just run main.py, just won't have a menu to interact with

import pygame, sys, math, random, subprocess
import project_settings as settings

pygame.init()

constants = settings.constants

# common colours, just making it easy to change colour scheme
WHITE = (250, 250, 255)
BLACK = (2, 0, 0)
LIGHT_GRAY = (230, 230, 232)
GRAY = (200,200,205)

FONT = pygame.font.SysFont('Verdana', 28)
TITLE_FONT = pygame.font.SysFont('Verdana', 69, bold=True) # nice

# using a classed based system just because of how modular it is, + keeps things nice & tidy

# <summary>
# container for all ui elements, like a unity canvas
# </summary>
class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.current_screen = None
        self.screens = {}

    def add_screen(self, name, screen):
        self.screens[name] = screen

    def set_screen(self, name):
        self.current_screen = self.screens.get(name)

    def update(self):
        if self.current_screen:
            self.current_screen.update()

    def render(self):
        if self.current_screen:
            self.current_screen.render()

# <summary>
# an individual "screen" for each page, for now just main menu & tutorial
# </summary>            
class Screen:
    def __init__(self, ui_manager):
        self.ui_manager = ui_manager
        self.triangles = self.create_triangles()

    # function for creating the background triangles, surprisingly simple for the effect it creates
    # CHANGE MADE: swapped out the repeating snake scale pattern for this, as i needed more space & padding for the buttons than I thought i'd need    
    def create_triangles(self):
        triangles = []
        for _ in range(10):
            x = random.uniform(0, constants.WIDTH)
            y = random.uniform(0, constants.HEIGHT)
            size = random.uniform(100, 200)
            speed = random.uniform(0.001, 0.01)
            angle = random.uniform(0, 2 * math.pi)
            direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * random.uniform(0.1, 0.5)
            triangles.append({'pos': pygame.math.Vector2(x, y), 'size': size, 'angle': angle, 'speed': speed, 'direction': direction})
        return triangles
    
    def update_triangles(self):
        for triangle in self.triangles:
            triangle['angle'] += triangle['speed']
            triangle['pos'] += triangle['direction']
            if triangle['pos'].x < -triangle['size'] or triangle['pos'].x > constants.WIDTH + triangle['size'] or triangle['pos'].y < -triangle['size'] or triangle['pos'].y > constants.HEIGHT + triangle['size']:
                triangle['pos'] = pygame.math.Vector2(random.uniform(0, constants.WIDTH), random.uniform(0, constants.HEIGHT))

    def draw_triangles(self):
        for triangle in self.triangles:
            points = []
            for i in range(3):
                angle = triangle['angle'] + i * 2 * math.pi / 3
                point = triangle['pos'] + pygame.math.Vector2(math.cos(angle), math.sin(angle)) * triangle['size']
                points.append((point.x, point.y))
            pygame.draw.polygon(self.ui_manager.screen, LIGHT_GRAY, points, width=0)

    def update(self):
        self.update_triangles()

    def render(self):
        self.ui_manager.screen.fill(WHITE)
        self.draw_triangles()
        
# <summary>
# main menu page derived from screen class
# </summary>        
class MainMenu(Screen):
    def __init__(self, ui_manager):
        super().__init__(ui_manager)
        self.buttons = [
            Button("Start Game", constants.WIDTH // 2, constants.HEIGHT // 2, self.start_game),
            Button("Tutorial", constants.WIDTH // 2, constants.HEIGHT // 2 + 60, self.show_tutorial)
        ]

    def update(self):
        super().update()
        for button in self.buttons:
            button.update()

    def render(self):
        super().render()
        title_surface = TITLE_FONT.render("Main Menu", True, BLACK)
        self.ui_manager.screen.blit(title_surface, (constants.WIDTH // 2 - title_surface.get_width() // 2, 50))
        for button in self.buttons:
            button.render(self.ui_manager.screen)

    def start_game(self):
        self.ui_manager.set_screen('main_game')

    def show_tutorial(self):
        self.ui_manager.set_screen('tutorial')

# <summary>
# tutorial page derived from screen class, like main menu
# </summary>        
class Tutorial(Screen):
    def __init__(self, ui_manager):
        super().__init__(ui_manager)
        self.text = "This is the tutorial. Scroll to read more."
        #self.images = [pygame.image.load('example.png')]  # Replace with your own images
        self.scroll_offset = 0
        self.back_button = Button("Back", 60, 30, self.go_back)

    def update(self):
        super().update()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.scroll_offset += 5
        if keys[pygame.K_DOWN]:
            self.scroll_offset -= 5
        self.back_button.update()

    def render(self):
        super().render()
        y_offset = self.scroll_offset
        try:
            for image in self.images:
                self.ui_manager.screen.blit(image, (50, y_offset))
                y_offset += image.get_height() + 10
        except:
            # print("No images in loaded scene")
            pass 
        text_surface = FONT.render(self.text, True, BLACK)
        self.ui_manager.screen.blit(text_surface, (50, y_offset))
        self.back_button.render(self.ui_manager.screen)
        
    def go_back(self):
        self.ui_manager.set_screen('main_menu')

# <summary>
# TEMPORARY PAGE FOR TESTING
# will be swapped with a method of opening main.py
# </summary>     
class MainGame(Screen):
    def __init__(self, ui_manager):
        super().__init__(ui_manager)

    def update(self):
        super().update()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.ui_manager.set_screen('main_menu')

    def render(self):
        super().render()
        text_surface = FONT.render("Main Game - Press ESC to return to menu", True, WHITE)
        self.ui_manager.screen.blit(text_surface, (50, constants.HEIGHT // 2))

# <summary>
# creating classes for individual ui components, so far its just buttons
# uses basic rectangle "collision" detection with the mouse, renders hover animation if hovered & clicking triggers customisable action
# </summary>        
class Button:
    def __init__(self, text, x, y, action):
        self.text = text
        self.x = x
        self.y = y
        self.action = action
        self.rect = pygame.Rect(x - 100, y - 25, 200, 50)
        self.hovered = False

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered and pygame.mouse.get_pressed()[0]:
            self.action()

    def render(self, screen):
        color = LIGHT_GRAY if self.hovered else GRAY
        pygame.draw.rect(screen, color, self.rect)
        text_surface = FONT.render(self.text, True, BLACK)
        screen.blit(text_surface, (self.x - text_surface.get_width() // 2, self.y - text_surface.get_height() // 2))

# <summary>
# combines everything together
# </summary>        
def main():
    screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))
    pygame.display.set_caption('UI Engine Example')
    ui_manager = UIManager(screen)

    # Create and add screens
    ui_manager.add_screen('main_menu', MainMenu(ui_manager))
    ui_manager.add_screen('tutorial', Tutorial(ui_manager))
    ui_manager.add_screen('main_game', MainGame(ui_manager))

    # Set the initial screen
    ui_manager.set_screen('main_menu')

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        ui_manager.update()
        ui_manager.render()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

# ensure duplicate processes aren't run, or when importing to other scripts
if __name__ == "__main__":
    main()
