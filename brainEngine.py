import threading
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
        self.position = self.player.position
        self.playerID = self.player.getID()

    def run(self):
        while True:

            self.image1 = self.sense.look(self.position)

            #brain.feedforward(self.image1)
            # A simple way of analyzing the image to decide if a player is incoming
            incoming = array(self.image1).any()
            #If so, tell the player to jump
            if incoming:
                self.player.chargeJump()
                self.playerManager.jump(self.player)

            if len(self.player.collision_history) > 0:
                collision_data = self.player.collision_history.pop()
                collision_time = collision_data[0]
                other_player   = collision_data[1]
                print(' collision at: ', collision_time, 'between',
                      self.playerID, ' and ', other_player)

            #reinforcement code here
            #brain.train() ?
            time.sleep(self.SLEEP)