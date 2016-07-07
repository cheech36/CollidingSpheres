from __future__ import division
import threading
import numpy as np
import wx
from array import array
from Sense import *
from NeuralBrain import *
from visual.graph import *
import matplotlib.pyplot as plt

# Valid status keys
NULL    = np.array([False, False, False, False], dtype=bool)
STREAM  = np.array([True, False, False, False], dtype=bool)
FEED    = np.array([False, True, False, False], dtype=bool)
TRIGGER = np.array([False, False, True, False], dtype=bool)
LOCKOUT = np.array([False, False, False, True], dtype=bool)

class Gate:
    def __init__(self, capacity = 5):
        self.status = np.array([False, False, False, False], dtype=bool)
        self.stream_capacity = capacity
        self.stream_size = 0
        self.test_boundary = False
        self.display_graph = False
        self.display_plot  = False
        self.train_lock    = False
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


class brainEngine:
    message_log = None
    ui          = None

    def __init__(self, player1, sleep):
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
        self.stream_train_bffr = 0
        self.train_count = 0
        self.train_label = None
        self.correct_response = 0
        self.trainset = list()

        self.nojump_count = 0
        self.jump_count = 0
        self.correct_count = 0
        self.jump_skewness = 5
        self.disparity_old = 0
        self.disparity_new = 0



        # Status Flags stream,feed,trig,collision,lockout
        # Set Max stream size to 6 images
        self.gate = Gate(12)

        self.gate.display_graph = True
        self.gate.display_plot  = False
        #if(self.gate.display_graph):
        #    self.train_graph = self.ui.graph

        # Make the bain
        self.myBrain = NeuralBrain("NeuralModel_Logit_1Hl-n50_2Outputs", self.scope_x*self.scope_z, 1, 50);
        self.myBrain.loadPersistentModel();



    def run(self, time):
        listqueue = [];
        if( not ( time % 10)):
            buffer = self.sense.look(self.position)
            if (len(self.player.collision_history) > 0):
                collision_data = self.player.collision_history.pop()
                collision_time = collision_data[0]
                other_player = collision_data[1]
                print(' collision at: ', collision_time, 'between', self.playerID, ' and ', other_player)
                self.train_label = 'jump'


                if (self.gate.open()):
                    followinstinct = self.feed()
                    self.react(followinstinct)
                    self.stream_train_bffr += 1


                self.gate.add(LOCKOUT)

            if( self.gate.open() ):
                image_new = buffer
                if (self.image_old.any() != image_new.any()):
                # Detect End of stream
                    if( self.image_old.any() ):
                        self.gate.remove(STREAM)
                        self.gate.add(FEED)   ## ====> Skip to feed


                    elif( image_new.any() ):
                # Detect the Beginning of a stream
                        self.gate.add(STREAM)
                        if(self.gate.test_boundary):
                            #print('Did Not Need to jump 1')
                            self.gate.test_boundary = False
                        #self.print_to_log('Starting Stream: ' + str( self.stream_count) + ':   ')

                if(self.gate.stream() and not(self.gate.stream_full()) ):
                    self.image_sum += image_new
                    self.gate.increment()

                self.image_old = image_new
                if( self.gate.feed() or self.gate.stream_full()):
                    self.gate.add(LOCKOUT)
                    followinstinct = self.feed()
                    self.react(followinstinct)
                    self.gate.reset_stream()
                    self.stream_train_bffr += 1


            if(self.gate.test_boundary):
                self.should_have_jumped = self.check_test_boundary()
                # Where the ball would be if it had not jumped
                if(self.should_have_jumped):
                    print('Should have jumped')
                    self.gate.test_boundary = False



        if( self.train_label == 'jump' and not( self.check_scope())) :
            self.print_to_log('\nTraining: ')
            self.print_to_log( 'jump')
            self.train_count = int(self.stream_train_bffr)
	    self.jump_count += 1
            self.train(self.train_label)
            self.train_label = 'none'
            self.stream_train_bffr = int(self.stream_count)
        elif(not( self.check_scope()) and self.stream_train_bffr != self.stream_count):
            self.print_to_log('\nTraining: ')
            self.print_to_log( 'nojump')
            self.train_label = 'nojump'
	    self.nojump_count += 1
            self.train(self.train_label)
            self.train_label = 'none'
            self.stream_train_bffr = int(self.stream_count)



    def train(self, label):
        #The stream should always be locked out after termination
        #Termination can occur for 3 reasons
        # a) Stream is full
        # b) A collision has occured
        # c) The other player has exited the scope boundary
        if( self.gate.lock()):
            if( label == 'jump'):
                print('jump')
                label_hot = [1,0]
            elif( label == 'nojump'):
                print('nojump')
                label_hot = [0,1]
            else:
                print('Training Error')
                return


            np_label = np.array(label_hot)
            train_label = np_label.reshape((1,2))
            self.myBrain.trainAndSaveModel(self.train_data,train_label)
            #print(self.image_sum)
            self.image_sum = self.sense.blank()
            self.image_old = self.sense.blank()
            self.stream_size = 0
            self.gate.remove(LOCKOUT)
            self.gate.remove(FEED)
            self.gate.remove(STREAM)

            self.disparity_new = abs(self.jump_count - self.nojump_count)

            if  self.disparity_new < self.jump_skewness or abs(self.disparity_new) < abs(self.disparity_old):

                self.trainset.append([self.stream_count, label == self.followinstinct[0]])
                self.correct_response += self.trainset[self.stream_count][1]
                self.stream_count += 1
                self.accuaracy = self.correct_response / self.stream_count
                self.ui.graph.plot((self.stream_count,self.accuaracy))

                print('Training Efficiency: ', self.accuaracy)
                self.print_to_log('\nDisparity: ' + str(self.jump_count - self.nojump_count))

            else:
                self.print_to_log('\nData to Skewed, ommit from training\n')
            self.disparity_old = int(self.disparity_new)


    def feed(self):
            self.gate.remove(FEED)
            if(self.gate.display_plot):
                plt.imshow(self.image_sum, interpolation='nearest')
            N = self.image_sum.sum()
            if(N != 0):
                inputneurons = self.image_sum.reshape((1, self.scope_x * self.scope_z)) / N
            self.train_data = np.array(inputneurons)
            self.followinstinct = self.myBrain.feedForwardOnly(inputneurons);
            #msg = 'Response: ' + str(self.followinstinct[0]) + 'Confidence: ' + str(self.followinstinct[1]) + '\n'
            msg = '\n\nTraining Stream: ' + str(self.stream_count)
            self.print_to_log(msg)
            msg = '\nResponse: ' + str(self.followinstinct[0])
            self.print_to_log(msg)
            self.ui.plot.imshow(self.image_sum, interpolation='nearest')
            self.ui.canvas._onSize(1)
            self.gate.train_lock = True
            return self.followinstinct



    def react(self, instinct):
        if (instinct[0] == 'jump'):
            self.player.chargeJump()
            self.playerManager.jump(self.player)
            self.drop_test_boundary(self.position)

    def drop_test_boundary(self, position):
        # Must create a test sphere where the ball would be if it had not jumped.
        # To do this must project the current position of  ball on to floor, however a copy will not work for this,
        # must use a reference to current position
        # Revisit this

        self.test_sphere = bs(self.playerID,vector(self.position),2)
        self.gate.test_boundary = True


    def check_test_boundary(self):
        #Need to pass the projected position of the ball on each call, add a parameter for this
        hit =  self.test_sphere.check_for_players()

    def check_scope(self):
        return self.sense.scope_boundary.check_for_players_in_scope(self.position)


    def print_to_log(self,msg):
        self.ui.log.AppendText(msg)
        #A = np.random.randint(25, size=(5, 5) )
        #p1 = self.ui.plot.add_subplot(111)
        #p1.imshow(A, interpolation='nearest')


    def save(self):
        self.myBrain.trainAndSaveModel(None, None, True)


