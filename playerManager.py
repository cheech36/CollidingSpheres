from __future__ import print_function
from __future__ import division
from visual import *
from particle import *
from player import *
from smartPlayer import *


class playerManager:
    envObj = None
    def __init__(self):
        self.activePlayers = list()
        self.playerCount = 0
        self.activePlayerID = 0
        self.nonZero_FNet_ID = list()
        self.listOfWalkers = list()
        aabb.playerManager = self ## Register with aabb collision class
        brainEngine.playerManager = self # Register with Brain Engine Class

    def createPlayer(self, position = vector):
        newPlayer = player(position, self.playerCount)
        self.activePlayers.append(newPlayer)
        self.playerCount += 1
        if len(self.activePlayers) == 1:
            self.active = self.activePlayers[0]
        return newPlayer

    def createSmartPlayer(self, position = vector):
        newPlayer = smartPlayer(position, self.playerCount)
        self.activePlayers.append(newPlayer)
        self.playerCount += 1
        if len(self.activePlayers) == 1:
            self.active = self.activePlayers[0]
        return newPlayer

    def setPlayerMass(self, mass, id = 'none'):
        ##If no id is given set all player to this mass
        if id == 'none':
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

    def updatePlayers(self):
        for player in self.activePlayers:
            player.fullRender()
            player.updateVelocity()
            player.roll()                   ## Assumes player is a sphere, need to add player flag 'rollEnabled'

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
            newPlayerPosition.x = -50
        if newPlayerPosition.x > 50:
            newPlayerPosition.x = 50

        if newPlayerPosition.z < -19:
            newPlayerPosition.z = -19
        if newPlayerPosition.z > 19:
            newPlayerPosition.z = 19

        newPlayer = self.createPlayer( newPlayerPosition )
        self.buildPlayers(sphere(radius = 2, color = color.red ), vector(0,-6,0), materials.wood, newPlayer.getID() )
        newPlayer.updatePosition()
        newPlayer.setAcceleration(vector(0,-9.81,0))
        envObj.addForce('floor', newPlayer.getID())

        id = newPlayer.getID()      ## Use PlayerID to generate a new color
        colorID = id  - 3              ## StartGenerating colors from ID 1

        newColor   =  [int(x) for x in bin(colorID)[2:]]

        if( len(newColor) <= 3):
            while len(newColor) < 3:
                newColor.append(0)

        print(newColor)
        newPlayer.mass = 80
        envObj.activeForcesList.append('floor')
        envObj.activeForcesDict.update({'floor':newPlayer.getID()})
        self.setForce(newPlayer.getID(),'floor')

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
            active.setAcceleration(vector(0,-9.81,0))
            envObj.activeForcesList.append('floor')
            envObj.activeForcesDict.update({'floor':id})
            self.setForce(id,'floor')

    def jump_on_random(self, envObj, walker ):
        active = walker
        if active.position.y == 0:
            id = walker.getID()
            active.changeVelocity(active.jumpCharge)
            active.setAcceleration(vector(0,-9.81,0))
            envObj.activeForcesList.append('floor')
            envObj.activeForcesDict.update({'floor':id})
            self.setForce(id,'floor')

    def jump(self, player):
        if player.position.y == 0:
            id = player.getID()
            player.changeVelocity(player.jumpCharge)
            player.setAcceleration(vector(0,-9.81,0))
            self.envObj.activeForcesList.append('floor')
            self.envObj.activeForcesDict.update({'floor':id})
            self.setForce(id,'floor')

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

