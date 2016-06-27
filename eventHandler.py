from visual import*
from player import*
import numpy as np

class eventHandler:
    def __init__(self , envObj):
        self.env          =  envObj
        self.playerManager = envObj.playerMgr
        self.mode         = 0
        self.env.scene1.bind('keydown', self.handleKeyDown )
        self.env.scene1.bind('keyup'  , self.handleKeyUp   )
        self.env.scene1.bind('click'  , self.handleClick   )

        self.forward = self.env.scene1.forward
        print(self.forward)

    def handleKeyDown(self, evt ):
        if evt.key == 'left':
            self.leftKeyDown()

        if evt.key == 'right':
            self.rightKeyDown()

        if evt.key == 'up':
            self.upKeyDown()

        if evt.key == 'down':
            self.downKeyDown()

        if evt.key == " ":     # Jump
            self.spaceKeyDown()

        if evt.key == 's':     # Stop
            self.sKeyDown()

        if evt.key == 'f':     # Turn on friction
            self.fKeyDown()

        if evt.key == 'o':     # Return to position
            self.oKeyDown()

        if evt.key == 'p':     # Print stats
            self.pKeyDown()

        if evt.key == '1':      # Don't press
            self.oneKeyDown()

        if evt.key == '2':      # Don't press
            self.twoKeyDown()

        if evt.key == '3':      # Don't press
            self.threeKeyDown()

        if evt.key == 'f1':     # Pause
            self.f1KeyDown()

        if evt.key == 't':      # Train - Not working
            self.tKeyDown()

        if evt.key == 'l':      # Look  - Don't use
            print('Player is at: ', self.playerManager.getActivePlayer().position)
            self.playerManager.look(self.playerManager.getActivePlayer())

        if evt.key == 'j':     # Manual Indicate - Right Decision
            self.jKeyDown()

        if evt.key == 'n':    # Manual Indicate - Wrong Decisions
            self.nKeyDown()

    def leftKeyDown(self):
        if self.mode == 1:
            self.playerManager.changePlayer(-1)
            print('eventHandler change', self.playerManager.getActivePlayer().getID())
            return
        else:

            forward = self.forward
            forward[1] = 0 # set y value to 0
            left = 2*rotate(forward.norm(), angle = pi/2, axis = (0,1,0))
            self.playerManager.getActivePlayer().moveLeft(left)

    def rightKeyDown(self):
        if self.mode == 1:
            self.playerManager.changePlayer(1)
            print('eventHandler change', self.playerManager.getActivePlayer().getID())
            return
        else:
            forward = self.forward
            forward[1] = 0 # set y value to 0
            right = 2*rotate(forward.norm(), angle = -pi/2, axis = (0,1,0))
            self.playerManager.getActivePlayer().moveRight(right)

    def upKeyDown(self):
        if self.mode == 1:
            return
        else:
            forward = self.forward
            forward[1] = 0 # set y value to 0
            self.playerManager.getActivePlayer().moveUp(2*forward.norm())
    def downKeyDown(self):
        if self.mode == 1:
            return
        else:
            backward = -self.forward
            backward[1] = 0 # set y value to 0
            self.playerManager.getActivePlayer().moveDown(2*backward.norm())

    def spaceKeyDown(self):
        if self.playerManager.getActivePlayer().position.y == 0:
            #self.activePlayer = self.playerManager.getActivePlayer()
            self.playerManager.getActivePlayer().chargeJump()

    def fKeyDown(self):
        self.playerManager.toggle_friction()


    def sKeyDown(self):
#        if self.playerManager.getActivePlayer().position.y == 0:
            self.playerManager.getActivePlayer().setVelocity(vector(0,0,0))

    def oKeyDown(self):
##       if self.playerManager.getActivePlayer().position.y == 0:
            self.playerManager.getActivePlayer().setPosition(vector(-5,0,0))


    def jKeyDown(self):
        self.playerManager.train('jump')

    def nKeyDown(self):
        self.playerManager.train('nojump')

    def pKeyDown(self):
        self.playerManager.getActivePlayer().print_stats()

    def oneKeyDown(self):
        pass
        #self.activePlayer = self.env.p1

    def twoKeyDown(self):
        #self.activePlayer = self.env.p2
        print('Player 2 is active')

    def threeKeyDown(self):
        #self.activePlayer = self.env.p3
        print('Player 3 is active')


    def f1KeyDown(self):
        if self.mode == 0 or self.mode == 1:
            self.env.notPaused = not(self.env.notPaused)
            self.mode = not(self.mode)
            self.env.pauseCount = 0
            if self.env.notPaused == True:
                self.playerManager.unpause()

    def leftKeyDown_Paused(self):
            id = self.playerManager.getActivePlayer().getID()
            self.activePlayer = self.playerManager.activePlayers[ id - 2]
            print('new active player: ', self.playerManager.getActivePlayer().getID())
            self.playerManager.playerSelect(self.playerManager.getActivePlayer(), self.psBox)

    def rightKeyDown_Paused(self):
            id = self.playerManager.getActivePlayer().getID()
            self.activePlayer = self.playerManager.activePlayers[ id ]
            print('new active player: ', self.playerManager.getActivePlayer().getID())
            self.playerManager.playerSelect(self.playerManager.getActivePlayer(), self.psBox)

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
        self.playerManager.jump_on_keyup(self.env, self.playerManager.getActivePlayer())

    def handleClick(self,evt):
        if self.mode == 0:
            print ('click @', evt.pos)
            self.playerManager.createPlayer_Click(evt.pos, self.env)
        if self.mode == 2:
            self.playerManager.setTarget(evt.pos)

