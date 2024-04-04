from project_settings import *
import pygame, sys
import random
from main import *

def create_particle(particle:Particle):
    # places the particle in the main grid
    grid[str(particle.pos)] = particle
    if particle_types[particle.type]['move_type'] != 'static':
        particle.active = True
        
    particle.fill = 1
        
    # sets a slightly random colour to the particle
    particle.color = []
    for i in particle_types[particle.type]['color']:
        sign = random.getrandbits(4) # using getrandbits because it is more optimised (main bottleneck of this function is getting a random number)
        multi = sign
        if sign < 8:
            multi = -1
        else:
            multi = 1
        value = i + (sign / 2 * multi)
        if value > 255:
            value = 255
        if value < 0:
            value = 0
        
        particle.color.append(value)

# function to set a certain grid cell to a particle, used in reactions or when user manuall places particles
def set_cell(particle:Particle,pos:list):
    grid[str(pos)] = particle
    particle.pos = pos
    particle.fill = 1
    neighbours = [[particle.pos[0],particle.pos[1]+1],[particle.pos[0]+1,particle.pos[1]+1],[particle.pos[0]-1,particle.pos[1]+1],[particle.pos[0]+1,particle.pos[1]],[particle.pos[0]-1,particle.pos[1]],[particle.pos[0],particle.pos[1]-1],[particle.pos[0]+1,particle.pos[1]-1],[particle.pos[0]-1,particle.pos[1]-1]]
    if particle_types[particle.type]['move_type'] != 'static':
        particle.active = True
    for n in neighbours:
        if str(n) in grid.keys():
            if particle_types[grid[str(n)].type]['move_type'] != 'static':
                grid[str(n)].active = True

# function that simply clears a cell of its particle
def clear_cell(particle:Particle,pos:list):
    neighbours = [[particle.pos[0],particle.pos[1]+1],[particle.pos[0]+1,particle.pos[1]+1],[particle.pos[0]-1,particle.pos[1]+1],[particle.pos[0]+1,particle.pos[1]],[particle.pos[0]-1,particle.pos[1]],[particle.pos[0],particle.pos[1]-1],[particle.pos[0]+1,particle.pos[1]-1],[particle.pos[0]-1,particle.pos[1]-1]]
    for n in neighbours:
        if str(n) in grid.keys():
            if particle_types[grid[str(n)].type]['move_type'] != 'static':
                grid[str(n)].active = True
    del grid[str(pos)]

# function to move particles based on the "rules" of this CA
def move_particle(particle:Particle) -> dict:
    global moved
    moved = False

    # direction determines the way the particle is "looking", either left or right.
    direction = randint(0,1)
    if direction == 0:
        direction = -1
            
    neighbours = { # left/right is relative to which dir was picked to go first by the randint
        'down' : [particle.pos[0],particle.pos[1]+1],
        'downdiagonal1' : [particle.pos[0]+direction,particle.pos[1]+1],
        'downdiagonal2' : [particle.pos[0]-direction,particle.pos[1]+1],
        'side1' : [particle.pos[0]+direction,particle.pos[1]],
        'side2' : [particle.pos[0]-direction,particle.pos[1]],
        'up' : [particle.pos[0],particle.pos[1]-1],
        'updiagonal1' : [particle.pos[0]+direction,particle.pos[1]-1],
        'updiagonal2' : [particle.pos[0]-direction,particle.pos[1]-1]}
    
    if str(neighbours['side1']) in grid.keys():
        direction = 0 - direction
    
    

    
    
        # move to cell below if it is empty
    if not str(neighbours['down']) in grid.keys() and particle_types[particle.type]['density'] > 0:
        clear_cell(particle,particle.pos)
        set_cell(particle,neighbours['down'])
        moved=True
        
        # move to cell below if it has a particle with lower density
    elif str(neighbours['down']) in grid.keys() and particle_types[grid[str(neighbours['down'])].type]['density'] < particle_types[particle.type]['density']:
        clear_cell(particle,particle.pos)
        replacing_particle = grid[str(neighbours['down'])]
        clear_cell(grid[str(neighbours['down'])],neighbours['down'])
        set_cell(replacing_particle,particle.pos)
        set_cell(particle,neighbours['down'])
        moved=True

        # move to diagonal down cells if empty or lower density
    elif not str(neighbours['downdiagonal1']) in grid.keys() and particle_types[particle.type]['density'] > 0:
        clear_cell(particle,particle.pos)
        set_cell(particle,neighbours['downdiagonal1'])
        moved=True
    elif str(neighbours['downdiagonal1']) in grid.keys() and particle_types[grid[str(neighbours['downdiagonal1'])].type]['density'] < particle_types[particle.type]['density']:
        clear_cell(particle,particle.pos)
        replacing_particle = grid[str(neighbours['downdiagonal1'])]
        clear_cell(grid[str(neighbours['downdiagonal1'])],neighbours['downdiagonal1'])
        set_cell(replacing_particle,particle.pos)
        set_cell(particle,neighbours['downdiagonal1'])
        moved=True

       
    elif not str(neighbours['downdiagonal2']) in grid.keys() and particle_types[particle.type]['density'] > 0:
        clear_cell(particle,particle.pos)
        set_cell(particle,neighbours['downdiagonal2'])
        moved=True
    elif str(neighbours['downdiagonal2']) in grid.keys() and particle_types[grid[str(neighbours['downdiagonal2'])].type]['density'] < particle_types[particle.type]['density']:
        clear_cell(particle,particle.pos)
        replacing_particle = grid[str(neighbours['downdiagonal2'])]
        clear_cell(grid[str(neighbours['downdiagonal2'])],neighbours['downdiagonal2'])
        set_cell(replacing_particle,particle.pos)
        set_cell(particle,neighbours['downdiagonal2'])
        moved=True

    # same as above but for negative densities (gases)
    elif not str(neighbours['up']) in grid.keys() and particle_types[particle.type]['density'] < 0:
        clear_cell(particle,particle.pos)
        set_cell(particle,neighbours['up'])
        moved=True
    
    elif not str(neighbours['updiagonal1']) in grid.keys() and particle_types[particle.type]['density'] < 0:
        clear_cell(particle,particle.pos)
        set_cell(particle,neighbours['updiagonal1'])
        moved=True
    
    elif not str(neighbours['updiagonal2']) in grid.keys() and particle_types[particle.type]['density'] < 0:
        clear_cell(particle,particle.pos)
        set_cell(particle,neighbours['updiagonal2'])
        moved=True
    
        

    # physics for FLUID particles (implementing the fill level & pressure simulation)
    elif particle_types[particle.type]['move_type'] == 'fluid':
        if particle_types[particle.type]['density'] > 0 and grid[str(neighbours['down'])].type == particle.type and grid[str(neighbours['down'])].fill < 1:
            diff = clamp(1 - grid[str(neighbours['down'])].fill,0,particle.fill)
            grid[str(neighbours['down'])].fill += diff
            particle.fill -= diff
            moved=True
            

        if not str(neighbours['side1']) in grid.keys():
            # set_cell(particle,neighbours['side1'])
            create_particle(Particle(neighbours['side1'],particle.type))
            grid[str(neighbours['side1'])].age = particle.age
            grid[str(neighbours['side1'])].fill = particle.fill / 2
            particle.fill = particle.fill / 2
            moved=True
        elif grid[str(neighbours['side1'])].type == particle.type:
            diff = (particle.fill - grid[str(neighbours['side1'])].fill) / constants.FLUID_STICKINESS
            grid[str(neighbours['side1'])].fill += diff
            particle.fill -= diff
            moved=True

        elif not str(neighbours['side2']) in grid.keys():
            # set_cell(particle,neighbours['side2'])
            create_particle(Particle(neighbours['side2'],particle.type))
            grid[str(neighbours['side2'])].age = particle.age
            grid[str(neighbours['side2'])].fill = particle.fill / 2
            particle.fill = particle.fill / 2
            moved=True
        elif grid[str(neighbours['side2'])].type == particle.type:
            diff = (particle.fill - grid[str(neighbours['side2'])].fill) / constants.FLUID_STICKINESS
            grid[str(neighbours['side2'])].fill += diff
            particle.fill -= diff
            moved=True
            
        if particle.fill > 1:
            if not str(neighbours['up']) in grid.keys():
                create_particle(Particle(neighbours['side1'],particle.type))
                grid[str(neighbours['up'])].fill = particle.fill-1
                particle.fill -= particle.fill-1
                moved=True
            
        particle.shownFill = particle.fill
        
        if str(neighbours['up']) in grid.keys() or not str(neighbours['down']) in grid.keys():
            particle.shownFill = 1
        if particle.fill <= 0:
            clear_cell(particle, particle.pos)
        elif particle.fill < 1:
            particle.active = True
        elif particle.fill == 1:
            particle.active = False
    if not moved:
        particle.active = False
    return neighbours

def reaction_check(p:Particle,neighbours:dict):
    if len(particle_types[p.type]['reactions']) > 0:
        for r in particle_types[p.type]['reactions']:
            for i in reactions[r]['reactants']:
                if p.type in i:
                    for n in neighbours.values():
                        if str(n) in grid.keys() and p.type == grid[str(n)].type:
                            continue
                        elif str(n) in grid.keys() and grid[str(n)].type in i:
                            if randint(0,int(round(reactions[r]['reaction_difficulty']/clamp(p.fill,0.01,1)))) == 0:
                                reactants = [p,grid[str(n)]]
                                for x in reactants:
                                    if reactions[r]['products'][i.index(x.type)] == -1:
                                        clear_cell(x,x.pos)
                                        continue
                                    elif reactions[r]['products'][i.index(x.type)] == -2:
                                        continue
                                    else:
                                        if grid[str(x.pos)] != None:
                                                del grid[str(x.pos)]
                                        pos = x.pos
                                        old_type = x.type
                                        del x
                                        create_particle(Particle(pos,reactions[r]['products'][i.index(old_type)]))
                                        
                                            
                else:
                    continue

def update_world():
    particles = list(grid.values())
    neighbours = {}
    for p in particles:
        if p.active:
            neighbours = move_particle(p)
            reaction_check(p,neighbours)
            #pygame.draw.rect(constants.DISPLAY,tuple(p.color),(p.pos[0]*constants.CELLSIZE,p.pos[1]*constants.CELLSIZE,constants.CELLSIZE,constants.CELLSIZE))
        if particle_types[p.type]['decay'] != None:
            if p.age > particle_types[p.type]['decay'][1] and randint(0,4) == 0:
                if particle_types[p.type]['decay'][0] != -1:
                    try:
                        del grid[str(p.pos)]
                    except:
                        pass
                    pos = p.pos
                    old_type = p.type
                    del p
                    create_particle(Particle(pos,particle_types[old_type]['decay'][0]))
                    continue
                else:
                    del grid[str(p.pos)]
                    del p
                    continue
        p.age += 1
        if particle_types[p.type]['density'] < 0: # personally, gases look better as a solid colour but normal particles look better with varied colour
            p.color = []
            for i in particle_types[p.type]['color']:
                sign = random.getrandbits(4) # using getrandbits because it is more optimised (main bottleneck of this function is getting a random number)
                multi = sign
                if sign < 8:
                    multi = -1
                else:
                    multi = 1
                value = i + (sign / 2 * multi)
                if value > 255:
                    value = 255
                if value < 0:
                    value = 0
                p.color.append(value)
                
        if p.prevFill != p.fill:
            p.active = True
            p.prevFill = p.fill
        #if p.active: 
        _fill = clamp(round(p.shownFill*constants.CELLSIZE)/constants.CELLSIZE,0,1)
        pygame.draw.rect(constants.DISPLAY,tuple(p.color),(p.pos[0]*constants.CELLSIZE,(p.pos[1]+(1-_fill))*(constants.CELLSIZE),constants.CELLSIZE,constants.CELLSIZE * _fill))

# basic clamp function which I use surprisingly a lot, clamps x to between y (the low) & z (the high)
def clamp(x,y,z) -> float:
    i = max(y, min(x, z))
    return i