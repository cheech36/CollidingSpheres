from __future__ import print_function
from __future__ import division
from visual import *
from collision import bp

class flr:
    def __init__(self, position):
        self.tolerance = .05
        self.rect1 = box(length=110, height=.5, width = 50, material = materials.wood)
        self.rect1.pos = (0, position, 0)
        self.rect1.opacity = .2
        self.rect1.pos = (0, position - .25, 0)
        self.boundary = bp('y', -self.tolerance,'neg')

    def getFloorTop(self):
        return self.rect1.pos.y + self.rect1.height/2

    def friction(self, speed):
        speed.x -=  (self.dt * self.uFric * speed.norm().x)
        if( mag( vector(speed.x,0,0) ) < self.restThreshold ):
            speed.x = 0
        speed.z -=  (self.dt * self.uFric * speed.norm().z)
        if( mag( vector(speed.z,0,0) ) < self.restThreshold ):
            speed.z = 0
        return speed

    def check(self, player):
        return self.boundary.check(player)

    def gettype(self):
        return 2

    def getdata(self):
        return self.boundary.getdata()

class obstacle:
    def __init__(self, position, ax, h, w , boundary = 'none'):
        self.rect1 = box(axis = ax, height = h , width = w, material = materials.bricks)
        self.rect1.pos = position
        self.boundary  = boundary

    def addBoundingSphere(self, boundingSphere):
        self.boundaryList.append(boundingSphere)

    def addBoundingBox(self, boundingBox):
        self.boundaryList.append(boundingBox)

    def check(self, player):
        return self.boundary.check(player)

    def getdata(self):
        return self.boundary.getdata()

    def gettype(self):
        return 1