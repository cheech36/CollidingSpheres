from visual import *


class particle:
    
    def __init__(self, position ,id):
        self.id           = id
        self.type         = 'particle'
        self.time         = 0 
        self.dt           = .01
        self.mass         = 0
        self.dr           = vector(0,  0, 0)

        self.position     = position             ## Location of player center
        self.velocity     = vector(0,0,0)
        self.acceleration = vector(0,0,0)
        self.tolerance    = .001
        self.restThreshold    = .001

        self.momentum     = vector(0,0,0)
        self.netForce     = vector(0,0,0)
        self.energy       = 0
        self.forcesList = list()
 
        self.body         = sphere(pos=vector(0,0,0), radius = 0)                ## any simple shape
        self.origin       = vector(position)

    def getPosition(self):
        return self.position

    def updatePosition(self):                   
        self.dr = self.velocity * self.dt
        self.position += self.dr
        self.body.pos = self.position   

    def changePosition(self, dr):
            self.position += dr
            self.updatePosition()
            
    def setPosition(self, newPosition):
        self.position = newPosition
    
    def getVelocity(self):       
        return self.velocity

    def updateVelocity(self):
        self.velocity += self.acceleration * self.dt

    def changeVelocity(self, dv):
        self.velocity += dv

    def setVelocity(self, newVelocity):
        self.velocity = newVelocity

    def getAcceleration(self):
        return self.acceleration

    def setAcceleration(self, newAcceleration):
        self.acceleration = newAcceleration

    def changeAcceleration(self, newAcceleration):
        self.acceleration += newAcceleration

    def getForce(self):
        return self.netForce

    def changeForce(self, newForce):
        self.netForce += newForce

    def setForce(_m, newForce):
        self.netForce = newForce

    def getEnergy(self):
        self.energy = .5*self.mass*self.velocity.mag2
        return  self.energy

    def calcMomentum(self):
        self.momentum = self.mass * self.velocity

    def getMomentum(self):
        return self.momentum

    def getID(self):
        return self.id

    def age(self):
        self.time += dt

    def getAge(self):
        return self.time

    def addForce(self, forceName):
        self.forcesList.append(forceName)

    def removeForce(self, forceName):
        self.forcesList.remove(forceName)

    def getForcesList(self):
        return self.forcesList

    def moveRight(self):
        initialSpeed = self.getVelocity().x
        finalSpeed   =  self.getVelocity().x + 2
        if self.position.y == 0 and (self.getVelocity().x < self.maxSpeed or finalSpeed < initialSpeed):
            self.changeVelocity( (2,0,0 ) )

    def getType(self):
        return self.type

    def moveLeft(self):
        initialSpeed = self.getVelocity().x
        finalSpeed   =  self.getVelocity().x + -2
        if self.position.y == 0 and (self.getVelocity().x > -self.maxSpeed or finalSpeed > initialSpeed):
            self.changeVelocity( (-2,0,0 ) )

    def moveUp(self):
        initialSpeed = self.getVelocity().z
        finalSpeed   =  self.getVelocity().z + -2
        if self.position.y == 0 and (self.getVelocity().z > -self.maxSpeed or finalSpeed > initialSpeed):
            self.changeVelocity( (0,0,-2 ) )

    def moveDown(self):
        initialSpeed = self.getVelocity().z
        finalSpeed   =  self.getVelocity().z + 2
        if self.position.y == 0 and (self.getVelocity().z < self.maxSpeed or finalSpeed < initialSpeed):
            self.changeVelocity( (0,0,2 ) )

    def getOrigin(self):
        return vector(self.origin)

    def reset_position(self, axis = 3):
        origin = vector(self.origin)
        if axis == 3:
            self.setPosition(origin)

        elif axis == 0:
            self.position.x = origin.x

        elif axis == 1:
            self.position.y = origin.y

        elif axis == 2:
            self.position.z = origin.z

        self.updatePosition()


    def print_stats(self):
        print('position: ',self.position)
        print('velocity: ',self.velocity)
        print('acceleration:', self.acceleration)