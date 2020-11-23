# Adapted from https://gist.github.com/anirudhjayaraman/272e920079fd8cea97f81487ef1e78a3

class Vertex:
    def __init__(self, vertex):
        self.name = vertex
        self.visitCount = 0
        self.neighbors = []
        
    def addNeighbor(self, neighbor):
        if neighbor not in self.neighbors:
            self.neighbors.append(neighbor)
        else:
            return False
        
    def addNeighbors(self, neighbors):
        for neighbor in neighbors:
            if neighbor not in self.neighbors:
                self.neighbors.append(neighbor)
            else:
                return False
        
    def __repr__(self):
        return str(self.neighbors)

class Graph:
    def __init__(self):
        self.vertices = {}
    
    def addVertex(self, vertex):
        if vertex not in self.vertices:
            self.vertices[vertex] = Vertex(vertex)

    def addVertices(self, vertices):
        for vertex in vertices:
            if vertex not in self.vertices:
                self.vertices[vertex] = Vertex(vertex)
            
    def addEdge(self, vertex_from, vertex_to):
        if vertex_from in self.vertices and vertex_to in self.vertices:
            self.vertices[vertex_from].addNeighbor(vertex_to)
            self.vertices[vertex_to].addNeighbor(vertex_from)
        else:
            return False

    def addEdges(self, edges):
        for edge in edges:
            self.addEdge(edge[0],edge[1]) 

    def visitVertex(self, vertex):
        if vertex in self.vertices:
            self.vertices[vertex].visitCount += 1         
        else:
            return False

    def adjacencyList(self):
        if len(self.vertices) >= 1:
                return [str(key) + ":" + str(self.vertices[key]) for key in self.vertices.keys()]  
        else:
            return dict()


