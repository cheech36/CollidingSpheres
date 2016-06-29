from __future__ import print_function
from __future__ import division
from visual import *
import wx
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
import GUI as UI


### Matplotlib
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import Toolbar, FigureCanvasWxAgg
from matplotlib.figure import Figure


class gui_manager:
    def __init__(self, log=None, graph=None, plot=None):
        self.log = log
        self.graph = graph
        self.plot  = plot
        self.update_plot = False

class enviornment:

    def __init__(self):
        self.rate       = 200
        self.globalTime = 0
        self.globalDt   = 10/self.rate
        self.notPaused = True
        self.pauseCount = 0
        self.activeForcesDict    = dict()
        self.activeForcesList    = list()
        self.arena_boundary      = list()  #Walls, floor and ceiling
        self.forceFuncDict       = {'friction':self.friction}
        self.uFric = .05
        self.centerOfMass        = vector()
        self.playerMgr           = playerManager()
        self.playerMgr.envObj    = self
        self.init_gui()
        self.playerMgr.scene( self.scene1 )
        self.init_players()
        self.init_arena()
        print('Num of players',self.playerMgr.playerCount)


## Other Player Attributes


        self.randomWalk = randomWalk(1,self, self.playerMgr,.5)

    def run(self):
        #self.randomWalk.start()
        while True:
            rate(self.rate)
            while self.notPaused:
                rate(self.rate)
                self.playerMgr.updatePlayers(self.globalTime)
                self.playerMgr.applyForces(self)
                self.collisionTest1.check_player_player_collision(self.PLAYERS_COLLISION_KEY)
                self.collisionTest1.check_obstacle_player_collision(self.ARENA_BOUNDARY_KEY, self.PLAYERS_COLLISION_KEY)
                self.globalTime += 1
                #self.playerMgr.update_ui()
            if self.pauseCount == 0:
                print('Paused')
                print('Active Forces List: ', self.activeForcesList)
                print('Active Forces Dict: ', self.activeForcesDict)
                self.pauseCount = 1
                self.playerMgr.playerSelect()

    def friction(self, player):
        if player.position.y == 0:            ## Only frictino on floor
            player.velocity.x -=  (self.globalDt * self.uFric * player.velocity.norm().x)
            if mag(vector(player.velocity.x, 0, 0)) < player.restThreshold:
                player.velocity.x = 0
            player.velocity.z -=  (self.globalDt * self.uFric * player.velocity.norm().z)
            if mag(vector(player.velocity.z, 0, 0)) < player.restThreshold:
                player.velocity.z = 0

    def addForce(self, newForce , newPlayerID ):
        self.activeForcesList.append(newForce)
        self.activeForcesDict.update({newForce: newPlayerID})


    def init_players(self):
        self.SmartyPants = self.playerMgr.createSmartPlayer(vector(20, 0, 0))
        self.playerMgr.set_as_trainee(self.SmartyPants)
        print('Active player is: ', self.SmartyPants.getID())
        self.Walker0 = self.playerMgr.createPlayer(vector(-10, 0, 0))
        # self.Walker1 = self.playerMgr.createPlayer(vector(5, 0,  0))
        # self.Walker2 = self.playerMgr.createPlayer(vector(5, 0,  5))

        self.playerMgr.setPlayerBottom(-8)
        #        self.playerMgr.setAsWalker(self.SmartyPants)
        self.playerMgr.setAsWalker(self.Walker0)
        # self.playerMgr.setAsWalker(self.Walker1)
        # self.playerMgr.setAsWalker(self.Walker2)clear

        ## Other Player Attributes
        self.playerMgr.buildPlayers(sphere(radius=2, color=color.red, opacity=1), vector(0, -6, 0), materials.wood, 0)
        self.playerMgr.buildPlayers(sphere(radius=2, color=color.green, opacity=1), vector(0, -6, 0), materials.wood, 1)
        # self.playerMgr.buildPlayers(sphere(radius = 2, color = color.green, opacity = 1 ), vector(0,-6,0), materials.wood, 2)
        # self.playerMgr.buildPlayers(sphere(radius = 2, color = (.996,.616,.016), opacity = 1), vector(0,-6, 0), materials.wood, 3)

        self.SmartyPants.mass = 800
        self.Walker0.mass = 2

    def init_arena(self):
        self.floor1    = flr(self.playerMgr.getPlayerBottom(0))
        self.ceiling   = bp('y', .05, 'pos')
        self.frontWall = obstacle((0,     -6.75, -23)  ,(110, 0,  0),2.5, 3, bp('z', -20,'neg'))
        self.backWall = obstacle ((0,     -6.75,  23)  ,(110, 0,  0),2.5, 3, bp('z',  20,'pos'))
        self.leftWall = obstacle ((-53.5, -6.75,   0)  ,(0,   0, 44),2.5, 3, bp('x', -50,'neg'))
        self.rightWall = obstacle((53.5,  -6.75,   0)  ,(0,   0, 44),2.5, 3, bp('x',  50,'pos'))
        self.arena_boundary.append(self.floor1)
        self.arena_boundary.append(self.ceiling)
        self.arena_boundary.append(self.frontWall)
        self.arena_boundary.append(self.backWall)
        self.arena_boundary.append(self.leftWall)
        self.arena_boundary.append(self.rightWall)
        self.collisionTest1 = CollisionMonitor()
        self.PLAYERS_COLLISION_KEY = self.collisionTest1.addSet(self.playerMgr.activePlayers)
        self.ARENA_BOUNDARY_KEY    = self.collisionTest1.addSet(self.arena_boundary)


    def init_gui(self):
        L = 320
        Hgraph = 450

        self.controll_Window = UI.DisplayPanel('Display Panel',self.playerMgr)
        self.controll_Window.playerManager = self.playerMgr
        # For Dual Monitor x = 1300 is perfect
        # For Monitor Information use xrandr
        self.scene1 = display(x=800, y=0, width=600, height=800)
        self.scene1.autoscale = False
        self.scene1.title = 'SphereLand Lab Frame'
        self.scene1.range = (30, 10, 5)

        self.graph_display = UI.GraphPanel('Training Efficiency')
        self.ui = gui_manager(self.controll_Window.msg,self.graph_display,self.controll_Window.axes)
        self.ui.canvas = self.controll_Window.canvas
        self.ui.controll_window = self.controll_Window
        self.playerMgr.set_ui(self.ui)



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
                    self.manager.jump_on_random(self.envObj, walker)
            time.sleep(self.SLEEP)



############################### Main Program #############################################
env1 = enviornment()
env1.handler = eventHandler(env1)
env1.run()
############################### Main program #############################################


