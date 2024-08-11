# hello sir
# i've used a lot of c# coding conventions (unity) so sorry if it's confusing
# also i have used more modules than just pygame/sys but I believe they come installed with python
# i've copied & pasted this to the top of every script just so you see this
# pls give me bonus marks for not using AI :)

# this script manages the actual progression system for the player, including dialogue boxes, checking if certain elements are crafted, and providing an array of unlocked placable particles

import pygame
import time
from project_settings import *

def DisplayDialogue(text, isObjective=False, char_delay=0.035, text_color=(255, 255, 255), font=None, box_color=(15, 15, 15), sound_effect=constants.DIALOGUE_SOUND, sound_interval=2):
    if font is None:
        font = constants.DIALOGUE_FONT
    

    screenWidth = constants.WIDTH
    screenHeight = constants.HEIGHT

    lines = []
    words = text.split(' ')
    max_width = screenWidth - 100  # leave 50px of padding either side of screen
    line = ""
    
    _letter = 0
    
    # automatically create new lines of text depending on width of words
    for word in words:
        test_line = f"{line} {word}".strip()
        if font.size(test_line)[0] <= max_width:
            line = test_line
        else:
            lines.append(line)
            line = word
    lines.append(line)

    # calculating box dimensions, accounting for padding & font height
    box_padding = 10
    max_line_width = max([font.size(line)[0] for line in lines])
    box_width = max_line_width + 2 * box_padding
    box_height = len(lines) * font.get_height() + 2 * box_padding
    
    # put in center bottom of screen
    box_x = (screenWidth - box_width) // 2
    box_y = screenHeight - box_height - 50

    # creating the surface to display text on
    box_surface = pygame.Surface((box_width, box_height))
    box_surface.fill(box_color)

    if isObjective:
        constants.OBJECTIVE_SOUND.play() # play objective sound only if the dialogue is meant for the "objective complete!" text

    # Main loop to display each character one at a time
    for i, line in enumerate(lines): # for each line determined by the previous algojrithm
        for j, char in enumerate(line): # for each character within the line
            char_surface = font.render(char, True, text_color)
            box_surface.blit(char_surface, (box_padding + font.size(line[:j])[0], box_padding + i * font.get_height())) # map letters onto a surface for the box, treating it like a single image that can be moved around

            # play sound ever sound_interval letters, and if they are not a silent letter
            _letter += 1
            if not isObjective and sound_effect and _letter >= sound_interval and not (char == " " or char == "." or char == ","):
                sound_effect.play()
                _letter = 0
            pygame.display.get_surface().blit(box_surface, (box_x, box_y))
            pygame.display.update()
            if not (char == "." or char == "," or char == ";" or char == "!"):
                time.sleep(char_delay)
            else:
                time.sleep(char_delay*2) # sleep longer if the char is something that would be paused on IRL (full stops, commas, etc.)
    
    pygame.display.update()
    time.sleep(1.5) # "linger" time after dialogue done generating
    




# ---------------------------------------------------------------
# objectives

unlockedParticles = [0] # array of the indexes of unlocked particles (is capable of going [0,3,2], meaning it would display sand, then hydrogen, then water in that order)    
# screenShake = [0,0] # offset for particle rendering in x, y pixels

from random import randint

# <summary>
# a class that manages the entire objectives system, uses heavy OOP
# </summary>
class ObjectivesManager:
    def __init__(self, screen, font, sound_effect):
        self.screen = screen
        self.font = font
        self.sound_effect = sound_effect
        self.objectives = []
        self.current_objective = None

    # add a new objective to the list (just used to keep code clean)
    def AddObjective(self, objective):
        self.objectives.append(objective)

    # retrieves the next objective in the list of objectives
    def RetrieveObjective(self):
        if self.objectives:
            self.current_objective = self.objectives.pop(0)
            # Display the new objective to the user
            self.DisplayObjectiveDialogue(self.current_objective.description)
            for i in self.current_objective.unlocks:
                unlockedParticles.append(i)
    
    # used to have bonus functionality, but kept here in case change need to be made between objective dialogue & other dialogue
    def DisplayObjectiveDialogue(self, text, _objective=False, _charDelay=0.035):
        DisplayDialogue(text, _objective, _charDelay)

    # called whenever user manually places particles, if its current objective and particletype matches objective then CompleteObjective() is called
    def CheckPlaceParticle(self, particle_index):
        if self.current_objective and self.current_objective.objective_type == ObjectiveType.PLACE_PARTICLE:
            if particle_index == self.current_objective.target_index:
                self.CompleteObjective()
                
    # called whenever user changes cursor size, if its current objective then CompleteObjective() is called
    def CheckCursorSize(self, particle_index=0):
        if self.current_objective and self.current_objective.objective_type == ObjectiveType.CURSOR_SIZE:
            self.CompleteObjective()

    # called whenever a reaction occurs with a product, if product matches objective then CompleteObjective() is called
    def CheckReaction(self, reactant_index):
        if self.current_objective and self.current_objective.objective_type == ObjectiveType.REACTION:
            if reactant_index == self.current_objective.target_index:
                if not reactant_index == 13:
                    self.CompleteObjective()
                elif not ScreenShake.doScreenShake:
                    self.EndGame()
                    
    # called when the star element is crafted
    def EndGame(self):
        constants.RUMBLE_SOUND.play()
        DisplayDialogue("Wait... I should NOT have told you to do that... RUN!!!", False, 0.035, (200,20,20))
        ScreenShake.doScreenShake = True
        
    # called when the criteria of the objective is successfully met
    def CompleteObjective(self):
        self.DisplayObjectiveDialogue("Objective completed!", True, 0.015)
        self.RetrieveObjective()

# Example of adding objectives
def SetupObjectives(manager):
    # create all of the games objectives (chonky but simple)
    if GameParams.sandbox:
        manager.AddObjective(Objective(ObjectiveType.REACTION, 999, "This is the freeplay mode! Do whatever you want, no restrictions!", [1,2,4,5,6,7,8,9,10,11,12])) # unachievable reaction, unlocks everything from the beginning
    else:
        manager.AddObjective(Objective(ObjectiveType.REACTION, 13, "DEBUG:REACT_STAR", [3])) # star reaction, causes endgame
        manager.AddObjective(Objective(ObjectiveType.PLACE_PARTICLE, 0, "So... the new cosmic chef is here. Here we go again. First mission: click to place a sand particle", [])) # spawn sand, unlocks nothing
        manager.AddObjective(Objective(ObjectiveType.CURSOR_SIZE, 0, "Cool... you made a single particle. That's nothing though. Press = to increase your cursor size (and - to decrease it)", [])) # change cursor size, unlocks water
        manager.AddObjective(Objective(ObjectiveType.PLACE_PARTICLE, 2, "There we go, look at your big cursor. Now press C to change particle types, & place some water.", [2])) # place water, unlocks wood
        manager.AddObjective(Objective(ObjectiveType.REACTION, 12, "The holy god spent a lot of time making those fluid physics. Thank him for that. Now, try placing some wood & watch what happens when you water it.", [6])) # leaf reaction, unlocks fire liquid
        manager.AddObjective(Objective(ObjectiveType.REACTION, 5, "We have life! Now I wanna see it die. Set it on fire!!!", [9])) # smoke reaction / decay, unlocks nothing
        manager.AddObjective(Objective(ObjectiveType.REACTION, 10, "Yayyy! Time for you get thinking... Let's see if you can figure out how to make glass.", [])) # glass reaction, unlocks hydrogen
        manager.AddObjective(Objective(ObjectiveType.REACTION, 13, "Good, you're actually competent. Now make... a star!", [3])) # star reaction, causes endgame
    
def Clamp(x,y,z) -> float:
    i = max(y, min(x, z))
    return i

