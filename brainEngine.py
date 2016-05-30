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
        self.image1 = self.sense.blank_image
        self.lastImage = False;
        self.position = self.player.position
        self.playerID = self.player.getID()
        
        self.myBrain = NeuralBrain("NeuralModel_Logit_1Hl-n50_2Outputs", 800, 1, 50); # minibatch size=1, with 50 hidden neurons (hard-coded 1-layer only so far)
        self.myBrain.loadPersistentModel ();
        
        
    def run(self):
        listqueue = [];
        while True:
            self.image1 = self.sense.look(self.position)
            listqueue.append(self.image1)
            
            if (len (listqueue) == 3):
                
                # do training pass using the previous 2 measurements + current collision history
                inputneurons = np.concatenate ((array (listqueue[0]), array (listqueue[1])));
                inputneurons.shape = (1,800);
                jumptrain = [[0, 1]]; # hot endcoded for should not have jumped

                if len(self.player.collision_history) > 0:
                    collision_data = self.player.collision_history.pop()
                    collision_time = collision_data[0]
                    other_player   = collision_data[1]
                    print(' collision at: ', collision_time, 'between',
                          self.playerID, ' and ', other_player)
                    jumptrain = [[1, 0]]; # hot encoded for should have jumped
                    
                self.myBrain.trainAndSaveModel (inputneurons, np.array (jumptrain));
                    
                    
                # now do forward pass using most recent 2 measurements
                inputneurons = np.concatenate ((array (listqueue[1]), array (listqueue[2])));
                inputneurons.shape = (1,800);
                followinstinct = self.myBrain.feedForwardOnly (inputneurons);
                if (followinstinct[0] == "jump"):
                    print ('Jumping, given probability %f of success') % (followinstinct[1]);
                    self.player.chargeJump();
                    self.playerManager.jump(self.player);
                elif (not (followinstinct[0] == "nojump" or followinstinct[0] == "notsure")):
                    printf ("Error, non expected instinct");

                listqueue = [listqueue[1],listqueue[2]];

            time.sleep(self.SLEEP)
            self.lastImage = self.image1