from __future__ import print_function
from __future__ import division
from visual import *
from collision import bp



class flr:

    def __init__(m_, position):
        m_.tolerance = .05
        m_.rect1 = box(length=110, height=.5, width = 50, material = materials.wood)
        m_.rect1.pos = (0, position, 0)
        m_.rect1.opacity = .2
        m_.rect1.pos = (0, position - .25, 0)

        m_.boundary = bp('y', -m_.tolerance,'neg')


    def getFloorTop(m_):
        return m_.rect1.pos.y + m_.rect1.height/2

    def friction(m_, speed):
        speed.x -=  (m_.dt * m_.uFric * speed.norm().x)
        if( mag( vector(speed.x,0,0) ) < m_.restThreshold ):
            speed.x = 0
        speed.z -=  (m_.dt * m_.uFric * speed.norm().z)
        if( mag( vector(speed.z,0,0) ) < m_.restThreshold ):
            speed.z = 0

        return speed

    def check(m_, player):
        return m_.boundary.check(player)

    def gettype(m_):
        return 2

    def getdata(m_):
        return m_.boundary.getdata()


class obstacle:

    def __init__(m_, position, ax, h, w , boundary = 'none'):
        m_.rect1 = box(axis = ax, height = h , width = w, material = materials.bricks)
        m_.rect1.pos = position
        m_.boundary  = boundary

    def addBoundingSphere(m_, boundingSphere):
        m_.boundaryList.append(boundingSphere)


    def addBoundingBox(m_, boundingBox):
        m_.boundaryList.append(boundingBox)

    def check(m_, player):
        return m_.boundary.check(player)

    def getdata(m_):
        return m_.boundary.getdata()

    def gettype(m_):
        return 1