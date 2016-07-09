from __future__ import print_function
from __future__ import division
from visual import *
from particle import *
from player import *
from smartPlayer2 import *
from brainEngine import *
#from smartPlayer import *


class playerManager:
    envObj = None

    def __init__(self):
        self.activePlayers = list()
        self.playerCount = 0
        self.activePlayerID = 0
        self.nonZero_FNet_ID = list()
        self.listOfWalkers = list()
        aabb.playerManager = self ## Register with aabb collision class
        bs.playerManager   = self
        brainEngine.playerManager = self # Register with Brain Engine Class



    def createPlayer(self, position = vector):
        newPlayer = player(position, self.playerCount)
        self.activePlayers.append(newPlayer)
        self.playerCount += 1
        if len(self.activePlayers) == 1:
            self.active = self.activePlayers[0]
        return newPlayer

    def createSmartPlayer(self, position = vector):
#        newPlayer = smartPlayer(position, self.playerCount)
        newPlayer = smartPlayer2(position, self.playerCount)
        self.activePlayers.append(newPlayer)
        self.playerCount += 1
        if len(self.activePlayers) == 1:
            self.active = self.activePlayers[0]
        return newPlayer



    def setPlayerMass(self, mass, id = 0):
        ##If no id is given set all player to this mass
        if id == 0:
            for p in self.activePlayers:
                p.mass = mass
        else:
            self.activePlayers[id].mass = mass

    def buildPlayers(self, shape, relativePosition = 0, material='none', id  ='none'):
        ##If no id is given add for all players
        if id == 'none':
            for p in self.activePlayers:
                p.addComponent(shape, relativePosition + vector(6,0,0) * p.getID())
                p.body.material = material
                p.body.radius = shape.radius
                p.rollEnable = True
                # Need to check that it is a sphere first
                # If not disable Rolling
        else:
            self.activePlayers[id].addComponent(shape, relativePosition)
            self.activePlayers[id].body.material = material
            self.activePlayers[id].body.radius = shape.radius     ## Need to check that it is a sphere first
            self.activePlayers[id].rollEnable = True              ## If not disable rolling

    def addToPlayer(self, id, shape, relativePosition = 0, material='none' ):
            self.activePlayers[id].addComponent(self, shape, relativePosition, color, material)
            self.activePlayers[id].body.material = material

    def updatePlayers(self, time = 0):
        for player in self.activePlayers:
            player.fullRender()
            player.updateVelocity()
            player.roll()
            player.age()                   ## Assumes player is a sphere, need to add player flag 'rollEnabled'
            if (player.getType() == 'smartPlayer'):
                player.look(time)


    def setPlayerBottom(self, yValue):
        for player in self.activePlayers:
            player.bottom = yValue

    def getPlayerBottom(self, id):
        return self.activePlayers[id].bottom

    def getActivePlayer(self):
        return self.activePlayers[self.activePlayerID]

    def playerSelect(self):
            active = self.activePlayers[self.activePlayerID]
            self.psBox = box(pos = active.getPosition(),length = 6, height = 6, width = 6)
            self.psBox.pos.y = -6
            self.psBox.opacity = .1
            self.psBox.color = color.blue
            self.scene.center = self.psBox.pos

    def changePlayer(self, IncVal):
        if (self.activePlayerID + IncVal) < 0 or (self.activePlayerID + IncVal + 1) > self.playerCount:
            return self.activePlayers[self.activePlayerID]
        else:
            active  = self.activePlayers[self.activePlayerID + IncVal]
            self.psBox.pos = active.getPosition() - vector(0,6,0)
            self.activePlayerID = active.getID()
            self.scene.center = self.psBox.pos
            return active

    def silent_Change(self, id):

        if id  < 0:
            return self.activePlayers[id]
        else:
            print('Player manager Changing to player: ', id)
            active = self.activePlayers[id]
            self.activePlayerID = active.getID()



    def scene(self, scene):
        self.scene = scene

    def unpause(self):
        self.psBox.length  = 0
        self.psBox.width   = 0
        self.psBox.height  = 0
        self.psBox.visble = False
        del self.psBox

    def createPlayer_Click(self, position, envObj):
        newPlayerPosition   = vector()
        newPlayerPosition   = position
        if newPlayerPosition.x < -50:
            newPlayerPosition.x = -45
        if newPlayerPosition.x > 50:
            newPlayerPosition.x = 45
        if newPlayerPosition.z < -19:
            newPlayerPosition.z = -15
        if newPlayerPosition.z > 19:
            newPlayerPosition.z = 15
        newPlayer = self.createPlayer( newPlayerPosition )
        self.buildPlayers(sphere(radius = 1, color = color.red ), vector(0,-6,0), materials.wood, newPlayer.getID() )
        newPlayer.updatePosition()
        newPlayer.setAcceleration(vector(0,-9.81,0))
        id = newPlayer.getID()      ## Use PlayerID to generate a new color
        #colorID = id  - 3              ## StartGenerating colors from ID 1
        #newColor   =  [int(x) for x in bin(colorID)[2:]]
        #if( len(newColor) <= 3):
        #    while len(newColor) < 3:
        #        newColor.append(0)
        #print(newColor)
        newPlayer.mass = 2

    def applyForces(self,env):
        if len(self.nonZero_FNet_ID) != 0:    ##Call all active Forces
            for index in self.nonZero_FNet_ID:
                playerForceList = self.activePlayers[index].getForcesList()
                for force in playerForceList:
                    env.forceFuncDict[force](self.activePlayers[index])

    def setForce(self, playerID, forceName):
        if playerID == -1:
            for p in self.activePlayers:
                p.addForce(forceName)
                self.nonZero_FNet_ID.append( p.getID() )
        else:
            p = self.activePlayers[playerID]
            p.addForce(forceName)
            self.nonZero_FNet_ID.append(p.getID())

    def unsetForce(self, playerID, forceName):
        if playerID == -1:
            for p in self.activePlayers:
                p.removeForce(forceName)
                self.nonZero_FNet_ID.remove( p.getID() )
        else:
            p = self.activePlayers[playerID]
            p.removeForce(forceName)
            self.nonZero_FNet_ID.remove(p.getID())

    def jump_on_keyup(self, envObj, active):
        if active.position.y == 0:
            id = active.getID()
            active.changeVelocity(active.jumpCharge)



    def jump_on_random(self, envObj, walker ):
        active = walker
        if active.position.y == 0:
            id = walker.getID()
            active.changeVelocity(active.jumpCharge)

    def jump(self, player):
        if player.position.y == 0:
            id = player.getID()
            player.changeVelocity(player.jumpCharge)

    def setAsWalker(self, player):
        self.listOfWalkers.append(player)

    def setTarget( self, targetPosition ):
        targetPosition.y = 0                ## Project onto XZ plane
        for player in self.activePlayers:
            if player.getType() == 'smartPlayer':
                player.setTarget(targetPosition)
                player.chase()

    def look(self, smart_player):
        if smart_player.getType() == 'smartPlayer':
            smart_player.look()
        else:
            print('Not Smart')
            return -1

    def train(self, label):
        self.trainee.train(label)

    def set_as_trainee(self, trainee):
        self.trainee = trainee

    def set_ui(self, ui):
        #print(image_plot)
        self.ui = ui
        brainEngine.ui = ui

    def update_ui(self):
        if(self.ui.update_plot):
            print('Udated UI')
            A = self.ui.plot_data
            p1 = self.ui.plot.add_subplot(111)
            p1.imshow(A, interpolation='nearest')
            self.ui.update_plot = False

    def toggle_friction(self, mode = False):
        if 'friction' in self.envObj.activeForcesList:
            self.envObj.activeForcesList.remove('friction')
            del self.envObj.activeForcesDict['friction']
            self.unsetForce(-1,'friction')
            print('turning Friction off')
        else:
            self.envObj.activeForcesList.append('friction')
            self.envObj.activeForcesDict.update({'friction':self.getActivePlayer().id})
            self.setForce(-1,'friction')
            print('turning Friction On')
        print(self.envObj.activeForcesDict)
        if(not(mode)):
            self.ui.controll_window.ToggleFriction('manager')

    def save(self):
        for player in self.activePlayers:
            if player.getType() == 'smartPlayer':
                player.save()
