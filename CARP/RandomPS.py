import math
import time
import numpy as np
import random


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
                for u in free:
                    d = self.carp.graph.mul_sp[i][u[0]] 
                    if d < d_min:
                        d_min = d
                        u_slt = u
                    elif d == d_min:
                        choice = random.randint(0,1)
                        if choice == 1:
                            u_slt = u
                   
                if not free or d_min == math.inf:
                    break
    
                if load[k] + self.carp.graph.edge_demand[u_slt[0]][u_slt[1]] > capacity:
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
        return [sum(cost), road]
        # self.display(road, cost)

    def s_format (self, s):
        s_print = []
        for p in s:
            s_print.append(0)
            s_print.extend(p)
            s_print.append(0)
        return s_print

    def display(self, road, cost):  
        print("s", (",".join(str(d) for d in self.s_format(road))).replace(" ", ""))
        print("q", cost)


    def run(self, t):
        start = time.time()
        best_res = None
        end = start
        while end - start < t:
            cost, road = self.path_scanning()
            if best_res is None:
                best_res = [cost, road]
            if cost < best_res[0]:
                best_res = [cost, road]
            end = time.time()
        return best_res
        # self.display(best_res[1], best_res[0])

