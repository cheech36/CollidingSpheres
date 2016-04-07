from visual import*
from player import*
class eventHandler:

    def __init__(self , envObj):
        self.env          =  envObj
        self.playerManager = envObj.playerMgr
        self.activePlayer = self.playerManager.getActivePlayer()
        self.mode         = 0


        self.env.scene1.bind('keydown', self.handleKeyDown )
        self.env.scene1.bind('keyup'  , self.handleKeyUp   )
        self.env.scene1.bind('click'  , self.handleClick   )

    def handleKeyDown(self, evt ):
        if evt.key == 'left':
            self.leftKeyDown()

        if evt.key == 'right':
            self.rightKeyDown()

        if evt.key == 'up':
            self.upKeyDown()

        if evt.key == 'down':
            self.downKeyDown()

        if evt.key == " ":
            self.spaceKeyDown()

        if evt.key == 's':
            self.sKeyDown()

        if evt.key == 'f':
            self.fKeyDown()

        if evt.key == 'r':
            self.rKeyDown()

        if evt.key == 'p':
            self.pKeyDown()

        if evt.key == '1':
            self.oneKeyDown()

        if evt.key == '2':
            self.twoKeyDown()

        if evt.key == '3':
            self.threeKeyDown()

        if evt.key == 'f1':
            self.f1KeyDown()

        if evt.key == 't':
            self.tKeyDown()

        if evt.key == 'l':
            print('Player is at: ', self.activePlayer.position)
            self.playerManager.look(self.activePlayer)

    def leftKeyDown(self):

        if self.mode == 1:
            self.activePlayer = self.playerManager.changePlayer(-1)
            return
        else:
            self.activePlayer.moveLeft()

    def rightKeyDown(self):

        if self.mode == 1:
            self.activePlayer = self.playerManager.changePlayer(1)
            return
        else:
            self.activePlayer.moveRight()

    def upKeyDown(self):

        if self.mode == 1:
            return
        else:
            self.activePlayer.moveUp()

    def downKeyDown(self):

        if self.mode == 1:
            return
        else:
            self.activePlayer.moveDown()

    def spaceKeyDown(self):


        if self.activePlayer.position.y == 0:
            self.activePlayer = self.playerManager.getActivePlayer()
            self.activePlayer.chargeJump()

    def fKeyDown(self):
        if 'friction' in self.env.activeForcesList:
            self.env.activeForcesList.remove('friction')
            del self.env.activeForcesDict['friction']
            self.playerManager.unsetForce(-1,'friction')
            print('turning Friction off')

        else:
            self.env.activeForcesList.append('friction')
            self.env.activeForcesDict.update({'friction':self.activePlayer.id})
            self.playerManager.setForce(-1,'friction')
            print('turning Friction On')

        print(self.env.activeForcesDict)

    def sKeyDown(self):
#        if self.activePlayer.position.y == 0:
            self.activePlayer.setVelocity(vector(0,0,0))

    def rKeyDown(self):
##       if self.activePlayer.position.y == 0:
            self.activePlayer.setPosition(vector(-5,0,0))

    def pKeyDown(self):
        self.activePlayer.printStats()

    def oneKeyDown(self):
        self.activePlayer = self.env.p1

    def twoKeyDown(self):
        self.activePlayer = self.env.p2
        print('Player 2 is active')

    def threeKeyDown(self):
        self.activePlayer = self.env.p3
        print('Player 3 is active')


    def f1KeyDown(self):

        if self.mode == 0 or self.mode == 1:
            self.env.notPaused = not(self.env.notPaused)
            self.mode = not(self.mode)
            self.env.pauseCount = 0
            if self.env.notPaused == True:
                self.playerManager.unpause()

    def leftKeyDown_Paused(self):
            id = self.activePlayer.getID()
            self.activePlayer = self.playerManager.activePlayers[ id - 2]
            print('new active player: ', self.activePlayer.getID())
            self.playerManager.playerSelect(self.activePlayer, self.psBox)

    def rightKeyDown_Paused(self):
            id = self.activePlayer.getID()
            self.activePlayer = self.playerManager.activePlayers[ id ]
            print('new active player: ', self.activePlayer.getID())
            self.playerManager.playerSelect(self.activePlayer, self.psBox)

    def tKeyDown(self):
            if self.mode == 2:
                self.mode = 0
                print('Target Mode Off')
            elif self.mode == 0:
                self.mode = 2
                print('Target Mode Set')

## Key Up Functions ##

    def handleKeyUp(self, evt ):

        if evt.key == " ":
            self.spaceKeyUp()

    def spaceKeyUp(self):
        self.playerManager.jump_on_keyup(self.env, self.activePlayer)


    def handleClick(self,evt):

        if self.mode == 0:
            print ('click @', evt.pos)
            self.playerManager.createPlayer_Click(evt.pos, self.env)
        if self.mode == 2:
            self.playerManager.setTarget(evt.pos)

