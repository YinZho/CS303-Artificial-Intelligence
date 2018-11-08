import math
import heapq
import numpy as np
from collections import defaultdict


class Graph:
    def __init__(self, vertices, matrix):
        self.vertices = vertices
        self.adj_matrix = [[0 for i in range(vertices + 1)]
                           for j in range(vertices + 1)]
        self.edge_demand = [[0 for i in range(vertices + 1)]
                            for j in range(vertices + 1)]

        self.adj_list = defaultdict(set)
        
        self.mul_sp = []
        

        for row in matrix:
            src, dst, cost, demand = row

            self.adj_matrix[src][dst] = cost
            self.adj_matrix[dst][src] = cost

            self.adj_list[src].add((dst, cost))
            self.adj_list[dst].add((src, cost))

            self.edge_demand[src][dst] = demand
            self.edge_demand[dst][src] = demand

    def dijkstra(self, src):
        V = self.vertices

        dist = [math.inf for i in range(V + 1)]
        dist[src] = 0
        isvisited = set()

        heap = []

        heapq.heappush(heap, (0, src))
        
        while heap:
            u = heapq.heappop(heap)[1]
            isvisited.add(u)
            for v, cost in self.adj_list[u]:
                if u != math.inf and dist[v] > dist[u] + cost and v not in isvisited:
                    dist[v] = dist[u] + cost
                    heapq.heappush(heap, (dist[v], v))
        
        return dist


    def multiple_shortest_path(self):
        for i in range(self.vertices + 1):
            self.mul_sp.append(self.dijkstra(i))
            

if __name__ == '__main__':
    matrix = np.array([[1,3,4,4],
                      [1,4,2,2],
                      [4,2,8,0],
                      [4,5,5,5],
                      [2,5,1,1],
                      [5,6,13,2],
                      [6,7,15,0],
                      [2,7,3,3],
                      [2,3,10,5],
                      [3,7,6,6]
                     ])
    graph = Graph(7, matrix)
    graph.multiple_shortest_path()
    print(graph.mul_sp)