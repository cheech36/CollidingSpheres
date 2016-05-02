from __future__ import print_function
from __future__ import division
from visual import *
import time

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
        self.height = 2*scope[1]
        self.width  = 2*scope[2]

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
        if (Lower_x <= x and  x < Upper_x and
            #Lower_y <= y and  y < Upper_y and
            Lower_z <= z and  z < Upper_z    ):
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

# Bounding Plane
class bp:
    #Incoming direction positive, negative, or both
    direction = {'pos':1, 'neg':-1 , 'bi':0}
    axis      = {'x':0, 'y':1, 'z':2}
    COLLISION_THRESHOLD = .01

    def __init__(self,axis_name , axis_value,  mode = 'bi'):
        self.axis_name = axis_name
        self.norm_axis = self.axis[axis_name]
        self.axis_mode = self.direction[mode]
        self.axis_value = axis_value
        self.player_pos = 0
        self.collsion_data = [0,0,0,0,0]
        self.type = 0

    def check(self, player):

        # Check either the x, y, or z component of the players position
        pos = player.getPosition()[self.norm_axis]
        if self.axis_mode == 0 and False:
            # Handle this later
            pass

        elif self.axis_mode == -1 and pos < self.axis_value:
            self.collsion_data[0] = self.norm_axis
            return 1

        elif self.axis_mode == 1  and pos > self.axis_value:
            self.collsion_data[0] = self.norm_axis
            return 1

        else:
            self.collsion_data[0] = self.norm_axis
            return 0

    def getdata(self):
        return self.collsion_data

    def gettype(self):
        return self.type


class CollisionMonitor:

    interactingSets = dict()
    def __init__ (self):
        self.time = 0
        self.start_time = time.time()

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

    def check_obstacle_player_collision(self, obstacle_key, player_key):
        self.OBS_KEY = obstacle_key
        if len(self.interactingSets) == 0:
            print("Add interacting Set with 'addSet'")
            return
        obstacles = self.interactingSets[obstacle_key]
        players   = self.interactingSets[player_key]
        for obs in obstacles:
            for plr in players:
               if(obs.check(plr)):
                   type = obs.gettype()
                   if type == 0:
                       pass
                       self.on_crossing_ceiling(obs, plr)
                   else:
                       self.on_obstacle_player_collision(obs, plr)


    def on_obstacle_player_collision(self,obs, plr):
       vel_norm = obs.getdata()[0]
       if(vel_norm == 1):
           #Bouncing vertically of a plane
           plr.getVelocity()[vel_norm] = 0
           plr.getPosition()[1] = 0

       else:
            #Reflect off horizontal planes
            plr.getVelocity()[vel_norm] *= -1


    def on_crossing_ceiling(self, obs, plr):
        plr.setAcceleration(vector(0,-9.81,0))

#                   if(plr.getVelocity()[1] > 0):
#                        if(plr.getPosition()[1] > .5 ):
#                            plr.setAcceleration(vector(0,-9.81,0))
#                        else:
#                            plr.setAcceleration(vector(0,0,0))
#                            plr.getPosition()[1] = 0

    def on_player_player_collision(self,objX, objY):


        m1               = objX.mass
        m2               = objY.mass
        r1Norm           = objX.position
        r2Norm           = objY.position
        u1_vec           = objX.velocity
        u2_vec           = objY.velocity
        u                = m1*m2/(m1+m2)
        rNorselfvec      = r1Norm - r2Norm
        vRel_vec         = u1_vec - u2_vec
        dv1 = 2*(u/m1)*vRel_vec.proj(rNorselfvec)
        dv2 = 2*(u/m2)*vRel_vec.proj(rNorselfvec)
        v1_vec           = u1_vec - dv1
        v2_vec           = u2_vec + dv2
        elapsed_time = time.time() - self.start_time

        #This should be true for a valid collision
#        if(u1_vec.dot(rNorselfvec) <= 0 and u2_vec.dot(rNorselfvec) >= 0):

        #print('collision')
        #This should be true only for an invalid collision
        if(u1_vec.dot(rNorselfvec) >= 0 and u2_vec.dot(rNorselfvec) <= 0):
            print('Entangled')
            tol  = .05
            rpen = mag(r1Norm - r2Norm)
            dr1  = (rpen + tol)*rNorselfvec.norm()
            dr2  = (rpen + tol)*-rNorselfvec.norm()
            #Now check to make sure the 2 balls are not moving through another object
            hold_X = 0
            hold_Y = 0
            obstacles = self.interactingSets[self.OBS_KEY]
            for obs in obstacles:
                   hold_X += obs.check(objX)
                   hold_Y += obs.check(objY)
            #Now displace each player to disentangle them
            print('Disentangling')
            if not(hold_X):
                objX.changePosition(dr1)
            else:
                print('Cant move X')
            if not(hold_Y):
                objY.changePosition(dr2)
            else:
                print('Cant move Y')

        objX.on_collision(elapsed_time, objY.getID())
        objY.on_collision(elapsed_time, objX.getID())
        objX.setVelocity(v1_vec)
        objY.setVelocity(v2_vec)



    def addSet(self, newSet):
        newKey = len(self.interactingSets) + 1
        self.interactingSets.update({newKey: newSet})
        return newKey
