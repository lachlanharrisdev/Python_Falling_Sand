import pygame, sys
pygame.init()

particle_types = [ # air has density of 0, negative values float to top, positive fall
    {
        'name':'sand', # 0
        'move_type':'powder', # how the particle moves
        'color':(235,225,52), # average particle colour
        'density':1.6, # how dense the particle is
        'reactions':[3], # list of reactions it is a part of (just for optimisation)
        'decay':None, # what it will decay into after amount of frames [decay_into,decay_min_age]
        'move_resistance':1 # EXPERIMENTAL how resistant it is to movement & explosions
    },
    {
        'name':'wall', # 1
        'move_type':'static',
        'color':(100,100,100),
        'density':100, # infinity
        'reactions':[],
        'decay':None,
        'move_resistance':100
    },
    {
        'name':'water', # 2
        'move_type':'fluid',
        'color':(50,50,255),
        'density':1 ,
        'reactions':[],
        'decay':None,
        'move_resistance':2
    },
    {
        'name':'hydrogen', # 3
        'move_type':'fluid',
        'color':(200,50,50),
        'density':-1,
        'reactions':[0],
        'decay':None,
        'move_resistance':1
    },
    {
        'name':'fire_gas', # 4
        'move_type':'fluid',
        'color':(235,110,52),
        'density':-1,
        'reactions':[0,1,2],
        'decay':[5,8] 
    },
    {
        'name':'smoke', # 5
        'move_type':'fluid',
        'color':(75,75,75),
        'density':-1,
        'reactions':[],
        'decay':[-1,24],
        'move_resistance':1
    },
    {
        'name':'wood', # 6
        'move_type':'static',
        'color':(168,100,50),
        'density':100, # all solids density is max
        'reactions':[1],
        'decay':None,
        'move_resistance':3
    },
    {
        'name':'fire_solid', # 7
        'move_type':'static',
        'color':(235,110,52),
        'density':100,
        'reactions':[],
        'decay':[4,20],
        'move_resistance':1
    },
    {
        'name':'oil', # 8
        'move_type':'fluid',
        'color':(168,133,50),
        'density':0.7,
        'reactions':[2],
        'decay':None,
        'move_resistance':2
    },
    {
        'name':'fire_liquid', # 9
        'move_type':'fluid',
        'color':(235,110,52),
        'density':0.9,
        'reactions':[],
        'decay':[4,20],
        'move_resistance':1
    },
    {
        'name':'glass', # 10
        'move_type':'static',
        'color':(240,240,255),
        'density':2.5,
        'reactions':[3],
        'decay':None,
        'move_resistance':10
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
    }
]

class constants:
    WIDTH, HEIGHT = 1000, 500
    RESOLUTION = (WIDTH, HEIGHT)
    BACKGROUND = (0,0,0)
    FPS = 30
    DISPLAY = pygame.display.set_mode((WIDTH,HEIGHT))
    CLOCK = pygame.time.Clock()
    CELLSIZE = 10

class Particle:
    def __init__(self,pos,particle_type):
        self.pos = pos # position on the tile grid
        self.type = particle_type # how the tile moves
        self.active = False # if the particle should calculate movement in the current frame (for optimisation)
        self.age = 0 # lifetime of the particle in frames, used for particle decay
        self.color = [] # rgb colour value of this particle (for the slightly random colour)
        self.velocity = [0,0] # EXPERIMENTAL used to simulate waves in fluids, or explosions / wind in other materials