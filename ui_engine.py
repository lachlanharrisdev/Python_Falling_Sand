# hello sir
# i've used a lot of c# coding conventions (unity) so sorry if it's confusing
# also i have used more modules than just pygame/sys but I believe they come installed with python
# i've copied & pasted this to the top of every script just so you see this
# pls give me bonus marks for not using AI :)

# this script is a "launcher" for the main game AND SHOULD BE RUN AS THE PRIMARY SCRIPT, however everything will work if you just run main.py, just won't have a menu to interact with

import pygame, sys, math, random, subprocess

from pygame.mixer import music
import project_settings as settings
# import main as mainGame # not imported as main since it's short for main menu in this context

requestRunning = False # since this is imported into main, it uses a boolean to call a function in there to run the main game, as this script is unable to discretely call methods there

pygame.init()

constants = settings.constants

# common colours, just making it easy to change colour scheme
BACKGROUND = (12, 11, 10)
FOREGROUND = (250, 250, 255)
TERTIARY = (20, 20, 18)
TERTIARY_DARK = (40,40,45)

SCROLL_CLAMP = (100,100) # scroll limits, in pixels, for the tutorial screen

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
            pygame.draw.polygon(self.uiManager.screen, TERTIARY, points, width=0)

    def Update(self):
        self.Update_triangles()

    def Render(self):
        self.uiManager.screen.fill(BACKGROUND)
        self.draw_triangles()
        
# <summary>
# main menu page derived from screen class
# </summary>        
class MainMenu(Screen):
    def __init__(self, uiManager):
        super().__init__(uiManager)
        self.buttons = [
            Button("Story", constants.WIDTH // 2, constants.HEIGHT // 2, self.start_game),
            Button("Sandbox", constants.WIDTH // 2, constants.HEIGHT // 2 + 60, self.start_sandbox),
            Button("Controls", constants.WIDTH // 2, constants.HEIGHT // 2 + 120, self.show_tutorial)
        ]

    def Update(self):
        super().Update()
        for button in self.buttons:
            button.Update()

    def Render(self):
        super().Render()
        title_surface = constants.TITLE_FONT.render("COSMIC COOK", True, FOREGROUND)
        self.uiManager.screen.blit(title_surface, (constants.WIDTH // 2 - title_surface.get_width() // 2, 50))
        for button in self.buttons:
            button.Render(self.uiManager.screen)

    def start_game(self):
        settings.GameParams.sandbox = False
        self.uiManager.setScreen('main_game')

    def show_tutorial(self):
        self.uiManager.setScreen('tutorial')
    
    def start_sandbox(self):
        settings.GameParams.sandbox = True
        self.uiManager.setScreen('main_game')

# <summary>
# tutorial page derived from screen class, like main menu
# </summary>        
class Tutorial(Screen):
    def __init__(self, uiManager):
        super().__init__(uiManager)
        self.text = None # "Welcome to Cosmic Cook! This is a 2d sandbox game where you simply have to complete objectives given by the narrator. This is a story game, so it is best to be played only once & not have your friends spoil surprises for you."
        self.images = [pygame.image.load('instructions_transparent.png')]  # no images yet
        self.scrollOffset = 20 # how far the user has scrolled
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
                self.uiManager.screen.blit(image, ((constants.WIDTH-image.get_width())/2, yOffset+50))
                yOffset += image.get_height() + 10
        except:
            # print("No images in loaded scene")
            pass 
        # surfaceText = constants.FONT.render(self.text, True, FOREGROUND)
        # self.uiManager.screen.blit(surfaceText, (50, yOffset+70))
        self.backButton.Render(self.uiManager.screen)
        

        # render text, reuses dialogue code to automatically display in multiple lines
        if not self.text == None:

            screen_width = constants.WIDTH
            screen_height = constants.HEIGHT

            # Calculate the size of the dialogue box based on the text
            lines = []
            words = self.text.split(' ')
            max_width = screen_width - 100  # Leave some padding
            line = ""
    
            _letter = 0
    
            for word in words:
                test_line = f"{line} {word}".strip()
                if constants.FONT.size(test_line)[0] <= max_width:
                    line = test_line
                else:
                    lines.append(line)
                    line = word
            lines.append(line)

            # Calculate box dimensions
            box_padding = 10
            max_line_width = max([constants.FONT.size(line)[0] for line in lines])
            box_width = max_line_width + 2 * box_padding
            box_height = len(lines) * constants.FONT.get_height() + 2 * box_padding
    
            # Position the box in the center-bottom of the screen
            box_x = (screen_width - box_width) // 2
            box_y = 0 + box_height - 50

            # Create a surface for the dialogue box
            box_surface = pygame.Surface((box_width, box_height))
            box_surface.fill(BACKGROUND)

            # Main loop to display each character one at a time
            for i, line in enumerate(lines):
                for j, char in enumerate(line):
                    char_surface = constants.FONT.render(char, True, FOREGROUND)
                    box_surface.blit(char_surface, (box_padding + constants.FONT.size(line[:j])[0], box_padding + i * constants.FONT.get_height()))
        
            self.uiManager.screen.blit(box_surface, (box_x, box_y + yOffset))
        
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
        '''
        super().Render()
        surfaceText = FONT.render("Main Game - Press ESC to return to menu", True, BACKGROUND)
        self.uiManager.screen.blit(surfaceText, (50, constants.HEIGHT // 2))'''
        requestRunning = True
        pygame.mixer.music.fadeout(2000)
        RunGame()
        

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
            constants.CLICK_SOUND.play()

    def Render(self, screen):
        color = TERTIARY if self.hovered else TERTIARY_DARK
        pygame.draw.rect(screen, color, self.rect)
        surfaceText = constants.FONT.render(self.text, True, FOREGROUND)
        screen.blit(surfaceText, (self.x - surfaceText.get_width() // 2, self.y - surfaceText.get_height() // 2))

# <summary>
# combines everything together
# </summary>   
screen = None

running = True

def main():
    screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))
    pygame.display.set_caption('UI Engine Example')
    uiManager = UIManager(screen)
    
    # play ambient music on repeat
    pygame.mixer.music.load("sounds/music.mp3")
    pygame.mixer.music.play(-1)
    
    music.set_volume(0.8)

    # Create and add screens
    uiManager.AddScreen('main_menu', MainMenu(uiManager))
    uiManager.AddScreen('tutorial', Tutorial(uiManager))
    uiManager.AddScreen('main_game', MainGame(uiManager))

    # Set the initial screen
    uiManager.setScreen('main_menu')

    clock = pygame.time.Clock()

    global running # python is genuinely a stupid language, please let us use c++

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

        uiManager.Update()
        uiManager.Render()
        if requestRunning:
            running=False

        pygame.display.flip()
        clock.tick(constants.FPS)
    
def RunGame():
    global running
    running = False

# ensure duplicate processes aren't run, or when importing to other scripts
if __name__ == "__main__":
    main()


