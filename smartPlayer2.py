from player import *
from brainEngine import *
from Sense import *
import threading
import time


class smartPlayer2 (player):
    def __init__(self, position, id):
        player.__init__(self, position, id)
        self.type = 'smartPlayer'
        self.target = vector(0,0)
        self.scope = (7, 7, 7)
        self.sense = sense(id, position, self.scope)
        self.image1 = self.sense.blank_image
        
        self.brain = brainEngine(self, .05)
        self.brain.start()
        
    def getType(self):
        return self.type

    def look(self):
        self.image1 = self.sense.look(self.position) 

    def train(self, label):
        self.brain.train(label)