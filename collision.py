from __future__ import print_function
from __future__ import division
from visual import *
import math

class aabb:

    playerManager = None
    def __init__(self, id, scope, pos_Rel_Center = vector(0,0,0) ):

        self.player_id = 0
        self.type = 'aabb'
        if id >= 0:
            self.id = id
        else:
            return
        self.length = 2*scope[0]
        self.height  = 2*scope[1]
        self.width = 2*scope[2]

        ## This part gets updated each call to look()
        self.location = vector(pos_Rel_Center)
        self.Upper = self.location + .5*vector(self.length, self.height, self.width)
        self.Lower = self.location - .5*vector(self.length, self.height, self.width)

    def contains_players(self, position):
        #print('Checking to see if: ', position, ' is between ', self.Upper, ' and ', self.Lower)
        Upper_x = self.Upper.x
        Upper_y = self.Upper.y
        Upper_z = self.Upper.z

        Lower_x = self.Lower.x
        Lower_y = self.Lower.y
        Lower_z = self.Lower.z

        x = position.x
        y = position.y
        z = position.z


        #ommit checking y coordinates for now
        # Note: Exclusive inequality means if x and z are exactly equal to bounds, incoming will not be detected
        # to fix this make upper or lower bound inclusive
        if Lower_x <= x and  x < Upper_x and  Lower_z <= z and  z < Upper_z:
            return 1
        else:
            return 0

# Move the scope boundary to the players location
    def update_scope_boundary(self,  new_position):

        self.Upper = new_position + .5*vector(self.length, self.width, self.height)
        self.Lower = new_position - .5*vector(self.length, self.width, self.height)

    def check_for_players_in_scope(self, new_position):

        self.update_scope_boundary(new_position)
        # Do a preliminary check with a scope sized bounding box to avoid unnecessary computation
        incoming = 0
        threatCount = 0
        for incomingPlayer in self.playerManager.activePlayers:
            id = incomingPlayer.getID()
            if id != self.player_id:
                incoming = self.contains_players(incomingPlayer.getPosition())
                if incoming:
                    # print('Incoming Player: ', incomingPlayer.getID())
                    threatCount += 1
                    incoming = 0
        return threatCount

    def check_for_players_in_cell(self):

        incoming = 0
        threatCount = 0
        for incomingPlayer in self.playerManager.activePlayers:
            id = incomingPlayer.getID()
            if id != self.player_id:
                incoming = self.contains_players(incomingPlayer.getPosition())
                if incoming:
                    #print('Incoming Player: ', incomingPlayer.getID())
                    threatCount += 1
                    incoming = 0
        return threatCount


    def move(self, displacement):
        self.Upper += displacement
        self.Lower += displacement



# Bounding Sphere Class
class bs:
    def __init__(self, interactingSets):
        pass

class CollisionMonitor:

    interactingSets = dict()


    def __init__ (self):
        self.time = 0

        # should sort through objectList, caclute, then assign bounding sphere, bound box etc
        # or a superpostion of bounding structures

    def check_player_player_collision(self, setID):
        if len(self.interactingSets) == 0:
            print("Add interacting Set with 'addSet'")
            return

        test_set = self.interactingSets[setID]
        length = len(test_set)
        for j in range(0, length):
            objX = test_set[j]
            for i in range(j+1, length):
                objY = test_set[i]
                distance = objX.getPosition() - objY.getPosition()
                min_distance = objX.body.radius + objY.body.radius
                if distance.mag <= min_distance:
                    self.on_player_player_collision(objX, objY)

    def on_player_player_collision(self,objX, objY):
        m1               = objX.mass
        m2               = objY.mass
        r1Norm           = objX.position
        r2Norm           = objY.position
        u1_vec           = objX.velocity
        u2_vec           = objY.velocity
        u                = m1*m2/(m1+m2)
        rNorselfvec        = r1Norm - r2Norm
        vRel_vec         = u1_vec - u2_vec
        v1_vec           = u1_vec - 2*(u/m1)*vRel_vec.proj(rNorselfvec)
        v2_vec           = u2_vec + 2*(u/m2)*vRel_vec.proj(rNorselfvec)

        objX.setVelocity(v1_vec)
        objY.setVelocity(v2_vec)


    def addSet(self, newSet):
        newKey = len(self.interactingSets) + 1
        self.interactingSets.update({newKey: newSet})
        return newKey
