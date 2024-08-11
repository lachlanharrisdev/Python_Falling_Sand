# hello sir
# i've used a lot of c# coding conventions (unity) so sorry if it's confusing
# also i have used more modules than just pygame/sys but I believe they come installed with python
# i've copied & pasted this to the top of every script just so you see this
# pls give me bonus marks for not using AI :)

# this script manages the actual progression system for the player, including dialogue boxes, checking if certain elements are crafted, and providing an array of unlocked placable particles

import pygame
import time
from project_settings import *

def display_dialogue(text, isObjective=False, char_delay=0.035, font=None, text_color=(255, 255, 255), box_color=(15, 15, 15), sound_effect=constants.DIALOGUE_SOUND, sound_interval=2):
    if font is None:
        font = pygame.font.Font(None, 36)  # Default font and size
    

    screen_width = constants.WIDTH
    screen_height = constants.HEIGHT

    # Calculate the size of the dialogue box based on the text
    lines = []
    words = text.split(' ')
    max_width = screen_width - 100  # Leave some padding
    line = ""
    
    _letter = 0
    
    for word in words:
        test_line = f"{line} {word}".strip()
        if font.size(test_line)[0] <= max_width:
            line = test_line
        else:
            lines.append(line)
            line = word
    lines.append(line)

    # Calculate box dimensions
    box_padding = 10
    max_line_width = max([font.size(line)[0] for line in lines])
    box_width = max_line_width + 2 * box_padding
    box_height = len(lines) * font.get_height() + 2 * box_padding
    
    # Position the box in the center-bottom of the screen
    box_x = (screen_width - box_width) // 2
    box_y = screen_height - box_height - 50

    # Create a surface for the dialogue box
    box_surface = pygame.Surface((box_width, box_height))
    box_surface.fill(box_color)

    if isObjective:
        constants.OBJECTIVE_SOUND.play()

    # Main loop to display each character one at a time
    for i, line in enumerate(lines):
        for j, char in enumerate(line):
            char_surface = font.render(char, True, text_color)
            box_surface.blit(char_surface, (box_padding + font.size(line[:j])[0], box_padding + i * font.get_height()))

            # Play the sound effect for each character
            _letter += 1
            if not isObjective and sound_effect and _letter >= sound_interval and not (char == " " or char == "." or char == ","):
                sound_effect.play()
                _letter = 0
            # Update the display
            pygame.display.get_surface().blit(box_surface, (box_x, box_y))
            pygame.display.update()
            if not (char == "." or char == "," or char == ";" or char == "!"):
                time.sleep(char_delay)
            else:
                time.sleep(char_delay*2)
    
    # Keep the full dialogue box on the screen for a short time after displaying all text
    pygame.display.update()
    time.sleep(1.5)  # Adjust this duration as needed
    




# ---------------------------------------------------------------
# objectives

import asyncio

class ObjectivesManager:
    def __init__(self, screen, font, sound_effect):
        self.screen = screen
        self.font = font
        self.sound_effect = sound_effect
        self.objectives = []
        self.current_objective = None

    def add_objective(self, objective):
        self.objectives.append(objective)

    def get_next_objective(self):
        if self.objectives:
            self.current_objective = self.objectives.pop(0)
            # Display the new objective to the user
            self.display_objective_dialogue(self.current_objective.description)

    def display_objective_dialogue(self, text, _objective=False, _charDelay=0.035):
        display_dialogue(text, _objective, _charDelay)

    def check_place_particle(self, particle_index):
        if self.current_objective and self.current_objective.objective_type == ObjectiveType.PLACE_PARTICLE:
            if particle_index == self.current_objective.target_index:
                self.complete_objective()
                
    def check_cursor_size(self, particle_index=0):
        if self.current_objective and self.current_objective.objective_type == ObjectiveType.CURSOR_SIZE:
            self.complete_objective()

    def check_reaction(self, reactant_index):
        if self.current_objective and self.current_objective.objective_type == ObjectiveType.REACTION:
            if reactant_index == self.current_objective.target_index:
                self.complete_objective()

    def complete_objective(self):
        # Objective completed, display a dialogue and get the next objective
        self.display_objective_dialogue("Objective completed!", True, 0.015)
        self.get_next_objective()

# Example of adding objectives
def setup_objectives(manager):
    manager.add_objective(Objective(ObjectiveType.PLACE_PARTICLE, 0, "So... the new cosmic chef is here. Time for basic training. First, place a sand particle")) # spawn sand
    manager.add_objective(Objective(ObjectiveType.CURSOR_SIZE, 0, "Cool... you made a single particle. That's nothing though. Press - or = to change your cursor size, we'll start making BIG things")) # change cursor size
    manager.add_objective(Objective(ObjectiveType.PLACE_PARTICLE, 2, "There we go, bulk creating particles. Now press C to change particle types & place a water particle")) # place water
    manager.add_objective(Objective(ObjectiveType.REACTION, 12, "The holy god spent a lot of time making those fluid physics. Thank him for that. Now, try making placing some wood & watch what happens when you water it")) # leaf reaction
    manager.add_objective(Objective(ObjectiveType.REACTION, 5, "We have life! Now see if you can set that tree on fire (I love arson :D)")) # smoke reaction / decay
    manager.add_objective(Objective(ObjectiveType.REACTION, 10, "Yayyy! Time to let you get thinking... Let's see if you can figure out how to make glass.")) # glass reaction
    manager.add_objective(Objective(ObjectiveType.REACTION, 10, "Good, you're actually competent. Now make... a star!")) # glass reaction


