import threading
import numpy as np
from array import array
from Sense import *

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

    def run(self):
        listqueue = [];
        while True:
            self.image1 = self.sense.look(self.position)
            listqueue.append(self.image1)
            if (len (listqueue) == 3):
                inputneurons = np.concatenate ((array (listqueue[0]), array (listqueue[1])));
                inputneurons.shape = (1,800);
                
                # now do forward pass using most recent 2 measurements
                
                # now do training pass using the previous 2 measurements + current collision history

                if len(self.player.collision_history) > 0:
                    collision_data = self.player.collision_history.pop()
                    collision_time = collision_data[0]
                    other_player   = collision_data[1]
                    print(' collision at: ', collision_time, 'between',
                          self.playerID, ' and ', other_player)

                listqueue = [listqueue[1],listqueue[2]];

            time.sleep(self.SLEEP)
            self.lastImage = self.image1