# hello sir
# i've used a lot of c# coding conventions (unity) so sorry if it's confusing
# key things are the way i've commented things (using the <summary> tags), calling functions that happen every tick as update & probably more that I can't see yet
# also i have used more modules than just pygame/sys but I believe they come installed with python
# i've copied & pasted this to the top of every script just so you see this
# pls give me bonus marks for not using AI :)

# this is the script for the main game, manages more of the "backend" of things while particlefunctions.py manages the individual functions for particle movement itself.

from particle_functions import *
from project_settings import *
import pygame, sys
from random import randint
# import pygetwindow as gw

grid = {} # format: {cell pos x, cell pos y}
dragging = False # if mouse down & mouse movement is detected
selected_particle = 0 # index of selected praticle in particleTypes
cursor_size = 1 # size of cursor in pixels width
cursor_rect = pygame.Rect # cursor image

class Game:
    # initialise game window
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(constants.RESOLUTION) # set resolution to predefined value
        self.clock = pygame.time.Clock()
        self.NewGame()
        
# generate wall border around game
    def NewGame(self):
        for x in range(int(constants.WIDTH/constants.CELLSIZE)):
            CreateParticle(Particle([x,int(constants.HEIGHT/constants.CELLSIZE)-1],1))
            CreateParticle(Particle([x,0],1))
            for y in range(int(constants.HEIGHT/constants.CELLSIZE)):
                CreateParticle(Particle([0,y],1))
                CreateParticle(Particle([int(constants.WIDTH/constants.CELLSIZE)-1,y],1))
    
    def Update(self):
        pygame.display.flip()
        self.clock.tick(constants.FPS)
        pygame.display.set_caption(f'FPS: {self.clock.get_fps()}   Particle: {particleTypes[selected_particle]['name'].upper()}')
        self.GameLoop()
        
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
        UpdateWorld()
        cursor_rect = pygame.Rect((pygame.mouse.get_pos()[0]//constants.CELLSIZE)*constants.CELLSIZE,(pygame.mouse.get_pos()[1]//constants.CELLSIZE)*constants.CELLSIZE,constants.CELLSIZE*cursor_size,constants.CELLSIZE*cursor_size)
        pygame.draw.rect(constants.DISPLAY,(200,200,200),cursor_rect) # to add alpha this has to be a surface that is blitted to the screen
        constants.CLOCK.tick(constants.FPS)
        
    def HandleInput(self, event:pygame.event):
        global dragging
        global selected_particle
        global cursor_size
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == pygame.BUTTON_LEFT:
                dragging = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                if not selected_particle +1 >= len(particleTypes):
                    selected_particle += 1
                else:
                    selected_particle = 0
                print(particleTypes[selected_particle]['name'].upper())
            elif event.key == pygame.K_EQUALS and cursor_size < 3:
                cursor_size += 1
            elif event.key == pygame.K_MINUS and cursor_size > 1:
                cursor_size -= 1
        if dragging:
            for x in range(cursor_rect.left,cursor_rect.left+cursor_rect.width):
                for y in range(cursor_rect.top,cursor_rect.top+cursor_rect.height):    
                    CreateParticle(Particle([x//constants.CELLSIZE,y//constants.CELLSIZE],selected_particle))
        
    def run(self):
        while True:
            self.Update()

if __name__ == '__main__':
    game = Game()
    game.run()