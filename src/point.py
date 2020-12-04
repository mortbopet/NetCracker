import numpy as np
import math
import re

from src.direction import *

class Point:
    def __init__(self, x=None, y=None):
        self.x = int(x)
        self.y = int(y)

        self.angle, self.length = self.getRadAngle()
        self.dir = self.getDirection()

    def getDirection(self):
        if self.x == 0 and self.y == 0:
            return Direction.INVALID

        # Rectilinear wires
        if (self.x == 0):
            return Direction.N if(self.y > 0) else Direction.S
        elif (self.y == 0):
            return Direction.E if(self.x > 0) else Direction.W
        # diagonal wires
        elif(self.x > 0):
            return Direction.NE if(self.y > 0) else Direction.SE
        else:
            return Direction.NW if(self.y > 0) else Direction.SW

    def __eq__(self, value):
        return self.x == value.x and self.y == value.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __str__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Point(x, y)

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return Point(x, y)
    
    def __neg__(self):
        return Point(-self.x, -self.y)
    

    def __lt__(self, other):
        return self.length < other.length

    def getRadAngle(self):
        radius = np.hypot(self.x, self.y)
        theta = np.arctan2(self.y, self.x)
        return theta, radius
