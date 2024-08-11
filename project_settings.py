# hello sir
# i've used a lot of c# coding conventions (unity) so sorry if it's confusing
# also i have used more modules than just pygame/sys but I believe they come installed with python
# i've copied & pasted this to the top of every script just so you see this
# pls give me bonus marks for not using AI :)

# this is a "settings" script where variables are stored to be used by other scripts, but doesn't have functionality on its own

import pygame, sys
pygame.init()

particleTypes = [ # air has density of 0, negative values float to top, positive fall
    {
        'name':'Sand', # 0
        'moveType':'powder', # how the particle moves
        'colour':(235,225,52), # average particle colour
        'density':1.6, # how dense the particle is
        'reactions':[3], # list of reactions it is a part of (just for optimisation)
        'decay':None, # what it will decay into after amount of frames [decay_into,decay_min_age]
        'sound':pygame.mixer.Sound("sounds/sand.wav"), # sound to play at appropriate times (sometimes when moving, always when the product of reaction, sometimes when being placed)
    },
    {
        'name':'Wall', # 1
        'moveType':'static',
        'colour':(22,20,20),
        'density':100, # infinity
        'reactions':[],
        'decay':None,
        'sound':None,
    },
    {
        'name':'Water', # 2
        'moveType':'fluid',
        'colour':(50,50,255),
        'density':1 ,
        'reactions':[4,6],
        'decay':None,
        'sound':pygame.mixer.Sound("sounds/water.wav"),
    },
    {
        'name':'Hydrogen', # 3
        'moveType':'fluid',
        'colour':(200,50,50),
        'density':-1,
        'reactions':[0,7],
        'decay':[13,150],
        'sound':pygame.mixer.Sound("sounds/vapour.wav"),
    },
    {
        'name':'Fire Gas', # 4
        'moveType':'fluid',
        'colour':(235,110,52),
        'density':-1,
        'reactions':[0,1,2,3,4,5],
        'decay':[5,8],
        'sound':pygame.mixer.Sound("sounds/fire.wav"),
    },
    {
        'name':'Smoke', # 5
        'moveType':'fluid',
        'colour':(75,75,75),
        'density':-1,
        'reactions':[],
        'decay':[-1,24],
        'sound':pygame.mixer.Sound("sounds/fire.wav"),
    },
    {
        'name':'Wood', # 6
        'moveType':'static',
        'colour':(168,100,50),
        'density':100, # all solids density is max
        'reactions':[1,6],
        'decay':None,
        'sound':pygame.mixer.Sound("sounds/wood.wav"),
    },
    {
        'name':'Fire Solid', # 7
        'moveType':'static',
        'colour':(235,110,52),
        'density':100,
        'reactions':[0,1,2,3,4,5],
        'decay':[4,20],
        'sound':pygame.mixer.Sound("sounds/fire.wav"),
    },
    {
        'name':'Oil', # 8
        'moveType':'fluid',
        'colour':(168,133,50),
        'density':0.7,
        'reactions':[2],
        'decay':None,
        'sound':pygame.mixer.Sound("sounds/water.wav"),
    },
    {
        'name':'Fire Liquid', # 9
        'moveType':'fluid',
        'colour':(235,110,52),
        'density':0.9,
        'reactions':[0,1,2,3,4,5],
        'decay':[4,20],
        'sound':pygame.mixer.Sound("sounds/fire.wav"),
    },
    {
        'name':'Glass', # 10
        'moveType':'static',
        'colour':(240,240,255),
        'density':2.5,
        'reactions':[3],
        'decay':None,
        'sound':pygame.mixer.Sound("sounds/glass.wav")
    },
    {
        'name':'Vapour', # 11
        'moveType':'fluid',
        'colour':(220,220,255),
        'density':-1,
        'reactions':[],
        'decay':[2,40],
        'sound':pygame.mixer.Sound("sounds/vapour.wav"),
    },
    {
        'name':'Plant', # 12
        'moveType':'static',
        'colour':(20,200,25),
        'density':99, # not accurate but allows accurate behaviour
        'reactions':[5],
        'decay':None, 
        'sound':pygame.mixer.Sound("sounds/sand.wav"),
    },
    {
        'name':'Star', # 13
        'moveType':'static',
        'colour':(255,255,245),
        'density':9999,
        'reactions':[],
        'decay':None, 
        'sound':pygame.mixer.Sound("sounds/sand.wav"),
    }
]
reactions = [
    {
        'name':'hydrogen combust', # 0
        'reactants':[[3,4],[3,7],[3,9]], # list of combinations of elements that cause reaction
        'products':[4,-2], # what the particle turns into
        'reactionDifficulty':0 # lower the number, the higher the chance of reaction occuring per frame (randint (0, x) == 0)
    },
    {
        'name':'wood combust', # 1
        'reactants':[[6,4],[6,7],[6,9]],
        'products':[7,-2],
        'reactionDifficulty':1
    },
    {
        'name':'oil combust', # 2
        'reactants':[[8,4],[8,7],[8,9]],
        'products':[9,-2],
        'reactionDifficulty':3
    },
    {
        'name':'glass forging', # 3
        'reactants':[[0,4],[0,7],[0,9]],
        'products':[10,-2],
        'reactionDifficulty':75
    },
    {
        'name':'water evaporation', # 4
        'reactants':[[2,4],[2,7],[2,9]],
        'products':[11,-2],
        'reactionDifficulty':100
    },
    {
        'name':'plant burning', # 5
        'reactants':[[12,4],[12,7],[12,9]],
        'products':[9,-2],
        'reactionDifficulty':4
    },
    {
        'name':'plant growing', # 6
        'reactants':[[2,6]],
        'products':[12,-2],
        'reactionDifficulty':20
    },
    {
        'name':'star... manufacturing?', # 7
        'reactants':[[3,3]],
        'products':[13,-2],
        'reactionDifficulty':1
    },
]

class constants:
    WIDTH, HEIGHT = 1300, 720
    RESOLUTION = (WIDTH, HEIGHT)
    BACKGROUND = (0,0,0)
    FPS = 30
    DISPLAY = pygame.display.set_mode((WIDTH,HEIGHT))
    CLOCK = pygame.time.Clock()
    CELLSIZE = 20
    FLUID_STICKINESS = 1.2
    
    # sound effects
    
    DIALOGUE_SOUND = pygame.mixer.Sound("sounds/dialogue.mp3")
    OBJECTIVE_SOUND = pygame.mixer.Sound("sounds/objective.wav")
    RUMBLE_SOUND = pygame.mixer.Sound("sounds/rumble.wav")
    CLICK_SOUND = pygame.mixer.Sound("sounds/click.wav")
    MUSIC = pygame.mixer.Sound("sounds/music.mp3")
    SOUND_PLAY_CHANCE = 5 # chance of playing sound effect with state change (randint(0,SOUND_PLAY_CHANCE) == 0)
    
    # fonts
    
    FONT = pygame.font.Font('fonts/pixelpro-2p.ttf', 28)
    TITLE_FONT = pygame.font.Font('fonts/8-BIT WONDER.ttf', 90)
    DIALOGUE_FONT = pygame.font.Font('fonts/pixelpro-2p.ttf', 36)

class Particle:
    def __init__(self,pos,particle_type):
        self.pos = pos # position on the tile grid
        self.type = particle_type # what the particle is made of
        self.active = False # if the particle should calculate movement in the current frame (for optimisation)
        self.age = 0 # lifetime of the particle in frames, used for particle decay
        self.colour = [] # rgb colour value of this particle (for the slightly random colour)
        self.fill = 1 # EXPERIMENTAL used for simulating much more advanced fluid physics
        self.prevFill = 1 # EXPERIMENTAL used in conjunction with "self.active" to help with optimisation
        self.shownFill = 1 # EXPERIMENTAL used to show fill, but will be full or empty depending on if there's other particles above, if its falling etc
        self.indestructible = False # only used for wall particles, otherwise major memory leaks occur
        
        self.state = "idle" # EXPERIMENTAL a state machine for determining when a sound should be played for the particle (includes idle, falling, rolling, filling)
        self.prevState = "idle" # "
        

# objectives
from enum import Enum

class ObjectiveType(Enum):
    PLACE_PARTICLE = 1
    REACTION = 2
    CURSOR_SIZE = 3

class Objective:
    def __init__(self, objective_type, target_particle, description, unlocks:list=None):
        self.objective_type = objective_type
        self.target_index = target_particle
        self.description = description
        self.unlocks = unlocks
        
class ScreenShake: # used to share "doScreenShake" across scripts, since python global variables are stupid. also have screenshake vars here to keep code clean-ish
    doScreenShake = False
    shakeTime = 0 # how long, in seconds, the shake has been happening for
    screenShake = [0,0]
    SHAKE_MAX_OFFSET = 20
    SHAKE_MAX_CHANGE = 15
    SHAKE_BUILDUP = 5
    SHAKE_QUIT_TIME = 10 # seconds to wait until closing window
    
class GameParams: # used to share starting variables for the game across scripts (for now just if the user is playing sandbox or not)
    sandbox = False