# hello sir
# i've used a lot of c# coding conventions (unity) so sorry if it's confusing
# also i have used more modules than just pygame/sys but I believe they come installed with python
# i've copied & pasted this to the top of every script just so you see this
# pls give me bonus marks for not using AI :)

# this is the script for the main game, manages more of the "backend" of things while particlefunctions.py manages the individual functions for particle movement itself.

from particle_functions import *
from project_settings import *
import pygame, sys
from random import randint
import ui_engine as uiEngine
from progression import *
import asyncio
# import pygetwindow as gw # attempted to create ui_engine as a separate window, but turned out to be much more complicated than I thought

grid = {} # grid[1,2] will return a particle with x position 1, y position 2 (2d array) or None if there is none there
dragging = False # if mouse down & mouse movement is detected
destroying = False # if rmb & mouse movement detected
selected_particle = 0 # index of selected praticle in particleTypes
cursor_size = 1 # size of cursor in pixels width
cursor_rect = pygame.Rect # cursor image

objectiveReady=False # used to tell game loop whether it is ready to display first objective

screen = uiEngine.screen # used as a global, since it is called with multiple functions
running = False # true when inside main game, false when in main menu or quit

screenShake = [0,0]

# dialogue boxes
font = pygame.font.SysFont('Verdana', 18)

class Game:
    # initialise game window
    def __init__(self):
        pygame.init()
        self.screen = uiEngine.screen # pygame.display.set_mode(constants.RESOLUTION) # set resolution to predefined value
        self.clock = pygame.time.Clock()
        self.objectives_manager = ObjectivesManager(self.screen, font, constants.DIALOGUE_SOUND)
        SetupObjectives(self.objectives_manager)
        
        global screen
        screen = uiEngine.screen

        self.NewGame()
        
# generate wall border around game
    def NewGame(self):
        _wall = []
        for x in range(int(constants.WIDTH/constants.CELLSIZE)):
            CreateParticle(Particle([x,int(constants.HEIGHT/constants.CELLSIZE)-1],1))
            CreateParticle(Particle([x,0],1))
            for y in range(int(constants.HEIGHT/constants.CELLSIZE)):
                CreateParticle(Particle([0,y],1))
                CreateParticle(Particle([int(constants.WIDTH/constants.CELLSIZE)-1,y],1))     
        for p in list(grid.values()):
            p.indestructible = True
    
# manage framerate + debugging
    def Update(self):
        pygame.display.flip()
        self.clock.tick(constants.FPS)
        pygame.display.set_caption(f'FPS: {self.clock.get_fps()}   Particle: {particleTypes[unlockedParticles[selected_particle]]['name'].upper()}')
        global screen
        if screen == None:
            screen=uiEngine.screen
        if ScreenShake.doScreenShake:
            ScreenShake.screenShake = [Clamp(screenShake[0] + randint(-ScreenShake.SHAKE_MAX_CHANGE,ScreenShake.SHAKE_MAX_CHANGE), -ScreenShake.SHAKE_MAX_OFFSET, ScreenShake.SHAKE_MAX_OFFSET) * Clamp(ScreenShake.shakeTime / ScreenShake.SHAKE_BUILDUP,0,1), Clamp(screenShake[1] + randint(-ScreenShake.SHAKE_MAX_CHANGE,ScreenShake.SHAKE_MAX_CHANGE), -ScreenShake.SHAKE_MAX_OFFSET, ScreenShake.SHAKE_MAX_OFFSET) * Clamp(ScreenShake.shakeTime / ScreenShake.SHAKE_BUILDUP,0,1)]
            ScreenShake.shakeTime += 1/constants.FPS # since the rest of the game doesnt use delta time
            if ScreenShake.shakeTime > ScreenShake.SHAKE_QUIT_TIME:
                pygame.display.quit()
                time.sleep(2)
                screen = pygame.display.set_mode((1300,720))
                screen.blit(pygame.image.load("endgame.png").convert(), (0,0))
                pygame.display.flip()
                while True:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
        self.GameLoop()
        self.RenderHUD()
        
# manages main input events, calls updateWorld in particlefunctions.py & displays cursor
    def GameLoop(self):
        global cursor_rect
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            else:
                self.HandleInput(event)
        constants.DISPLAY.fill(constants.BACKGROUND)
        UpdateWorld(self.objectives_manager)
        cursor_rect = pygame.Rect((pygame.mouse.get_pos()[0]//constants.CELLSIZE)*constants.CELLSIZE,(pygame.mouse.get_pos()[1]//constants.CELLSIZE)*constants.CELLSIZE,constants.CELLSIZE*cursor_size,constants.CELLSIZE*cursor_size)
        pygame.draw.rect(constants.DISPLAY,(200,200,200),cursor_rect) # to add transparency, this has to be a surface that is blitted to the screen (not bothered)
        constants.CLOCK.tick(constants.FPS)

        global objectiveReady
        if not objectiveReady:
            self.objectives_manager.RetrieveObjective()
            objectiveReady = True
      
 # render ui components for the main game itself, for now just the current particle indicator
    def RenderHUD(self):
        colour = (255,250,250)
        padding = 4
        offset = [25,25]
        
        # current particle indicator
        
        text = f"{particleTypes[unlockedParticles[selected_particle]]['name'].upper() } SELECTED"
        textSurface = constants.FONT.render(text, True, colour)
    
        # auto calculate dimensions
        textWidth, textHeight = textSurface.get_size()
        elementIndicatorSize = textHeight  # indicator is as tall as the text
        sumWidth = elementIndicatorSize + padding + textWidth
    
        # change positions of text & indicator based on padding & the other's position
        elementIndicatorPos = (padding + offset[0], padding + offset[1])
        textPos = (padding*2 + elementIndicatorSize + offset[0], padding + offset[1])
    
        # draws the background as a sem-transparent rectangle, accounting for text width & padding
        backgroundRect = pygame.Rect(0, 0, sumWidth + 2 * padding, textHeight + 2 * padding)
        backgroundSurface = pygame.Surface((backgroundRect.width, backgroundRect.height), pygame.SRCALPHA)
        backgroundSurface.fill((0,0,0)) # change background colour here
        backgroundSurface.set_alpha(150)
        constants.DISPLAY.blit(backgroundSurface, (offset[0],offset[1]))
    
        pygame.draw.rect(constants.DISPLAY, particleTypes[unlockedParticles[selected_particle]]['colour'], (*elementIndicatorPos, elementIndicatorSize, elementIndicatorSize))
        constants.DISPLAY.blit(textSurface, textPos)
        
# rest of input management, debating whether i add keybinds system
    def HandleInput(self, event:pygame.event):
        global dragging
        global destroying
        global selected_particle
        global cursor_size
        if event.type == pygame.MOUSEBUTTONDOWN: # placing particles
            if event.button == pygame.BUTTON_LEFT:
                dragging = True
            elif event.button == pygame.BUTTON_RIGHT: # destroying particles
                destroying = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == pygame.BUTTON_LEFT:
                dragging = False
            elif event.button == pygame.BUTTON_RIGHT:
                destroying = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c: # change particle
                if not selected_particle +1 >= len(unlockedParticles): # only switch between unlocked particles (sandbox just makes it so every particle starts unlocked)
                    selected_particle += 1
                else:
                    selected_particle = 0
                print(particleTypes[unlockedParticles[selected_particle]]['name'].upper()) # for debugging, print out the name of the just selected particle
            elif event.key == pygame.K_EQUALS and cursor_size < 3: # clamp cursor size to a max of 3
                cursor_size += 1
                self.objectives_manager.CheckCursorSize(0)
            elif event.key == pygame.K_MINUS and cursor_size > 1: # clamp cursor size to a min of 1
                cursor_size -= 1
                self.objectives_manager.CheckCursorSize(0)
        if dragging: # if lmb
            self.objectives_manager.CheckPlaceParticle(unlockedParticles[selected_particle]) # trigger a check for if the placed particle satisfies the objective
            for x in range(cursor_rect.left,cursor_rect.left+cursor_rect.width): # for the width of the mouse cursor
                for y in range(cursor_rect.top,cursor_rect.top+cursor_rect.height):    # for the height of the mouse cursor
                    CreateParticle(Particle([x//constants.CELLSIZE,y//constants.CELLSIZE],unlockedParticles[selected_particle])) # create particle at x,y position (uses // for floor division, which divides & rounds down)
        elif destroying: # if rmb
            for x in range(cursor_rect.left,cursor_rect.left+cursor_rect.width): # same as above but clears cells
                for y in range(cursor_rect.top,cursor_rect.top+cursor_rect.height):  
                    
                    try: # uses try in case particles dont exist in requested delete area
                        ClearCell(Particle([x//constants.CELLSIZE,y//constants.CELLSIZE],selected_particle),[x//constants.CELLSIZE,y//constants.CELLSIZE]) 
                    except:
                        pass
# run the game
    def run(self):
        running = True
        while running:
            self.Update()    

# runs the main game screen rather than the ui engine screen
def RunMainGame():
    if uiEngine.requestRunning: # if the ui engine has requested the main game be run
        if not running:    
            game = Game() # python classes are weird but creating new game object (different to a gameObject for some stupid reason)
            game.run()
            running = True
        
running = False

# run the game & load main menu first
if __name__ == '__main__':
    uiEngine.main()  
    if not running:    
        game = Game() # run the game as a class to keep code clean
        game.run() 
        running = True # used in the end game when window is closed but code is still running
        #uiEngine.running = False  