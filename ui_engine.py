# hello sir
# i've used a lot of c# coding conventions (unity) so sorry if it's confusing
# key things are the way i've commented things (using the <summary> tags), calling functions that happen every tick as Update & probably more that I can't see yet
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

SCROLL_CLAMP = (-500,0)

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

    def AddScreen(self, name, screen):
        self.screens[name] = screen

    def setScreen(self, name):
        self.current_screen = self.screens.get(name)

    def Update(self):
        if self.current_screen:
            self.current_screen.Update()

    def Render(self):
        if self.current_screen:
            self.current_screen.Render()

# <summary>
# an individual "screen" for each page, for now just main menu & tutorial
# </summary>            
class Screen:
    def __init__(self, uiManager):
        self.uiManager = uiManager
        self.triangles = self.create_triangles()

    # function for creating the background triangles, surprisingly simple for the effect it creates
    # CHANGE MADE: swapped out the repeating snake scale pattern for this, as i needed more space & padding for the buttons than I thought i'd need    
    def create_triangles(self):
        triangles = []
        for i in range(10):
            x = random.uniform(0, constants.WIDTH)
            y = random.uniform(0, constants.HEIGHT)
            size = random.uniform(100, 200)
            speed = random.uniform(0.001, 0.01)
            angle = random.uniform(0, 2 * math.pi)
            direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * random.uniform(0.1, 0.5)
            triangles.append({'pos': pygame.math.Vector2(x, y), 'size': size, 'angle': angle, 'speed': speed, 'direction': direction})
        return triangles
    
    # Update each triangle every frame
    def Update_triangles(self):
        for triangle in self.triangles:
            triangle['angle'] += triangle['speed']
            triangle['pos'] += triangle['direction']
            if triangle['pos'].x < -triangle['size'] or triangle['pos'].x > constants.WIDTH + triangle['size'] or triangle['pos'].y < -triangle['size'] or triangle['pos'].y > constants.HEIGHT + triangle['size']:
                triangle['pos'] = pygame.math.Vector2(random.uniform(0, constants.WIDTH), random.uniform(0, constants.HEIGHT))

    # using the python polygon function because for some reason it doesnt support triangles by default           
    def draw_triangles(self):
        for triangle in self.triangles:
            points = []
            for i in range(3):
                angle = triangle['angle'] + i * 2 * math.pi / 3
                point = triangle['pos'] + pygame.math.Vector2(math.cos(angle), math.sin(angle)) * triangle['size']
                points.append((point.x, point.y))
            pygame.draw.polygon(self.uiManager.screen, LIGHT_GRAY, points, width=0)

    def Update(self):
        self.Update_triangles()

    def Render(self):
        self.uiManager.screen.fill(WHITE)
        self.draw_triangles()
        
# <summary>
# main menu page derived from screen class
# </summary>        
class MainMenu(Screen):
    def __init__(self, uiManager):
        super().__init__(uiManager)
        self.buttons = [
            Button("Start Game", constants.WIDTH // 2, constants.HEIGHT // 2, self.start_game),
            Button("Tutorial", constants.WIDTH // 2, constants.HEIGHT // 2 + 60, self.show_tutorial)
        ]

    def Update(self):
        super().Update()
        for button in self.buttons:
            button.Update()

    def Render(self):
        super().Render()
        title_surface = TITLE_FONT.render("Main Menu", True, BLACK)
        self.uiManager.screen.blit(title_surface, (constants.WIDTH // 2 - title_surface.get_width() // 2, 50))
        for button in self.buttons:
            button.Render(self.uiManager.screen)

    def start_game(self):
        self.uiManager.setScreen('main_game')

    def show_tutorial(self):
        self.uiManager.setScreen('tutorial')

# <summary>
# tutorial page derived from screen class, like main menu
# </summary>        
class Tutorial(Screen):
    def __init__(self, uiManager):
        super().__init__(uiManager)
        self.text = "blah blah blah tutorial stuff"
        #self.images = [pygame.image.load('example.png')]  # no images yet
        self.scrollOffset = 0 # how far the user has scrolled
        self.backButton = Button("Back", 60, 30, self.go_back)

    def Update(self):
        super().Update()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.scrollOffset += 5
        if keys[pygame.K_DOWN]:
            self.scrollOffset -= 5
        self.scrollOffset = min(SCROLL_CLAMP[1], max(SCROLL_CLAMP[0], self.scrollOffset))
        self.backButton.Update()

    def Render(self):
        super().Render()
        yOffset = self.scrollOffset
        try:
            for image in self.images:
                self.uiManager.screen.blit(image, (50, yOffset))
                yOffset += image.get_height() + 10
        except:
            # print("No images in loaded scene")
            pass 
        surfaceText = FONT.render(self.text, True, BLACK)
        self.uiManager.screen.blit(surfaceText, (50, yOffset+70))
        self.backButton.Render(self.uiManager.screen)
        
    def go_back(self):
        self.uiManager.setScreen('main_menu')

# <summary>
# TEMPORARY PAGE FOR TESTING
# will be swapped with a method of opening main.py
# </summary>     
class MainGame(Screen):
    def __init__(self, uiManager):
        super().__init__(uiManager)

    def Update(self):
        super().Update()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.uiManager.setScreen('main_menu')

    def Render(self):
        super().Render()
        surfaceText = FONT.render("Main Game - Press ESC to return to menu", True, WHITE)
        self.uiManager.screen.blit(surfaceText, (50, constants.HEIGHT // 2))

# <summary>
# creating classes for individual ui components, so far its just buttons
# uses basic rectangle "collision" detection with the mouse, Renders hover animation if hovered & clicking triggers customisable action
# </summary>        
class Button:
    def __init__(self, text, x, y, action):
        self.text = text
        self.x = x
        self.y = y
        self.action = action
        self.rect = pygame.Rect(x - 100, y - 25, 200, 50)
        self.hovered = False

    def Update(self):
        mousePos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mousePos)
        if self.hovered and pygame.mouse.get_pressed()[0]:
            self.action()

    def Render(self, screen):
        color = LIGHT_GRAY if self.hovered else GRAY
        pygame.draw.rect(screen, color, self.rect)
        surfaceText = FONT.render(self.text, True, BLACK)
        screen.blit(surfaceText, (self.x - surfaceText.get_width() // 2, self.y - surfaceText.get_height() // 2))

# <summary>
# combines everything together
# </summary>        
def main():
    screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))
    pygame.display.set_caption('UI Engine Example')
    uiManager = UIManager(screen)

    # Create and add screens
    uiManager.AddScreen('main_menu', MainMenu(uiManager))
    uiManager.AddScreen('tutorial', Tutorial(uiManager))
    uiManager.AddScreen('main_game', MainGame(uiManager))

    # Set the initial screen
    uiManager.setScreen('main_menu')

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        uiManager.Update()
        uiManager.Render()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

# ensure duplicate processes aren't run, or when importing to other scripts
if __name__ == "__main__":
    main()
