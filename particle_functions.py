# hello sir
# i've used a lot of c# coding conventions (unity) so sorry if it's confusing
# also i have used more modules than just pygame/sys but I believe they come installed with python
# i've copied & pasted this to the top of every script just so you see this
# pls give me bonus marks for not using AI :)

# this script manages all the functions for managing individual particle functions & organising the grid. basically the front-end game logic

# CELL - an individual cell, cannot be created or deleted but have values changed
# PARTICLE - a movable, destroyable, reactable & decayable object that takes the position of a cell

from math import ceil
from project_settings import *
import pygame, sys
import random
from main import *

def CreateParticle(particle:Particle, _fill=1):
    # creates a NEW particle & places it on the main grid, used when manually placing particles & with fluids spreading
    if not str(particle.pos) in grid.keys():
        grid[str(particle.pos)] = particle
        if particleTypes[particle.type]['moveType'] != 'static':
            particle.active = True
        else:
            try:
                if randint(0,2) == 0:
                    particleTypes[particle.type]['sound'].play()
            except:
                pass
        
        particle.fill = _fill
    
        particle.colour = [particleTypes[particle.type]['colour']]
    

# <summary>
# function to set a certain grid cell to a PRE-EXISTING particle, used when moving powders, swapping particles with density differences & reactions
# </summary>    
def SetCell(particle:Particle,pos:list,age=0,_fill=0.5):
    grid[str(pos)] = particle
    particle.pos = pos
    
    if particleTypes[particle.type]['moveType'] == 'fluid': # when fluids are splitting into new particles to spread, this line ensures no extra fluid is created
        particle.fill = _fill
        
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
    if not (pos[0] == 0 or pos[0] == int(constants.WIDTH / constants.CELLSIZE)-1 or pos[1] == 0 or pos[1] == int(constants.HEIGHT / constants.CELLSIZE)-1):
        try:
            del grid[str(pos)]
        except:
            pass
    '''try:
        if (pos.x == 0 | pos.x == constants.WIDTH / constants.CELLSIZE) | (pos.y == 0 | pos.y == constants.WIDTH / constants.CELLSIZE):
            del grid[str(pos)]
    except:
        pass'''

# <summary>
# absolutely chonkiest & most spaghetti function you'll see in here. holds all of the cellular automata rules & applies them based on neighbours, particle properties, etc.
# </summary>    
def MoveParticle(particle:Particle) -> dict:
    global moved
    moved = False
    
    if particleTypes[particle.type]['moveType'] == 'static':
        return

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
        SetCell(particle,neighbours['down'],particle.age,particle.fill)
        moved=True
        particle.state = "falling"
        
        # move to cell below if it has a particle with lower density
    elif str(neighbours['down']) in grid.keys() and particleTypes[grid[str(neighbours['down'])].type]['density'] < particleTypes[particle.type]['density']:
        ClearCell(particle,particle.pos)
        replacingParticle = grid[str(neighbours['down'])]
        ClearCell(grid[str(neighbours['down'])],neighbours['down'])
        SetCell(replacingParticle,particle.pos,replacingParticle.age,replacingParticle.fill)
        SetCell(particle,neighbours['down'],particle.age,particle.fill)
        moved=True
        particle.state = "falling"

        # move to forward diagonal down cells if empty or lower density AND no particle forward (it would phase through otherwise)
    elif not str(neighbours['downdiagonal1']) in grid.keys() and particleTypes[particle.type]['density'] > 0 and not str(neighbours['side1']) in grid.keys():
        ClearCell(particle,particle.pos)
        SetCell(particle,neighbours['downdiagonal1'],particle.age,particle.fill)
        moved=True
        particle.state = "rolling"
    elif str(neighbours['downdiagonal1']) in grid.keys() and particleTypes[grid[str(neighbours['downdiagonal1'])].type]['density'] < particleTypes[particle.type]['density'] and not str(neighbours['side1']) in grid.keys():
        ClearCell(particle,particle.pos)
        replacingParticle = grid[str(neighbours['downdiagonal1'])]
        ClearCell(grid[str(neighbours['downdiagonal1'])],neighbours['downdiagonal1'])
        SetCell(replacingParticle,particle.pos,replacingParticle.age,replacingParticle.fill)
        SetCell(particle,neighbours['downdiagonal1'],particle.age,particle.fill)
        moved=True
        particle.state = "rolling"

       # same as above but for behind
    elif not str(neighbours['downdiagonal2']) in grid.keys() and particleTypes[particle.type]['density'] > 0 and not str(neighbours['side1']) in grid.keys():
        ClearCell(particle,particle.pos)
        SetCell(particle,neighbours['downdiagonal2'],particle.age)
        moved=True
        particle.state = "rolling"
    elif str(neighbours['downdiagonal2']) in grid.keys() and particleTypes[grid[str(neighbours['downdiagonal2'])].type]['density'] < particleTypes[particle.type]['density'] and not str(neighbours['side1']) in grid.keys():
        ClearCell(particle,particle.pos)
        replacingParticle = grid[str(neighbours['downdiagonal2'])]
        ClearCell(grid[str(neighbours['downdiagonal2'])],neighbours['downdiagonal2'])
        SetCell(replacingParticle,particle.pos,replacingParticle.age,replacingParticle.fill)
        SetCell(particle,neighbours['downdiagonal2'],particle.age,particle.fill)
        moved=True
        particle.state = "rolling"

    # same as above but for negative densities (gases)
    elif not str(neighbours['up']) in grid.keys() and particleTypes[particle.type]['density'] < 0:
        ClearCell(particle,particle.pos)
        SetCell(particle,neighbours['up'])
        moved=True
        particle.state = "falling"
    
    elif not str(neighbours['updiagonal1']) in grid.keys() and particleTypes[particle.type]['density'] < 0:
        ClearCell(particle,particle.pos)
        SetCell(particle,neighbours['updiagonal1'])
        moved=True
        particle.state = "falling"
    
    elif not str(neighbours['updiagonal2']) in grid.keys() and particleTypes[particle.type]['density'] < 0:
        ClearCell(particle,particle.pos)
        SetCell(particle,neighbours['updiagonal2'])
        moved=True
        particle.state = "falling"
    
        

    # physics for FLUID particles (implementing the fill level & pressure simulation)
    elif particleTypes[particle.type]['moveType'] == 'fluid' and particleTypes[particle.type]['density'] > 0:
        # fill particle below current if it is the same particle type & it is not fill > 1
        if particleTypes[particle.type]['density'] > 0 and grid[str(neighbours['down'])].type == particle.type and grid[str(neighbours['down'])].fill < 1:
            diff = Clamp(1 - grid[str(neighbours['down'])].fill,0,particle.fill)
            grid[str(neighbours['down'])].fill += diff
            particle.fill -= diff
            moved=True
            particle.state = "filling"
            
        # create & split water to particle in front if there is no particle there
        if not str(neighbours['side1']) in grid.keys():
            # SetCell(particle,neighbours['side1'])
            CreateParticle(Particle(neighbours['side1'],particle.type), )
            grid[str(neighbours['side1'])].age = particle.age
            # grid[str(neighbours['side1'])].fill = particle.fill / 2
            # particle.fill = particle.fill / 2
            diff = Clamp(particle.fill,0,0.5) / constants.FLUID_STICKINESS
            grid[str(neighbours['side1'])].fill = diff
            particle.fill -= diff
            moved=True
            particle.state = "filling"
            
        # split water to particle in front if there is particle of same type there & fill is less than current particle
        elif grid[str(neighbours['side1'])].type == particle.type and grid[str(neighbours['side1'])].fill < particle.fill: # and not moved:
            diff = Clamp(particle.fill - grid[str(neighbours['side1'])].fill,0,0.5) / constants.FLUID_STICKINESS
            grid[str(neighbours['side1'])].fill += diff
            particle.fill -= diff
            moved=True
            particle.state = "filling"

        # same function as above but behind
        elif not str(neighbours['side2']) in grid.keys():
            # SetCell(particle,neighbours['side2'])
            CreateParticle(Particle(neighbours['side2'],particle.type))
            grid[str(neighbours['side2'])].age = particle.age
            # grid[str(neighbours['side2'])].fill = particle.fill / 2
            # particle.fill = particle.fill / 2

            diff = Clamp(particle.fill,0,0.5) / constants.FLUID_STICKINESS
            grid[str(neighbours['side2'])].fill = diff
            particle.fill -= diff
            moved=True
            particle.state = "filling"
         
        # same function as above but behind
        elif grid[str(neighbours['side2'])].type == particle.type and grid[str(neighbours['side1'])].fill < particle.fill: # and not moved:
            diff = Clamp(particle.fill - grid[str(neighbours['side2'])].fill,0,0.5) / constants.FLUID_STICKINESS
            grid[str(neighbours['side2'])].fill += diff
            particle.fill -= diff
            moved=True
            particle.state = "filling"
            
        if particle.fill > 1:
            if not str(neighbours['up']) in grid.keys():
                CreateParticle(Particle(neighbours['side1'],particle.type))
                grid[str(neighbours['up'])].fill = particle.fill-1
                particle.fill = 1
                moved=True
                particle.state = "filling"
            elif grid[str(neighbours['up'])].type == particle.type:
                diff = Clamp(particle.fill - grid[str(neighbours['side2'])].fill,0,0.5) / constants.FLUID_STICKINESS
                grid[str(neighbours['up'])].fill += diff
                particle.fill -= diff
                moved = True
                particle.state = "filling"
            
        particle.shownFill = particle.fill
        
        #if not str(neighbours['down']) in grid.keys():
        #    particle.shownFill = 1
        #if str(neighbours['up']) in grid.keys() and grid[str(neighbours['up'])].type == particle.type:
        #    particle.shownFill = 1
        if particle.fill <= 0.02:
            ClearCell(particle, particle.pos)
        elif particle.fill < 1:
            particle.active = True
        #elif particle.fill >= 1:
        #    particle.active = False
            
    elif particleTypes[particle.type]['density'] < 0:
        if not str(neighbours['side1']) in grid.keys():
            ClearCell(particle,particle.pos)
            SetCell(particle,neighbours['side1'],particle.age)
            moved=True
            
        if not str(neighbours['side2']) in grid.keys():
            ClearCell(particle,particle.pos)
            SetCell(particle,neighbours['side2'],particle.age)
            moved=True

    if not moved:
        particle.active = False
        particle.state = "idle"
        

    if not particle.state == particle.prevState and not particle.state == 'filling':
        if random.randint(0,constants.SOUND_PLAY_CHANCE) == 0 and not particleTypes[particle.type]['sound'] == None:
            particleTypes[particle.type]['sound'].play()
        particle.prevState = particle.state
    return neighbours

# <summary>
# looks a lot more complicated than it is, ill try my best to explain 
# manages the reactions of particles based on their neighbours & the set rules within project_settings.py
# REACTANT - particle type used to start a reaction, PRODUCT - particle created after a reaction, REACTION - the reaction itself, involving 2 reactants to create a product
# </summary>
def ReactionCheck(p:Particle,neighbours:dict,_objectiveManager=None):
    if len(particleTypes[p.type]['reactions']) > 0: # if particle is capable of reacting
        for r in particleTypes[p.type]['reactions']: # for all existing reactions this particle is a part of
            for i in reactions[r]['reactants']: # for all of the required elements to create this reaction
                if p.type in i: # if current particle is a reactant in this reaction
                    for n in neighbours.values(): # for each adjacent (including diagonals) cell
                        if str(n) in grid.keys() and p.type == grid[str(n)].type: # if this neighbour is occupied by a particle & is the same particle type as current particle (helps with optimisation)
                            continue # next iteration through neighbours
                        elif str(n) in grid.keys() and grid[str(n)].type in i: # if neighbour is occupied by a particle and is a reactant (BRAIN REFRESHER: r - current iteration of reactions, i - current iteration of reactants, n - current iteration of neighbours)
                            if randint(0,int(round(reactions[r]['reactionDifficulty']/Clamp(p.fill,0.01,1)))) == 0: # if a random chance of reaction (determined in project_settings.py) is fulfilled
                                reactants = [p,grid[str(n)]] # store the particle class of both current particle & the successfully reacting neighbour
                                _checkParticles = []
                                for x in reactants: # for both the current particle & the reacting neighbour
                                    if reactions[r]['products'][i.index(x.type)] == -1: # if set in project_settings.py to delete itself
                                        ClearCell(x,x.pos) # delete particle
                                        continue # next reactant
                                    elif reactions[r]['products'][i.index(x.type)] == -2: # if set to do nothing
                                        continue # next reactant
                                    else:
                                        try: # using a try method here as sometimes particles react while moving, and the movement in a grid space is effectively deleting a particle & creating a new one with the same properties
                                            del grid[str(x.pos)]
                                        except:
                                            pass
                                        
                                        if particleTypes[p.type]['moveType'] == 'fluid':
                                            if randint(0,int(100 - (p.fill * 100))) == 0: # multiply current particle fill & reacting neighbour fill to see if a reactant should be formed
                                                pos = x.pos # position of the new particle
                                                old_type = x.type # store current reactant type
                                                del x # delete reactant
                                                CreateParticle(Particle(pos,reactions[r]['products'][i.index(old_type)])) # create the product of the reaction in the reactant's position, with the type determined by the reactant's properties
                                                try: # try to play sound instead of actually calling it, as particles dont always have sound & its too unoptimised to call for the particle type below twice
                                                    particleTypes[reactions[r]['products'][i.index(old_type)]]['sound'].play() # play sound associated with product of reaction
                                                except:
                                                    pass
                                                if _objectiveManager:
                                                    #_objectiveManager.CheckReaction(reactions[r]['products'][i.index(old_type)]) # if reaction particle was the current objective, it would freeze rendering the rest of the particles. instead added to a temporary array which is then checked for each particle as objective
                                                    if not reactions[r]['products'][i.index(old_type)] in _checkParticles:
                                                        _checkParticles.append(reactions[r]['products'][i.index(old_type)])
                                        else:
                                            pos = x.pos # position of the new particle
                                            old_type = x.type # store current reactant type
                                            del x # delete reactant
                                            CreateParticle(Particle(pos,reactions[r]['products'][i.index(old_type)]))
                                            if _objectiveManager:
                                                #_objectiveManager.CheckReaction(reactions[r]['products'][i.index(old_type)])
                                                if not reactions[r]['products'][i.index(old_type)] in _checkParticles:
                                                        _checkParticles.append(reactions[r]['products'][i.index(old_type)])
                                #for k in _checkParticles:
                                #    _objectiveManager.CheckReaction(reactions[r]['products'][i.index(k)])
                                return _checkParticles                        
                            
                else: # if not a particle within the reaction type, not only skip reactant iteration but also skip reaction iteration
                    continue

# <summary>
# brings all of these functions together. the only function in this script that manages more than one particle. called by main.py
# </summary>                
def UpdateWorld(_objectiveManager=None):
    particles = list(grid.values())
    neighbours = {}
    objectiveCheck = []
    for p in particles:
        if p.active:
            neighbours = MoveParticle(p)
            reactionResult = ReactionCheck(p,neighbours,_objectiveManager)
            if not reactionResult == None:
                for k in reactionResult:
                    if not k in objectiveCheck:
                        objectiveCheck.append(k)
            if p.pos[1] < -1:
                try:
                    del grid[str(p.pos)]
                except:
                    pass
                del p
            #pygame.draw.rect(constants.DISPLAY,tuple(p.colour),(p.pos[0]*constants.CELLSIZE,p.pos[1]*constants.CELLSIZE,constants.CELLSIZE,constants.CELLSIZE)) # used to draw particles BEFORE adding fluids, but deprecated as it does not Render fill levels
        if p != None and particleTypes[p.type]['decay'] != None:
            if p.age > particleTypes[p.type]['decay'][1] and randint(0,4) == 0: # if small random chance is true and particle is older than decay age
                try:
                    del grid[str(p.pos)]
                except:
                    pass
                if particleTypes[p.type]['decay'][0] != -1:
                    pos = p.pos
                    oldType = p.type
                    oldFill = p.fill
                    del p
                    if particleTypes[oldType]['moveType'] == 'fluid':
                        if randint(0,int(100 - (oldFill * 100))) and oldFill > 0.1: # reduce odds of creating a decay particle depending on fill level
                            CreateParticle(Particle(pos,particleTypes[oldType]['decay'][0]), oldFill)
                    else:
                        CreateParticle(Particle(pos,particleTypes[oldType]['decay'][0]), oldFill)
                    _objectiveManager.CheckReaction(particleTypes[oldType]['decay'][0])
                    continue
                else:
                    del p
                    continue
        p.age += 1
        if particleTypes[p.type]['density'] < 0 or particleTypes[p.type]['moveType'] == 'fluid': # vary colour of gases & water each frame but not solid particles
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
        _fill = Clamp(ceil(p.fill*constants.CELLSIZE)/constants.CELLSIZE,0,1)
        
        if particleTypes[p.type]['moveType'] == 'fluid' and particleTypes[p.type]['density'] > 0:
            pygame.draw.rect(constants.DISPLAY,tuple(p.colour),(p.pos[0]*constants.CELLSIZE+ScreenShake.screenShake[0],(p.pos[1]+(1-_fill))*(constants.CELLSIZE)+ScreenShake.screenShake[1],constants.CELLSIZE,constants.CELLSIZE * _fill))
        else:
            pygame.draw.rect(constants.DISPLAY,tuple(p.colour),(p.pos[0]*constants.CELLSIZE+ScreenShake.screenShake[0],(p.pos[1])*(constants.CELLSIZE)+ScreenShake.screenShake[1],constants.CELLSIZE,constants.CELLSIZE))
    for k in objectiveCheck:
        _objectiveManager.CheckReaction(k) # check for objective complete only after all particles have been rendered

# basic Clamp function which I use surprisingly a lot, Clamps x to between y (the low) & z (the high)
def Clamp(x,y,z) -> float:
    i = max(y, min(x, z))
    return i