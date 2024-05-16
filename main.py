# hello zigglezord
# TODO:
# 1. add the new fluid physics to particles with negative density --ABANDONED
# 2. optimise (and add more necessary) ways that stats are transferred to newly created particles (such as fill level, age, etc) --DONE
# 3. explosion physics & velocity simulation???
# probably more but rn i'm lazy
# you're gonna cringe reading this, cry abt it

from particle_functions import *
from project_settings import *
import pygame, sys
from random import randint

grid = {} # format: {cell pos x, cell pos y}
dragging = False
selected_particle = 0
cursor_size = 1
cursor_rect = pygame.Rect

class Game:
    # initialise game window
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(constants.RESOLUTION)
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
        pygame.display.set_caption(f'{self.clock.get_fps()}')
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


