from project_settings import *
import pygame, sys
import random
from main import *

def create_particle(particle:Particle) -> None:
    # creates a grid entry for the new particle
    grid[str(particle.pos)] = particle
    if particle_types[particle.type]['move_type'] != 'static':
        particle.active = True
        
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
def set_cell(particle:Particle,pos:list) -> None:
    grid[str(pos)] = particle
    particle.pos = pos
    neighbours = [[particle.pos[0],particle.pos[1]+1],[particle.pos[0]+1,particle.pos[1]+1],[particle.pos[0]-1,particle.pos[1]+1],[particle.pos[0]+1,particle.pos[1]],[particle.pos[0]-1,particle.pos[1]],[particle.pos[0],particle.pos[1]-1],[particle.pos[0]+1,particle.pos[1]-1],[particle.pos[0]-1,particle.pos[1]-1]]
    if particle_types[particle.type]['move_type'] != 'static':
        particle.active = True
    for n in neighbours:
        if str(n) in grid.keys():
            if particle_types[grid[str(n)].type]['move_type'] != 'static':
                grid[str(n)].active = True

# function that simply clears a cell of its particle
def clear_cell(particle:Particle,pos:list) -> None:
    neighbours = [[particle.pos[0],particle.pos[1]+1],[particle.pos[0]+1,particle.pos[1]+1],[particle.pos[0]-1,particle.pos[1]+1],[particle.pos[0]+1,particle.pos[1]],[particle.pos[0]-1,particle.pos[1]],[particle.pos[0],particle.pos[1]-1],[particle.pos[0]+1,particle.pos[1]-1],[particle.pos[0]-1,particle.pos[1]-1]]
    for n in neighbours:
        if str(n) in grid.keys():
            if particle_types[grid[str(n)].type]['move_type'] != 'static':
                grid[str(n)].active = True
    del grid[str(pos)]

# function that moves "active" particles following a simple pattern
def move_particle(particle:Particle) -> dict:
    global moved
    moved = False
    
# simulate (very) simple waves for fluids, or random for powders (which makes them behave naturally still)
    direction = randint(0,1)
    if direction == 0:
        direction = -1
    if particle_types[particle.type]['move_type'] == 'fluid':
        if particle.velocity[0] == 0 and particle.active:
            particle.velocity[0] = direction
        elif particle.velocity[0] != 0:
            direction = particle.velocity[0]
            
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
    
    

    
    

    if not str(neighbours['down']) in grid.keys() and particle_types[particle.type]['density'] > 0:
        clear_cell(particle,particle.pos)
        set_cell(particle,neighbours['down'])
        moved=True
    elif str(neighbours['down']) in grid.keys() and particle_types[grid[str(neighbours['down'])].type]['density'] < particle_types[particle.type]['density']:
        clear_cell(particle,particle.pos)
        replacing_particle = grid[str(neighbours['down'])]
        clear_cell(grid[str(neighbours['down'])],neighbours['down'])
        set_cell(replacing_particle,particle.pos)
        set_cell(particle,neighbours['down'])
        moved=True

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

    # there is no need for having things behave like bubbles as the behaviour is natural in the density simulation
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

    elif particle_types[particle.type]['move_type'] == 'fluid':
        if not str(neighbours['side1']) in grid.keys():
            clear_cell(particle,particle.pos)
            set_cell(particle,neighbours['side1'])
            moved=True
        elif str(neighbours['side1']) in grid.keys() and particle_types[grid[str(neighbours['side1'])].type]['density'] < particle_types[particle.type]['density']:
            clear_cell(particle,particle.pos)
            replacing_particle = grid[str(neighbours['side1'])]
            clear_cell(grid[str(neighbours['side1'])],neighbours['side1'])
            set_cell(replacing_particle,particle.pos)
            set_cell(particle,neighbours['side1'])
            moved=True

        elif not str(neighbours['side2']) in grid.keys():
            clear_cell(particle,particle.pos)
            set_cell(particle,neighbours['side2'])
            moved=True
        elif str(neighbours['side2']) in grid.keys() and particle_types[grid[str(neighbours['side2'])].type]['density'] < particle_types[particle.type]['density']:
            clear_cell(particle,particle.pos)
            replacing_particle = grid[str(neighbours['side2'])]
            clear_cell(grid[str(neighbours['side2'])],neighbours['side2'])
            set_cell(replacing_particle,particle.pos)
            set_cell(particle,neighbours['side2'])
            moved=True
    if not moved:
        particle.active = False
    return neighbours

def reaction_check(p:Particle,neighbours:dict) -> None:
    if len(particle_types[p.type]['reactions']) > 0:
        for r in particle_types[p.type]['reactions']:
            for i in reactions[r]['reactants']:
                if p.type in i:
                    for n in neighbours.values():
                        if str(n) in grid.keys() and p.type == grid[str(n)].type:
                            continue
                        elif str(n) in grid.keys() and grid[str(n)].type in i:
                            if randint(0,reactions[r]['reaction_difficulty']) == 0:
                                reactants = [p,grid[str(n)]]
                                for x in reactants:
                                    if reactions[r]['products'][i.index(x.type)] == -1:
                                        clear_cell(x,x.pos)
                                        continue
                                    elif reactions[r]['products'][i.index(x.type)] == -2:
                                        continue
                                    else:
                                        del grid[str(x.pos)]
                                        pos = x.pos
                                        old_type = x.type
                                        del x
                                        create_particle(Particle(pos,reactions[r]['products'][i.index(old_type)]))
                                        
                                            
                else:
                    continue

def update_world() -> None:
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
                    del grid[str(p.pos)]
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
        if particle_types[p.type]['density'] < 0:
            p.color = []
            for i in particle_types[p.type]['color']:
                sign = randint(0,1)
                if sign == 0:
                    sign = -1
                value = i+randint(0,10)*sign
                if value > 255:
                    value = 255
                if value < 0:
                    value = 0
                p.color.append(value)
        pygame.draw.rect(constants.DISPLAY,tuple(p.color),(p.pos[0]*constants.CELLSIZE,p.pos[1]*constants.CELLSIZE,constants.CELLSIZE,constants.CELLSIZE))
