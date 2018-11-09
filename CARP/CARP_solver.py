import math
import heapq
import numpy as np
import argparse
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
            

class RandomPS:
    def __init__(self, carp):
        self.carp = carp
        

    def construct_free(self):
        free = list()
        for i in range(self.carp.graph.vertices + 1):
            for j in range(i + 1, self.carp.graph.vertices + 1):
                if self.carp.graph.edge_demand[i][j] > 0:
                    free.append((i, j))
                    free.append((j, i))
        return free

    # criteria 1 : minimization ratio cost(i, j)/rmn_dmnd(i, j) once (i, j) is treated; 
    def criteria_1(self, u, u_slt):
        u_cost = self.carp.graph.adj_matrix[u[0]][u[1]]
        u_dmnd = self.carp.graph.edge_demand[u[0]][u[1]]
        u_slt_cost = self.carp.graph.adj_matrix[u_slt[0]][u_slt[1]]
        u_slt_dmnd = self.carp.graph.edge_demand[u_slt[0]][u_slt[1]]
        
        return u_cost / u_dmnd < u_slt_cost / u_slt_dmnd

    # criteria 2 : maximization ratio cost(i, j)/rmn_dmnd(i, j); 
    def criteria_2(self, u, u_slt):
        u_cost = self.carp.graph.adj_matrix[u[0]][u[1]]
        u_dmnd = self.carp.graph.edge_demand[u[0]][u[1]]
        u_slt_cost = self.carp.graph.adj_matrix[u_slt[0]][u_slt[1]]
        u_slt_dmnd = self.carp.graph.edge_demand[u_slt[0]][u_slt[1]]
        
        return u_cost / u_dmnd > u_slt_cost / u_slt_dmnd

    # criteria 3 : maximize cost(j, depot)
    def criteria_3(self, u, u_slt):
        u_end_depot = self.carp.graph.mul_sp[u[1]][self.carp.depot]
        u_slt_end_depot = self.carp.graph.mul_sp[u_slt[1]][self.carp.depot] 

        return u_end_depot > u_slt_end_depot

    # criteria 4 : minimize cost(j, depot)
    def criteria_4(self, u, u_slt):
        u_end_depot = self.carp.graph.mul_sp[u[1]][self.carp.depot]
        u_slt_end_depot = self.carp.graph.mul_sp[u_slt[1]][self.carp.depot] 

        return u_end_depot < u_slt_end_depot
        
    # if vehicls is less than half-full than criteria 3
        # else criteria 4
    def criteria_5(self, u, u_slt, k):
        if k + 1 < self.carp.vehicles:
            return self.criteria_3(u, u_slt)
        else:
            return self.criteria_4(u, u_slt)


    
    def better(self, u, u_slt, k):
        choice = np.random.choice([i for i in range(1, 6)], size=1, p=[0.2, 0.2, 0.2, 0.2, 0.2])

        if choice == 1:
            return self.criteria_1(u, u_slt)
        elif choice == 2:
            return self.criteria_2(u, u_slt)
        elif choice == 3:
            return self.criteria_3(u, u_slt)
        elif choice == 4:
            return self.criteria_4(u, u_slt)
        else:
            return self.criteria_5(u, u_slt, k)

    
    def path_scanning(self):

        k = 0
        capacity = self.carp.capacity

        free = self.construct_free()
        road = list()
        load = list()
        cost = list()

        while free:
            road.append(list())
            load.append(0)
            cost.append(0)
            i = 1
            while True:
                d_min = math.inf
                u_slt = ()

                for u in free:
                    u_dmnd = self.carp.graph.edge_demand[u[0]][u[1]]
                    if load[k] + u_dmnd <= capacity:
                        
                        d = self.carp.graph.mul_sp[i][u[0]] 
                        if d < d_min:
                            d_min = d
                            u_slt = u
                        elif d == d_min and self.better(u, u_slt, k):
                            u_slt = u
                if not free or d_min == math.inf:
                    break
                road[k].append(u_slt)
                free.remove(u_slt)
                free.remove((u_slt[1], u_slt[0]))
                u_slt_dmnd = self.carp.graph.edge_demand[u_slt[0]][u_slt[1]]
                u_slt_cost = self.carp.graph.adj_matrix[u_slt[0]][u_slt[1]]
                load[k] = load[k] + u_slt_dmnd
                cost[k] = cost[k] + d_min + u_slt_cost
                i = u_slt[1]
                
            rtn_cost = self.carp.graph.mul_sp[i][1]
            cost[k] = cost[k] + rtn_cost
            k = k + 1

def read_file(file_name):
    dict = {'matrix': np.empty((0, 4), int)}
    with open(file_name) as fp:
        for i, line in enumerate(fp):
            if i < 8:
                key, value = line.replace(':', '').replace('\n', '').split('  ')
                key = " ".join(key.split()).replace(' ', '_').replace('-', '_').lower()
                try:
                    value = int(value)
                except ValueError:
                    pass
                dict[key] = value
            elif i > 8:
                try:
                    dict['matrix'] = np.vstack((dict['matrix'], np.fromstring(" ".join(line.split()), dtype=int, sep=' ')))
                except ValueError:
                    pass
    return dict


class CARP:
    def __init__(self, name, vertices, depot, required_edges, non_required_edges, vehicles, capacity, total_cost_of_required_edges, matrix):
        self.name = name
        self.vertices = vertices
        self.depot = depot
        self.required_edges = required_edges
        self.non_required_edges = non_required_edges
        self.vehicles = vehicles
        self.capacity = capacity
        self.total_cost_of_required_edges = total_cost_of_required_edges
        self.matrix = matrix
        self.graph = Graph(self.vertices, self.matrix)
        self.graph.multiple_shortest_path()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('instance_file', help='the absolute path of the test CARP instance file')
    parser.add_argument('-t', dest='termination', help='a positive number which indicates how many seconds the algorithm can spend on this instance.')
    parser.add_argument('-s', dest='random_seed', help='the random seed used in this run.')
    parse_res = parser.parse_args()

    dict = read_file(parse_res.instance_file)
    carp = CARP(dict['name'], dict['vertices'], dict['depot'], dict['required_edges'], dict['non_required_edges'], dict['vehicles'], dict['capacity'], dict['total_cost_of_required_edges'], dict['matrix'])
    randomPS = RandomPS(carp)
    randomPS.path_scanning()
    