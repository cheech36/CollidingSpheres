from __future__ import division
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
        self.scope_x  = 2*self.player.scope[0]
        self.scope_z  = 2*self.player.scope[2]
        self.lastImage = False;
        self.position = self.player.position
        self.playerID = self.player.getID()


        self.image_old = np.zeros((self.scope_x,self.scope_z), dtype= int)
        self.image_sum = np.zeros((self.scope_x,self.scope_z), dtype= int)

        self.stream_size = 0
        self.image_stream = False
        self.image_feed = False
        self.image_trig = False
        self.collision  = False
        self.lockout_flag = False

        self.myBrain = NeuralBrain("NeuralModel_Logit_1Hl-n50_2Outputs", self.scope_x*self.scope_z, 1, 50);
        # minibatch size=1, with 50 hidden neurons (hard-coded 1-layer only so far)
        self.myBrain.loadPersistentModel();


    def run(self):
        listqueue = [];
        while True:
            buffer = np.array(self.sense.look(self.position), dtype=int)

            if (len(self.player.collision_history) > 0):
                collision_data = self.player.collision_history.pop()
                collision_time = collision_data[0]
                other_player = collision_data[1]
                print(' collision at: ', collision_time, 'between', self.playerID, ' and ', other_player)

                print('Feeding Forward, Stream Size= ', self.stream_size)
                self.image_feed = False
                # for row in self.image_sum.tolist():
                #print('Image Sum\n', self.image_sum)
                inputneurons = self.image_sum.reshape((1, self.scope_x * self.scope_z)) / self.stream_size;
                #print('Input Neurons\n', inputneurons)
                self.train_data = np.array(inputneurons)
                followinstinct = self.myBrain.feedForwardOnly(inputneurons);
                print('Instinct is: ', followinstinct)
                self.stream_size = 0
                self.lockout_flag = True
                self.image_stream = False
                self.image_feed = False




            if(not(self.lockout_flag)):
                image_new = buffer

                if (self.image_old.any() != image_new.any()):
                    ## Either begin or the end of a stream
                    if( self.image_old.any() ):
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
                    self.stream_size += 1
                    #print(image_new.any())

                self.image_old = image_new
                if( self.image_feed or self.stream_size > 5):

                    if(self.stream_size > 5):
                        self.image_stream = False
                        print('Stream is Full')
                        self.lockout_flag = True
                    else:
                        print('stream not full ', self.stream_size)

                    print('Feeding Forward')
                    self.image_feed = False
                    #for row in self.image_sum.tolist():
                    print(self.image_sum)
                    inputneurons = self.image_sum.reshape((1,self.scope_x*self.scope_z))/self.stream_size;
                    #print(inputneurons)
                    self.train_data = np.array(inputneurons)
                    followinstinct = self.myBrain.feedForwardOnly(inputneurons);
                    print('Instinct is: ', followinstinct)

                    if (followinstinct[0] == 'jump'):
                        self.player.chargeJump()
                        self.playerManager.jump(self.player)

            time.sleep(self.SLEEP)


    def train(self, label):
        print(label, ' Made it to brain engine')
        np_label = np.array(label)
        train_label = np_label.reshape((1,2))
        print(train_label)

        #print('Image Sum\n', self.image_sum)
        #print('Input Neurons\n', self.train_data)

        self.myBrain.trainAndSaveModel(self.train_data,train_label)

        self.image_sum = np.zeros((self.scope_x, self.scope_z), dtype=int)
        self.image_old = np.zeros((self.scope_x, self.scope_z), dtype=int)
        self.stream_size = 0
        self.lockout_flag = False
        self.image_feed = False
