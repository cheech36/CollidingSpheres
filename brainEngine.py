import threading
import numpy as np
from array import array
from Sense import *
from NeuralBrain import *

class brainEngine (threading.Thread):
    playerManager = None
    def __init__(self, player1, sleep):
        threading.Thread.__init__(self)
        self.player = player1
        self.SLEEP = sleep
        self.sense = self.player.sense
        self.lastImage = False;
        self.position = self.player.position
        self.playerID = self.player.getID()


        self.image_old = np.zeros((20,20))
        self.image_sum = np.zeros((20,20))
        self.image_stream = False
        self.image_feed = False
        self.image_trig = False
        self.collision  = False

        self.myBrain = NeuralBrain("NeuralModel_Logit_1Hl-n50_2Outputs", 400, 1, 50);
        # minibatch size=1, with 50 hidden neurons (hard-coded 1-layer only so far)
        self.myBrain.loadPersistentModel();


    def run(self):
        listqueue = [];
        while True:
            image_new = np.array(self.sense.look(self.position), dtype=int)
            if (self.image_old.any() != image_new.any()):
                ## Either begin or the end of a stream
                if( self.image_old.any()):
                    ## Then the stream must be ending
                    self.image_stream = False
                    self.image_feed = True
                    print('Ending Stream')
                elif( image_new.any() ):
                    ## The stream must be beginning
                    self.image_stream = True
                    print('Starting Stream')
            if(self.image_stream):
                self.image_sum += image_new
                #print(image_new.any())

            self.image_old = image_new
            if( self.image_feed ):
                print('Feeding Forward')
                self.image_feed = False
                #for row in self.image_sum.tolist():
                print(self.image_sum)
                inputneurons = self.image_sum.reshape((1,400));
                followinstinct = self.myBrain.feedForwardOnly(inputneurons);
                self.image_sum = np.zeros((20,20), dtype=int)



                if (len(self.player.collision_history) > 0):
                    collision_data = self.player.collision_history.pop()
                    collision_time = collision_data[0]
                    other_player = collision_data[1]
                    print(' collision at: ', collision_time, 'between', self.playerID, ' and ', other_player)




            time.sleep(self.SLEEP)

