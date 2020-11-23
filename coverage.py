import numpy as np
import sys
from Queue import Queue
import time

from graph import *

class Coverage:
    def __init__(self, height, width, initialPos):
        self.neighbors = np.zeros((3, 3))		
        self.curPos = initialPos
        self.coveredGraph = Graph()
        self.coveredGraph.addVertex(self.curPos)
        self.coveredGraph.visitVertex(self.curPos)
        self.finished = False
        self.nextCell = False #south:0, east:1, north:2, west:3
        self.isNeighborsSet = False
        self.calculatedPath = []
        self.path = [self.curPos]
    
    def distance(self, v1, v2):
        """ 
        Distance function in the grid. 
        Eucledian seems to do worse in terms of total coverage time.
        This possibly bcs neighbourhoods are 4-sided (not 8) and diagonal movements are not allowed. 
        I'm sticking to Manhattan for now.
        """
        #return pow(v1[0]-v2[0],2) + pow(v1[1]-v2[1],2)
        return abs(v1[0]-v2[0]) + abs(v1[1]-v2[1])

    def isCovered(self, ):
        '''
        Indicator flag on whether we visited all reachable positions. 
        '''
        return self.finished

    def searchNotVisited(self,):
        '''
        Search for the nearest cell/node to visit when all immediate neighbors are visited.
        '''
        minDistance = float('inf')
        targetCell = False
        for key, vertex in self.coveredGraph.vertices.items():
            if vertex.visitCount == 0:
                dist = self.distance(self.curPos, key)
                if dist < minDistance and key!=self.curPos:
                    minDistance = dist
                    targetCell = key

        if not targetCell:
	        return False

        queue = Queue()
        queue.put(self.curPos)
        cameFrom = {}
        cameFrom[self.curPos] = None

        while queue.qsize() > 0:
            current = queue.get()
            if current == targetCell:
                break

            for next in self.coveredGraph.vertices[current].neighbors:
                if next not in cameFrom:
                    queue.put(next)
                    cameFrom[next] = current
        
        current = targetCell
        while current != self.curPos:
            self.calculatedPath.append(current)
            current = cameFrom[current]

        return True
    
    def calculateDirection(self, cell):
        '''
        Convert tuple-enumerated neighbors to the direction notation in the simulation .
        '''
        difference = (self.curPos[0]-cell[0], self.curPos[1]-cell[1])
        if difference[0] == 1:
            return 2
        if difference[0] == -1:
            return 0
        if difference[1] == 1:
            return 3
        if difference[1] == -1:
            return 1 
        return -1

    def choose(self,):
        """
        Choose where to go next.
        If one of the 4 neighbors is avaialable, go there.
        Else calculate the path to nearest non-visited cell.  
        """
        if not self.isNeighborsSet:
            print("To choose, set neighbors first.")            
            return None
        
        nextCell = None
        result = -1

        if len(self.calculatedPath) > 0:
            self.nextCell = self.calculatedPath.pop()            
            return self.calculateDirection(self.nextCell)
        
        neighbors = [(1,0), (0, 1), (1, 2),	(2, 1) ]
        for cell in neighbors:
            if self.neighbors[cell] > -1:
                _cell = (self.curPos[0] + cell[0] - 1, self.curPos[1] + cell[1] - 1)
                self.coveredGraph.addVertex( _cell )
                self.coveredGraph.addEdge(_cell, self.curPos)
                visits = self.coveredGraph.vertices[_cell].visitCount
                if visits == 0:
                    nextCell = _cell
                    result = self.calculateDirection(_cell)

        if not nextCell:
            searchResult = self.searchNotVisited()
            if searchResult:
                nextCell = self.calculatedPath.pop()
                result = self.calculateDirection(nextCell)
            else:
                self.finished = True
                return None
        
        self.nextCell = nextCell
        return result

    def updatePosition(self,):
        """
        Update the position after choosing the next cell.
        This is needed since it takes time to actually go to the chosen position in the simulation.
        """
        if not self.nextCell:
            if not self.finished:
                print('To update position, run \'choose\' method first.')
            return
        
        self.curPos = self.nextCell
        self.path.append(self.curPos)
        self.coveredGraph.visitVertex(self.curPos)
        self.nextCell = False
        self.isNeighborsSet = False
    
    def setNeighbors(self, south, east, north, west):
        """
        Set the neighbor info in the graph for the current position, using the sensor/surrondings info.
        """
        self.neighbors[ 1, 0 ] = south
        self.neighbors[ 0, 1 ] = east
        self.neighbors[ 1, 2 ] = north
        self.neighbors[ 2, 1 ] = west
        self.isNeighborsSet = True

    @staticmethod
    def buildTestEnvironment(height, width, numOfObstacles):
        """
        Builds a simple test grid with the given number of obstacles placed randomly.
        """
        gird = None
        if numOfObstacles == 0:
            grid = np.zeros((height,width))
        else:
            grid = np.zeros((height*width,))
            grid[ np.random.choice(range(height*width), numOfObstacles, replace=False) ] = -1
            grid = grid.reshape((height, width))

        grid = np.hstack( (-1*np.ones( (width,1) ), grid, -1*np.ones((width,1)) ) )
        grid = np.vstack( (-1*np.ones(height+2), grid, -1*np.ones(height+2) ) )		
        grid[1,1] = 0
        return grid      
    
    @staticmethod    
    def getSurroundings(grid, position):
        """
            This simulates the robot fetching the information from the sensors on the 4 sides.
        """
        return grid[position[0]+1,   position[1]],   \
		        grid[position[0],position[1]+1],     \
                grid[position[0]+1,  position[1]+2],   \
                grid[position[0]+2,position[1]+1]

    @staticmethod
    def cover(gridHeight, gridWidth, obstacleNumber):
        """
        Example usage.
        """
        testGrid =  Coverage.buildTestEnvironment(gridHeight, gridWidth, obstacleNumber)        
        cov = Coverage(gridHeight, gridWidth, (0,0))
        
        testGrid[(1,1)] = 1
        while not cov.isCovered():
            a,b,c,d = Coverage.getSurroundings(testGrid, cov.curPos)
            cov.setNeighbors(  a,b,c,d )
            nextCell = cov.choose()
            print nextCell
            cov.updatePosition()
        
        visit = 0.0
        for key, value in cov.coveredGraph.vertices.items():
            visit += value.visitCount
        return visit/( gridHeight*gridWidth - obstacleNumber - 1)


if __name__ == "__main__":
    gridHeight = 5
    gridWidth = 5
    trials = 1
    obstacleNumber = 0

    visits = 0
    turns = 0.0
    for i in range(trials):
        visits += Coverage.cover(gridHeight, gridWidth, obstacleNumber)
    print visits/trials

	
