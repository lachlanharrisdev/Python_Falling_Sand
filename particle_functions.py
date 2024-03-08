from project_settings import *
import pygame, sys
from random import randint
from main import *

def create_particle(particle:Particle) -> None:
    # creates a grid entry for the new particle
    grid[str(particle.pos)] = particle
    if particle_types[particle.type]['move_type'] != 'static':
        particle.active = True
        
    # sets a slightly random colour to the particle
    particle.color = []
    for i in particle_types[particle.type]['color']:
        sign = randint(0,1)
        if sign == 0:
            sign = -1
        value = i+randint(0,10)*sign
        if value > 255:
            value = 255
        if value < 0:
            value = 0
        particle.color.append(value)

# function to set a certain grid cell to a particle, used in reactions or when user manuall places particles
def set_cell(particle:Particle,pos:list) -> None:
    grid[str(pos)] = particle
    particle.pos = pos
    neighbors = [[particle.pos[0],particle.pos[1]+1],[particle.pos[0]+1,particle.pos[1]+1],[particle.pos[0]-1,particle.pos[1]+1],[particle.pos[0]+1,particle.pos[1]],[particle.pos[0]-1,particle.pos[1]],[particle.pos[0],particle.pos[1]-1],[particle.pos[0]+1,particle.pos[1]-1],[particle.pos[0]-1,particle.pos[1]-1]]
    if particle_types[particle.type]['move_type'] != 'static':
        particle.active = True
    for n in neighbors:
        if str(n) in grid.keys():
            if particle_types[grid[str(n)].type]['move_type'] != 'static':
                grid[str(n)].active = True

# function that simply clears a cell of its particle
def clear_cell(particle:Particle,pos:list) -> None:
    neighbors = [[particle.pos[0],particle.pos[1]+1],[particle.pos[0]+1,particle.pos[1]+1],[particle.pos[0]-1,particle.pos[1]+1],[particle.pos[0]+1,particle.pos[1]],[particle.pos[0]-1,particle.pos[1]],[particle.pos[0],particle.pos[1]-1],[particle.pos[0]+1,particle.pos[1]-1],[particle.pos[0]-1,particle.pos[1]-1]]
    for n in neighbors:
        if str(n) in grid.keys():
            if particle_types[grid[str(n)].type]['move_type'] != 'static':
                grid[str(n)].active = True
    del grid[str(pos)]

# function that moves "active" particles following a simple pattern
def move_particle(particle:Particle) -> dict: # its possible particles can move twice if they were displaced by another particle falling and then they moved, this probably can be fixed with a "moved" bool property that says if the particle moved that frame already
    global moved
    moved = False
    direction = randint(0,1)
    if direction == 0:
        direction = -1
    neighbors = { # left/right is relative to which dir was picked to go first by the randint
        'down' : [particle.pos[0],particle.pos[1]+1],
        'downdiagonal1' : [particle.pos[0]+direction,particle.pos[1]+1],
        'downdiagonal2' : [particle.pos[0]-direction,particle.pos[1]+1],
        'side1' : [particle.pos[0]+direction,particle.pos[1]],
        'side2' : [particle.pos[0]-direction,particle.pos[1]],
        'up' : [particle.pos[0],particle.pos[1]-1],
        'updiagonal1' : [particle.pos[0]+direction,particle.pos[1]-1],
        'updiagonal2' : [particle.pos[0]-direction,particle.pos[1]-1]}

    if not str(neighbors['down']) in grid.keys() and particle_types[particle.type]['density'] > 0:
        clear_cell(particle,particle.pos)
        set_cell(particle,neighbors['down'])
        moved=True
    elif str(neighbors['down']) in grid.keys() and particle_types[grid[str(neighbors['down'])].type]['density'] < particle_types[particle.type]['density']:
        clear_cell(particle,particle.pos)
        replacing_particle = grid[str(neighbors['down'])]
        clear_cell(grid[str(neighbors['down'])],neighbors['down'])
        set_cell(replacing_particle,particle.pos)
        set_cell(particle,neighbors['down'])
        moved=True

    elif not str(neighbors['downdiagonal1']) in grid.keys() and particle_types[particle.type]['density'] > 0:
        clear_cell(particle,particle.pos)
        set_cell(particle,neighbors['downdiagonal1'])
        moved=True
    elif str(neighbors['downdiagonal1']) in grid.keys() and particle_types[grid[str(neighbors['downdiagonal1'])].type]['density'] < particle_types[particle.type]['density']:
        clear_cell(particle,particle.pos)
        replacing_particle = grid[str(neighbors['downdiagonal1'])]
        clear_cell(grid[str(neighbors['downdiagonal1'])],neighbors['downdiagonal1'])
        set_cell(replacing_particle,particle.pos)
        set_cell(particle,neighbors['downdiagonal1'])
        moved=True

    elif not str(neighbors['downdiagonal2']) in grid.keys() and particle_types[particle.type]['density'] > 0:
        clear_cell(particle,particle.pos)
        set_cell(particle,neighbors['downdiagonal2'])
        moved=True
    elif str(neighbors['downdiagonal2']) in grid.keys() and particle_types[grid[str(neighbors['downdiagonal2'])].type]['density'] < particle_types[particle.type]['density']:
        clear_cell(particle,particle.pos)
        replacing_particle = grid[str(neighbors['downdiagonal2'])]
        clear_cell(grid[str(neighbors['downdiagonal2'])],neighbors['downdiagonal2'])
        set_cell(replacing_particle,particle.pos)
        set_cell(particle,neighbors['downdiagonal2'])
        moved=True

    # there is no need for having things behave like bubbles as the behaviour is natural in the density simulation
    elif not str(neighbors['up']) in grid.keys() and particle_types[particle.type]['density'] < 0:
        clear_cell(particle,particle.pos)
        set_cell(particle,neighbors['up'])
        moved=True
    
    elif not str(neighbors['updiagonal1']) in grid.keys() and particle_types[particle.type]['density'] < 0:
        clear_cell(particle,particle.pos)
        set_cell(particle,neighbors['updiagonal1'])
        moved=True
    
    elif not str(neighbors['updiagonal2']) in grid.keys() and particle_types[particle.type]['density'] < 0:
        clear_cell(particle,particle.pos)
        set_cell(particle,neighbors['updiagonal2'])
        moved=True

    elif particle_types[particle.type]['move_type'] == 'fluid':
        if not str(neighbors['side1']) in grid.keys():
            clear_cell(particle,particle.pos)
            set_cell(particle,neighbors['side1'])
            moved=True
        elif str(neighbors['side1']) in grid.keys() and particle_types[grid[str(neighbors['side1'])].type]['density'] < particle_types[particle.type]['density']:
            clear_cell(particle,particle.pos)
            replacing_particle = grid[str(neighbors['side1'])]
            clear_cell(grid[str(neighbors['side1'])],neighbors['side1'])
            set_cell(replacing_particle,particle.pos)
            set_cell(particle,neighbors['side1'])
            moved=True

        elif not str(neighbors['side2']) in grid.keys():
            clear_cell(particle,particle.pos)
            set_cell(particle,neighbors['side2'])
            moved=True
        elif str(neighbors['side2']) in grid.keys() and particle_types[grid[str(neighbors['side2'])].type]['density'] < particle_types[particle.type]['density']:
            clear_cell(particle,particle.pos)
            replacing_particle = grid[str(neighbors['side2'])]
            clear_cell(grid[str(neighbors['side2'])],neighbors['side2'])
            set_cell(replacing_particle,particle.pos)
            set_cell(particle,neighbors['side2'])
            moved=True
    if not moved:
        particle.active = False
    return neighbors

def reaction_check(p:Particle,neighbors:dict) -> None:
    if len(particle_types[p.type]['reactions']) > 0:
        for r in particle_types[p.type]['reactions']:
            for i in reactions[r]['reactants']:
                if p.type in i:
                    for n in neighbors.values():
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
                                        for m in neighbors.values():
                                            if not m.type == 'static':
                                                m.active = True
                                            
                else:
                    continue

def update_world() -> None:
    particles = list(grid.values())
    neighbors = {}
    for p in particles:
        if p.active:
            neighbors = move_particle(p)
            reaction_check(p,neighbors)
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
