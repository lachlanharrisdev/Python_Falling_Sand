import pygame, sys
pygame.init()

particleTypes = [ # air has density of 0, negative values float to top, positive fall
    {
        'name':'sand', # 0
        'moveType':'powder', # how the particle moves
        'colour':(235,225,52), # average particle colour
        'density':1.6, # how dense the particle is
        'reactions':[3], # list of reactions it is a part of (just for optimisation)
        'decay':None, # what it will decay into after amount of frames [decay_into,decay_min_age]
    },
    {
        'name':'wall', # 1
        'moveType':'static',
        'colour':(100,100,100),
        'density':100, # infinity
        'reactions':[],
        'decay':None,
    },
    {
        'name':'water', # 2
        'moveType':'fluid',
        'colour':(50,50,255),
        'density':1 ,
        'reactions':[4],
        'decay':None,
    },
    {
        'name':'hydrogen', # 3
        'moveType':'fluid',
        'colour':(200,50,50),
        'density':-1,
        'reactions':[0],
        'decay':None,
    },
    {
        'name':'fire_gas', # 4
        'moveType':'fluid',
        'colour':(235,110,52),
        'density':-1,
        'reactions':[0,1,2,3,4],
        'decay':[5,8] 
    },
    {
        'name':'smoke', # 5
        'moveType':'fluid',
        'colour':(75,75,75),
        'density':-1,
        'reactions':[],
        'decay':[-1,24],
    },
    {
        'name':'wood', # 6
        'moveType':'static',
        'colour':(168,100,50),
        'density':100, # all solids density is max
        'reactions':[1],
        'decay':None,
    },
    {
        'name':'fire_solid', # 7
        'moveType':'static',
        'colour':(235,110,52),
        'density':100,
        'reactions':[0,1,2,3,4],
        'decay':[4,20],
    },
    {
        'name':'oil', # 8
        'moveType':'fluid',
        'colour':(168,133,50),
        'density':0.7,
        'reactions':[2],
        'decay':None,
    },
    {
        'name':'fire_liquid', # 9
        'moveType':'fluid',
        'colour':(235,110,52),
        'density':0.9,
        'reactions':[0,1,2,3,4],
        'decay':[4,20],
    },
    {
        'name':'glass', # 10
        'moveType':'static',
        'colour':(240,240,255),
        'density':2.5,
        'reactions':[3],
        'decay':None,
    },
    {
        'name':'vapour', # 11
        'moveType':'fluid',
        'colour':(220,220,255),
        'density':-1,
        'reactions':[],
        'decay':[2,40],
    }
]
reactions = [
    {
        'name':'hydrogen combust', # 0
        'reactants':[[3,4],[3,7],[3,9]], # list of combinations of elements that cause reaction
        'products':[4,-2], # what the particle turns into
        'reaction_difficulty':1 # lower the number, the higher the chance of reaction occuring per frame
    },
    {
        'name':'wood combust', # 1
        'reactants':[[6,4],[6,7],[6,9]],
        'products':[7,-2],
        'reaction_difficulty':7
    },
    {
        'name':'oil combust', # 2
        'reactants':[[8,4],[8,7],[8,9]],
        'products':[9,-2],
        'reaction_difficulty':4
    },
    {
        'name':'glass forging', # 3
        'reactants':[[0,4],[0,7],[0,9]],
        'products':[10,-2],
        'reaction_difficulty':50
    },
    {
        'name':'water evaporation', # 4
        'reactants':[[2,4],[2,7],[2,9]],
        'products':[11,-2],
        'reaction_difficulty':100
    }
]

class constants:
    WIDTH, HEIGHT = 1000, 500
    RESOLUTION = (WIDTH, HEIGHT)
    BACKGROUND = (0,0,0)
    FPS = 30
    DISPLAY = pygame.display.set_mode((WIDTH,HEIGHT))
    CLOCK = pygame.time.Clock()
    CELLSIZE = 20
    FLUID_STICKINESS = 1.2

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