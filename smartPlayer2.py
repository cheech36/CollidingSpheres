from player import *
from NeuralBrain import *
from brainEngine import *
from Sense import *
import threading
import time


class smartPlayer2 (player):
    def __init__(self, position, id):
        player.__init__(self, position, id)
        self.type = 'smartPlayer'
        self.target = vector(0,0)
        self.scope = (10,10,10)
        self.sense = sense(id, position, self.scope)
        self.image1 = self.sense.blank_image
        
        self.myBrain = NeuralBrain("NeuralModel_Logit_1Hl-n50_2Outputs", 1, 50); # minibatch size=1, with 50 hidden neurons (hard-coded 1-layer only so far)
        self.myBrain.loadPersistentModel ();
        
        self.brainEngine = brainEngine(self, .25)
        self.brainEngine.start()
        
    def getType(self):
        return self.type

    def look(self):
        self.image1 = self.sense.look(self.position) 
