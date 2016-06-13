from __future__ import division
import threading
import numpy as np
from array import array
from Sense import *
from NeuralBrain import *

# Valid status keys
NULL    = np.array([False, False, False, False], dtype=bool)
STREAM  = np.array([True, False, False, False], dtype=bool)
FEED    = np.array([False, True, False, False], dtype=bool)
TRIGGER = np.array([False, False, True, False], dtype=bool)
LOCKOUT = np.array([False, False, False, True], dtype=bool)

class Gate:
    def __init__(self, capacity = 5):
        self.status = np.array([False, False, False, False], dtype=bool)
        self.stream_capacity = 5
        self.stream_size = 0
    def __check__(self, key):
        index = np.where(key == True)[0][0]
        return self.status[index]
    def stream_full(self):
        return (self.stream_size >= self.stream_capacity)
    def add(self, key):
        self.status +=  key
    def remove(self, key):
        index_to_subtract = np.where(key == True)[0][0]
        self.status[index_to_subtract] = False
    def stream(self):
        return self.__check__(STREAM)
    def reset_stream(self):
        self.stream_size = 0
    def feed(self):
        return self.__check__(FEED)
    def trigger(self):
        return self.__check__(TRIGGER)
    def lock(self):
        return self.__check__(LOCKOUT)
    def open(self):
        return not(self.__check__(LOCKOUT))
    def increment(self):
        self.stream_size += 1
        return self.stream_size


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
        self.image_old = self.sense.blank()
        self.image_sum = self.sense.blank()
        self.stream_count = 0
        self.correct_response = 0
        self.trainset = list()

        # Status Flags stream,feed,trig,collision,lockout
        # Set Max stream size to 6 images
        self.gate = Gate(6)
        # Make the bain
        self.myBrain = NeuralBrain("NeuralModel_Logit_1Hl-n50_2Outputs", self.scope_x*self.scope_z, 1, 50);
        self.myBrain.loadPersistentModel();


    def run(self):
        listqueue = [];
        while True:
            buffer = self.sense.look(self.position)
            if (len(self.player.collision_history) > 0):
                collision_data = self.player.collision_history.pop()
                collision_time = collision_data[0]
                other_player = collision_data[1]
                print(' collision at: ', collision_time, 'between', self.playerID, ' and ', other_player)

                if (self.gate.open()):
                    followinstinct = self.feed()
                self.gate.add(LOCKOUT)

            if( self.gate.open() ):
                image_new = buffer
                if (self.image_old.any() != image_new.any()):
                # Detect Beginning or end of stream
                    if( self.image_old.any() ):
                        self.gate.remove(STREAM)
                        self.gate.add(FEED)

                    elif( image_new.any() ):
                        self.gate.add(STREAM)
                        print('Starting Stream: ', self.stream_count)

                if(self.gate.stream() and not(self.gate.stream_full()) ):
                    self.image_sum += image_new
                    self.gate.increment()

                self.image_old = image_new
                if( self.gate.feed() or self.gate.stream_full()):
                    self.gate.add(LOCKOUT)

                    followinstinct = self.feed()
                    if (followinstinct[0] == 'jump'):
                        self.player.chargeJump()
                        self.playerManager.jump(self.player)

                    self.gate.reset_stream()
            time.sleep(self.SLEEP)


    def train(self, label):
        #The stream should always be locked out after termination
        #Termination can occur for 3 reasons
        # a) Stream is full
        # b) A collision has occured
        # c) The other player has exited the scope boundary
        if( self.gate.lock()):
            if( label == 'jump'):
                label_hot = [1,0]
            elif( label == 'nojump'):
                label_hot = [0,1]

            np_label = np.array(label_hot)
            train_label = np_label.reshape((1,2))
            self.myBrain.trainAndSaveModel(self.train_data,train_label)
            self.image_sum = self.sense.blank()
            self.image_old = self.sense.blank()
            self.stream_size = 0
            self.gate.remove(LOCKOUT)
            self.gate.remove(FEED)
            self.gate.remove(STREAM)
            self.trainset.append([self.stream_count, label == self.followinstinct[0]])
            self.correct_response += self.trainset[self.stream_count][1]
            self.stream_count += 1
            print('Train Label', label, 'Training Efficiency: ', self.correct_response / self.stream_count)
            print("\n")

        else:
            print('No Stream Data')



    def feed(self):
            self.gate.remove(FEED)
            inputneurons = self.image_sum.reshape((1, self.scope_x * self.scope_z)) / self.gate.stream_size;
            self.train_data = np.array(inputneurons)
            self.followinstinct = self.myBrain.feedForwardOnly(inputneurons);
            print('Response: ', self.followinstinct[0], 'Confidence: ', self.followinstinct[1])
            return self.followinstinct