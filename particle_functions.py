from project_settings import *
import pygame, sys
import random
from main import *

_rand = 0.5
def CreateParticle(particle:Particle):
    # places the particle in the main grid
    grid[str(particle.pos)] = particle
    if particleTypes[particle.type]['moveType'] != 'static':
        particle.active = True
        
    particle.fill = 1
        
    # sets a slightly random colour to the particle
    particle.colour = [particleTypes[particle.type]['colour']]
    
    # RANDOM COLOUR REMOVED DUE TO PERFORMANCE DEGRADE WHEN CREATING PARTICLES
    '''
    for i in particleTypes[particle.type]['colour']:
        
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

        particle.colour.append(i)'''


# function to set a certain grid cell to a particle, used in reactions or when user manuall places particles
def SetCell(particle:Particle,pos:list):
    grid[str(pos)] = particle
    particle.pos = pos
    
    if particleTypes[particle.type]['moveType'] == 'fluid':
        particle.fill = 0.5 / constants.FLUID_STICKINESS
        
    neighbours = [[particle.pos[0],particle.pos[1]+1],[particle.pos[0]+1,particle.pos[1]+1],[particle.pos[0]-1,particle.pos[1]+1],[particle.pos[0]+1,particle.pos[1]],[particle.pos[0]-1,particle.pos[1]],[particle.pos[0],particle.pos[1]-1],[particle.pos[0]+1,particle.pos[1]-1],[particle.pos[0]-1,particle.pos[1]-1]]
    if particleTypes[particle.type]['moveType'] != 'static':
        particle.active = True
    for n in neighbours:
        if str(n) in grid.keys():
            if particleTypes[grid[str(n)].type]['moveType'] != 'static':
                grid[str(n)].active = True

# function that simply clears a cell of its particle
def ClearCell(particle:Particle,pos:list):
    neighbours = [[particle.pos[0],particle.pos[1]+1],[particle.pos[0]+1,particle.pos[1]+1],[particle.pos[0]-1,particle.pos[1]+1],[particle.pos[0]+1,particle.pos[1]],[particle.pos[0]-1,particle.pos[1]],[particle.pos[0],particle.pos[1]-1],[particle.pos[0]+1,particle.pos[1]-1],[particle.pos[0]-1,particle.pos[1]-1]]
    for n in neighbours:
        if str(n) in grid.keys():
            if particleTypes[grid[str(n)].type]['moveType'] != 'static':
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
    
        # go opposite direction if the random direction has a particle there
    if str(neighbours['side1']) in grid.keys():
        direction = 0 - direction
    
    

    
    
        # move to cell below if it is empty
    if not str(neighbours['down']) in grid.keys() and particleTypes[particle.type]['density'] > 0:
        ClearCell(particle,particle.pos)
        SetCell(particle,neighbours['down'])
        moved=True
        
        # move to cell below if it has a particle with lower density
    elif str(neighbours['down']) in grid.keys() and particleTypes[grid[str(neighbours['down'])].type]['density'] < particleTypes[particle.type]['density']:
        ClearCell(particle,particle.pos)
        replacingParticle = grid[str(neighbours['down'])]
        ClearCell(grid[str(neighbours['down'])],neighbours['down'])
        SetCell(replacingParticle,particle.pos)
        SetCell(particle,neighbours['down'])
        moved=True

        # move to forward diagonal down cells if empty or lower density AND no particle forward (it would phase through otherwise)
    elif not str(neighbours['downdiagonal1']) in grid.keys() and particleTypes[particle.type]['density'] > 0 and not str(neighbours['side1']) in grid.keys():
        ClearCell(particle,particle.pos)
        SetCell(particle,neighbours['downdiagonal1'])
        moved=True
    elif str(neighbours['downdiagonal1']) in grid.keys() and particleTypes[grid[str(neighbours['downdiagonal1'])].type]['density'] < particleTypes[particle.type]['density'] and not str(neighbours['side1']) in grid.keys():
        ClearCell(particle,particle.pos)
        replacingParticle = grid[str(neighbours['downdiagonal1'])]
        ClearCell(grid[str(neighbours['downdiagonal1'])],neighbours['downdiagonal1'])
        SetCell(replacingParticle,particle.pos)
        SetCell(particle,neighbours['downdiagonal1'])
        moved=True

       # same as above but for behind
    elif not str(neighbours['downdiagonal2']) in grid.keys() and particleTypes[particle.type]['density'] > 0 and not str(neighbours['side1']) in grid.keys():
        ClearCell(particle,particle.pos)
        SetCell(particle,neighbours['downdiagonal2'])
        moved=True
    elif str(neighbours['downdiagonal2']) in grid.keys() and particleTypes[grid[str(neighbours['downdiagonal2'])].type]['density'] < particleTypes[particle.type]['density'] and not str(neighbours['side1']) in grid.keys():
        ClearCell(particle,particle.pos)
        replacingParticle = grid[str(neighbours['downdiagonal2'])]
        ClearCell(grid[str(neighbours['downdiagonal2'])],neighbours['downdiagonal2'])
        SetCell(replacingParticle,particle.pos)
        SetCell(particle,neighbours['downdiagonal2'])
        moved=True

    # same as above but for negative densities (gases)
    elif not str(neighbours['up']) in grid.keys() and particleTypes[particle.type]['density'] < 0:
        ClearCell(particle,particle.pos)
        SetCell(particle,neighbours['up'])
        moved=True
    
    elif not str(neighbours['updiagonal1']) in grid.keys() and particleTypes[particle.type]['density'] < 0:
        ClearCell(particle,particle.pos)
        SetCell(particle,neighbours['updiagonal1'])
        moved=True
    
    elif not str(neighbours['updiagonal2']) in grid.keys() and particleTypes[particle.type]['density'] < 0:
        ClearCell(particle,particle.pos)
        SetCell(particle,neighbours['updiagonal2'])
        moved=True
    
        

    # physics for FLUID particles (implementing the fill level & pressure simulation) (TEMPORARILY DISABLED FOR GASES)
    elif particleTypes[particle.type]['moveType'] == 'fluid' and particleTypes[particle.type]['density'] > 0:
        # fill particle below current if it is the same particle type & it is not fill > 1
        if particleTypes[particle.type]['density'] > 0 and grid[str(neighbours['down'])].type == particle.type and grid[str(neighbours['down'])].fill < 1:
            diff = clamp(1 - grid[str(neighbours['down'])].fill,0,particle.fill)
            grid[str(neighbours['down'])].fill += diff
            particle.fill -= diff
            moved=True
            
        # create & split water to particle in front if there is no particle there
        if not str(neighbours['side1']) in grid.keys():
            # SetCell(particle,neighbours['side1'])
            CreateParticle(Particle(neighbours['side1'],particle.type))
            grid[str(neighbours['side1'])].age = particle.age
            # grid[str(neighbours['side1'])].fill = particle.fill / 2
            # particle.fill = particle.fill / 2
            diff = clamp(particle.fill - grid[str(neighbours['side1'])].fill,0,0.5) / constants.FLUID_STICKINESS
            grid[str(neighbours['side1'])].fill = diff
            particle.fill -= diff
            moved=True
            
        # split water to particle in front if there is particle of same type there & fill is less than current particle
        elif grid[str(neighbours['side1'])].type == particle.type and grid[str(neighbours['side1'])].fill < particle.fill: # and not moved:
            diff = clamp(particle.fill - grid[str(neighbours['side1'])].fill,0,0.5) / constants.FLUID_STICKINESS
            grid[str(neighbours['side1'])].fill += diff
            particle.fill -= diff
            moved=True

        # same function as above but behind
        elif not str(neighbours['side2']) in grid.keys():
            # SetCell(particle,neighbours['side2'])
            CreateParticle(Particle(neighbours['side2'],particle.type))
            grid[str(neighbours['side2'])].age = particle.age
            # grid[str(neighbours['side2'])].fill = particle.fill / 2
            # particle.fill = particle.fill / 2

            diff = clamp(particle.fill - grid[str(neighbours['side2'])].fill,0,0.5) / constants.FLUID_STICKINESS
            grid[str(neighbours['side2'])].fill = diff
            particle.fill -= diff
            moved=True
         
        # same function as above but behind
        elif grid[str(neighbours['side2'])].type == particle.type and grid[str(neighbours['side1'])].fill < particle.fill: # and not moved:
            diff = clamp(particle.fill - grid[str(neighbours['side2'])].fill,0,0.5) / constants.FLUID_STICKINESS
            grid[str(neighbours['side2'])].fill += diff
            particle.fill -= diff
            moved=True
            
        if particle.fill > 1:
            if not str(neighbours['up']) in grid.keys():
                CreateParticle(Particle(neighbours['side1'],particle.type))
                grid[str(neighbours['up'])].fill = particle.fill-1
                particle.fill = 1
                moved=True
            elif grid[str(neighbours['up'])].type == particle.type:
                diff = clamp(particle.fill - grid[str(neighbours['side2'])].fill,0,0.5) / constants.FLUID_STICKINESS
                grid[str(neighbours['up'])].fill += diff
                particle.fill -= diff
                moved = True
            
        particle.shownFill = particle.fill
        
        #if not str(neighbours['down']) in grid.keys():
        #    particle.shownFill = 1
        #if str(neighbours['up']) in grid.keys() and grid[str(neighbours['up'])].type == particle.type:
        #    particle.shownFill = 1
        if particle.fill <= 0.01:
            ClearCell(particle, particle.pos)
        elif particle.fill < 1:
            particle.active = True
        elif particle.fill >= 1:
            particle.active = False
            
    elif particleTypes[particle.type]['density'] < 0:
        if not str(neighbours['side1']) in grid.keys():
            ClearCell(particle,particle.pos)
            SetCell(particle,neighbours['side1'])
            moved=True
            
        if not str(neighbours['side2']) in grid.keys():
            ClearCell(particle,particle.pos)
            SetCell(particle,neighbours['side2'])
            moved=True

    if not moved:
        particle.active = False
    return neighbours

def reaction_check(p:Particle,neighbours:dict):
    if len(particleTypes[p.type]['reactions']) > 0:
        for r in particleTypes[p.type]['reactions']:
            for i in reactions[r]['reactants']:
                if p.type in i:
                    for n in neighbours.values():
                        if str(n) in grid.keys() and p.type == grid[str(n)].type:
                            continue
                        elif str(n) in grid.keys() and grid[str(n)].type in i:
                            if randint(0,int(round(reactions[r]['reactionDifficulty']/clamp(p.fill,0.01,1)))) == 0:
                                reactants = [p,grid[str(n)]]
                                for x in reactants:
                                    if reactions[r]['products'][i.index(x.type)] == -1:
                                        ClearCell(x,x.pos)
                                        continue
                                    elif reactions[r]['products'][i.index(x.type)] == -2:
                                        continue
                                    else:
                                        try:
                                            del grid[str(x.pos)]
                                        except:
                                            pass
                                        pos = x.pos
                                        old_type = x.type
                                        del x
                                        CreateParticle(Particle(pos,reactions[r]['products'][i.index(old_type)]))
                                        
                                            
                else:
                    continue

def UpdateWorld():
    particles = list(grid.values())
    neighbours = {}
    for p in particles:
        if p.active:
            neighbours = move_particle(p)
            reaction_check(p,neighbours)
            if p.pos[1] < -1:
                try:
                    del grid[str(p.pos)]
                except:
                    pass
                del p
            #pygame.draw.rect(constants.DISPLAY,tuple(p.colour),(p.pos[0]*constants.CELLSIZE,p.pos[1]*constants.CELLSIZE,constants.CELLSIZE,constants.CELLSIZE))
        if p != None and particleTypes[p.type]['decay'] != None:
            if p.age > particleTypes[p.type]['decay'][1] and randint(0,4) == 0:
                try:
                    del grid[str(p.pos)]
                except:
                    pass
                if particleTypes[p.type]['decay'][0] != -1:
                    pos = p.pos
                    old_type = p.type
                    del p
                    CreateParticle(Particle(pos,particleTypes[old_type]['decay'][0]))
                    continue
                else:
                    del p
                    continue
        p.age += 1
        if particleTypes[p.type]['density'] < 0: # personally, gases look better as a solid colour but normal particles look better with varied colour
            p.colour = []
            for i in particleTypes[p.type]['colour']:
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
                p.colour.append(value)
                
        if p.prevFill != p.fill:
            p.active = True
            p.prevFill = p.fill
        #if p.active: 
        _fill = clamp(round(p.shownFill*constants.CELLSIZE)/constants.CELLSIZE,0,1)
        
# render fill level for gases upside down (as they should be) HOWEVER disabled due to fluid physics disable for gases
        '''
        if particleTypes[p.type]['density'] >= 0:
            pygame.draw.rect(constants.DISPLAY,tuple(p.colour),(p.pos[0]*constants.CELLSIZE,(p.pos[1]+(1-_fill))*(constants.CELLSIZE),constants.CELLSIZE,constants.CELLSIZE * _fill))
        else:
            pygame.draw.rect(constants.DISPLAY,tuple(p.colour),(p.pos[0]*constants.CELLSIZE,(p.pos[1]+(1+_fill))*(constants.CELLSIZE),constants.CELLSIZE,constants.CELLSIZE * _fill))
        '''
        if particleTypes[p.type]['moveType'] == 'fluid':
            pygame.draw.rect(constants.DISPLAY,tuple(p.colour),(p.pos[0]*constants.CELLSIZE,(p.pos[1]+(1-_fill))*(constants.CELLSIZE),constants.CELLSIZE,constants.CELLSIZE * _fill))
        else:
            pygame.draw.rect(constants.DISPLAY,tuple(p.colour),(p.pos[0]*constants.CELLSIZE,(p.pos[1])*(constants.CELLSIZE),constants.CELLSIZE,constants.CELLSIZE))

# basic clamp function which I use surprisingly a lot, clamps x to between y (the low) & z (the high)
def clamp(x,y,z) -> float:
    i = max(y, min(x, z))
    return i