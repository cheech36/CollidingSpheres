from __future__ import print_function
from __future__ import division
from visual import *
from eventHandler import *
from player import *
from eventHandler import *
from collision import *
from math import *
from CourseObjects import *
from fancyBalls import *
from playerManager import*
from smartPlayer import *
import threading
import time

class enviornment:

    def __init__(self):
        pass

        self.rate       = 200
        self.globalTime = 0
        self.globalDt   = 10/self.rate

        self.notPaused = True
        self.pauseCount = 0
        self.activeForcesDict    = dict()
        self.activeForcesList    = list()
        self.arena_boundary      = list()    # includes the walls and the floor at this point

        self.forceFuncDict       = {'floor':self.floor, 'friction':self.friction}
        self.uFric = .10

        self.centerOfMass        = vector()
        self.playerMgr           = playerManager()
        self.playerMgr.envObj    = self

        self.scene1 = display(x=0, y=0, width=1200, height = 600)
        self.scene1.autoscale = False
        self.scene1.title = 'SphereLand Lab Frame'
        self.scene1.range = (30,10,5)
        self.playerMgr.scene( self.scene1)



        self.SmartyPants = self.playerMgr.createSmartPlayer(vector(20, 0,0))
        print('Active player is: ', self.SmartyPants.getID())
        self.Walker0 = self.playerMgr.createPlayer(vector(-10, 0,  0))
        self.Walker1 = self.playerMgr.createPlayer(vector(5, 0,  0))
        self.Walker2 = self.playerMgr.createPlayer(vector(5, 0,  5))


        self.playerMgr.setPlayerBottom(-8)

        self.playerMgr.setAsWalker(self.SmartyPants)
        self.playerMgr.setAsWalker(self.Walker0)
        self.playerMgr.setAsWalker(self.Walker1)
        self.playerMgr.setAsWalker(self.Walker2)

## Other Player Attributes
        self.playerMgr.buildPlayers(sphere(radius = 2, color = color.cyan, opacity = 1  ), vector(0,-6,0), materials.wood, 0)
        self.playerMgr.buildPlayers(sphere(radius = 2, color = color.blue, opacity = 1 ), vector(0,-6,0), materials.wood, 1)
        self.playerMgr.buildPlayers(sphere(radius = 2, color = color.green, opacity = 1 ), vector(0,-6,0), materials.wood, 2)
        self.playerMgr.buildPlayers(sphere(radius = 2, color = (.996,.616,.016), opacity = 1), vector(0,-6, 0), materials.wood, 3)
        self.playerMgr.setPlayerMass(20)



## Other Player Attributes

        self.floor1    = flr(self.playerMgr.getPlayerBottom(0))
        self.ceiling   = bp('y', .05, 'pos')
        self.frontWall = obstacle((0,     -6.75, -23)  ,(110, 0,  0),2.5, 3, bp('z', -20,'neg'))
        self.backWall = obstacle ((0,     -6.75,  23)  ,(110, 0,  0),2.5, 3, bp('z',  20,'pos'))
        self.leftWall = obstacle ((-53.5, -6.75,    0) ,(0,   0, 44),2.5, 3, bp('x', -50,'neg'))
        self.rightWall = obstacle((53.5,  -6.75,     0),(0,   0, 44),2.5, 3, bp('x',  50,'pos'))

        self.arena_boundary.append(self.floor1)
        self.arena_boundary.append(self.ceiling)
        self.arena_boundary.append(self.frontWall)
        self.arena_boundary.append(self.backWall)
        self.arena_boundary.append(self.leftWall)
        self.arena_boundary.append(self.rightWall)

        self.collisionTest1 = CollisionMonitor()
        self.PLAYERS_COLLISION_KEY = self.collisionTest1.addSet(self.playerMgr.activePlayers)
        self.ARENA_BOUNDARY_KEY    = self.collisionTest1.addSet(self.arena_boundary)

        self.randomWalk = randomWalk(1,self, self.playerMgr,.5)

    def run(self):

        self.randomWalk.start()
        while True:
            rate(self.rate)
            while self.notPaused:
                rate(self.rate)
                self.playerMgr.updatePlayers()
                self.playerMgr.applyForces(self)
                self.collisionTest1.check_player_player_collision(self.PLAYERS_COLLISION_KEY)
                self.collisionTest1.check_obstacle_player_collision(self.ARENA_BOUNDARY_KEY,
                                                                    self.PLAYERS_COLLISION_KEY)
                #self.walls()

            if self.pauseCount == 0:
                print('Paused')
                print('Active Forces List: ', self.activeForcesList)
                print('Active Forces Dict: ', self.activeForcesDict)
                self.pauseCount = 1
                self.playerMgr.playerSelect()

    def floor(self, player):

                if 'floor' in self.activeForcesList:
                    if player.getPosition().y < .05:
                        player.velocity.y = 0
                        player.setAcceleration( vector(0,0,0) )
                        player.position.y = 0
                        player.jumpCharge = vector(0,1,0)
                        self.activeForcesList.remove('floor')

#                        del self.activeForcesDict['floor']
                        self.playerMgr.unsetForce(player.getID(),'floor')
                        return

    def friction(self, player):
        if player.position.y == 0:            ## Only frictino on floor
            player.velocity.x -=  (self.globalDt * self.uFric * player.velocity.norm().x)
            if mag(vector(player.velocity.x, 0, 0)) < player.restThreshold:
                player.velocity.x = 0
            player.velocity.z -=  (self.globalDt * self.uFric * player.velocity.norm().z)
            if mag(vector(player.velocity.z, 0, 0)) < player.restThreshold:
                player.velocity.z = 0

    def walls(self):
        for player in self.playerMgr.activePlayers:
            if player.getPosition().x <= -50 or player.getPosition().x >= 50:
                vx = player.getVelocity().x
                player.changeVelocity(vector(-2*vx,0,0 ))

            if player.getPosition().z <= -20 or player.getPosition().z >= 20:
                vz = player.getVelocity().z
                player.changeVelocity(vector(0,0,-2*vz))

    def addForce(self, newForce , newPlayerID ):
        self.activeForcesList.append(newForce)
        self.activeForcesDict.update({newForce: newPlayerID})

class randomWalk (threading.Thread):
    def __init__(self, threadID, envObj, manager, sleep):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.SLEEP = sleep
        self.manager = manager
        self.envObj = envObj

    def run(self):
        while true:
            for walker in self.manager.listOfWalkers:
                walker.walk()
                y = walker.jump_on_random()
                if y != 0:
                    #print(walker.getID(), ' is jumping :', y)
                    self.manager.jump_on_random(self.envObj, walker)
            time.sleep(self.SLEEP)




############################### Main Program #############################################
env1 = enviornment()
env1.handler = eventHandler(env1)
env1.run()
############################### Main program #############################################
## test add


