import time
from collections import defaultdict
from Graph import Graph
import numpy as np

class TabuSearch:
    def __init__(self, S, graph):
        self.S = S
        self.S_B = S
        self.S_BF = S
        self.graph = graph


    def cal_sol_cost(self, roads):
        pass
    

    def gen_neighbor_SI(self, not_adj):
        s_roads = self.S[1]
        move = []
        
        for r_idx, road in enumerate(s_roads):
            for i in range(len(road)):
                delta_cost = 0
                edge_cost = self.graph.edge_demand[road[i][0]][road[i][1]]

                delta_cost -= edge_cost
                if i-1 >= 0 and i+1 < len(road):
                    delta_cost -= self.graph.mul_sp[road[i-1][1]][road[i][0]]
                    delta_cost -= self.graph.mul_sp[road[i][1]][road[i+1][0]]
                    delta_cost += self.graph.mul_sp[road[i-1][1]][road[i+1][0]]
                elif i == len(road)-1:
                    delta_cost -= self.graph.mul_sp[road[i-1][1]][road[i][0]]
                    delta_cost += self.graph.mul_sp[road[i-1][1]][1]
                elif i == 0:
                    delta_cost -= self.graph.mul_sp[road[i][1]][road[i+1][0]]
                    delta_cost += self.graph.mul_sp[1][road[i+1][0]]

                edge = road[i]
                del road[i]
                
                for idx, not_adj_edge in not_adj.items():
                    if r_idx == idx:
                        pass
                    else:
                        for pos in not_adj_edge:
                            tmp_delta_cost = delta_cost
                            tmp_delta_cost -= self.graph.mul_sp[s_roads[idx][pos][1]][s_roads[idx][pos+1][0]]
                            direction_l_cost = self.graph.mul_sp[s_roads[idx][pos][1]][edge[0]] + self.graph.mul_sp[edge[1]][s_roads[idx][pos+1][0]]
                            direction_r_cost = self.graph.mul_sp[s_roads[idx][pos][1]][edge[1]] + self.graph.mul_sp[edge[0]][s_roads[idx][pos+1][0]]
                            if direction_l_cost < direction_r_cost:
                                s_roads[idx].insert(pos+1, edge)
                                tmp_delta_cost += direction_l_cost
                            else:
                                s_roads[idx].insert(pos+1, (edge[1], edge[0]))
                                tmp_delta_cost += direction_r_cost
                            
                            move.append(tmp_delta_cost+edge_cost, s_roads)

                            del s_roads[idx][pos+1]
                        
                        # front end
                        tmp_delta_cost = delta_cost
                        tmp_delta_cost -= self.graph.mul_sp[1][s_roads[idx][0]]
                        tmp_delta_cost += self.graph.mul_sp[1][edge[0]]
                        tmp_delta_cost += self.graph.mul_sp[edge[1]][s_roads[idx][0]]
                        s_roads[idx].insert(0, edge)
                        move.append(tmp_delta_cost+edge_cost, s_roads)

                        # back end
                        tmp_delta_cost = delta_cost
                        tmp_delta_cost -= self.graph.mul_sp[s_roads[idx][len(s_roads[idx])-1]][1]
                        tmp_delta_cost += self.graph.mul_sp[s_roads[idx][len(s_roads[idx])-1]][edge[0]]
                        tmp_delta_cost += self.graph.mul_sp[edge[1]][1]
                        s_roads[idx].insert(len(s_roads[idx]), edge)
                        move.append(tmp_delta_cost+edge_cost, s_roads)

                road.insert(i, edge)

        return move    

    
    def gen_neighbor_DI(self, not_adj):
        s_roads = self.S[1]
        move = []
        delta_cost = 0
        for r_idx, road in enumerate(s_roads):
            for i in range(len(road)-1):
                edge_cost = self.graph.edge_demand[road[i][0]][road[i][1]] + self.graph.edge_demand[road[i+1][0]][road[i+1][1]]
                edge_cost += self.graph.mul_sp[road[i][1]][road[i+1][0]]
                delta_cost -= edge_cost

                if  i-1 >= 0 and i+2 < len(road):
                    delta_cost -= self.graph.mul_sp[edge_1[1]][road[i+2][0]]
                elif i == len(road) - 2:
                    delta_cost -= self.graph.mul_sp[road[i-1][1]][edge_0[0]]
                elif i == 0:

                for idx, not_adj_edge in not_adj.items():
                    if r_idx == idx:
                        pass
                    else:
                        for pos in not_adj_edge:
                            delta_cost -= self.graph.mul_sp[s_roads[idx][pos][1]][s_roads[idx][pos+1][0]]
                            direction_l_cost = self.graph.mul_sp[s_roads[idx][pos][1]][edge_0[0]] + self.graph.mul_sp[edge_1[1]][s_roads[idx][pos+1][0]]
                            direction_r_cost = self.graph.mul_sp[s_roads[idx][pos][1]][edge_1[1]] + self.graph.mul_sp[edge_0[0]][s_roads[idx][pos+1][0]]
                            if direction_l_cost < direction_r_cost:
                                s_roads[idx].insert(pos+1, edge_0)
                                s_roads[idx].insert(pos+2, edge_1)
                                delta_cost += direction_l_cost
                            else:
                                s_roads[idx].insert(pos+1, edge_1)
                                s_roads[idx].insert(pos+2, edge_0)
                                delta_cost += direction_r_cost

                            move.append(delta_cost+edge_dmd, s_roads)
                            
                            del s_roads[idx][pos+1]
                            del s_roads[idx][pos+2]

                road.insert[i, edge_0]
                road.insert[i, edge_1]

        return move

    def gen_neighbor_SWAP(self):

        
    def gen_neighbor(self):
        moves = []
        s_roads = self.S[1]
        not_adj = defaultdict()
        for r_idx, road in enumerate(s_roads):
            not_adj[r_idx] = []
            for i in range(len(road) - 1):
                if road[i][1] != road[i + 1][0]:
                    not_adj[r_idx].append(i)
        print(not_adj)
        moves.append(self.gen_neighbor_SI(not_adj))
        moves.append(self.gen_neighbor_DI(not_adj))


             

    def tabu_solve(self):
        pass
        

if __name__ == '__main__':
    init_S = (3762, [[(1, 2), (2, 3), (2, 4), (4, 5), (9, 10), (11, 59), (59, 69), (69, 4)], [(69, 58), (58, 60), (60, 62), (62, 66), (66, 68), (62, 63), (63, 65), (60, 61), (58, 59), (59, 44), (44, 46)], [(58, 57), (57, 42), (43, 44), (44, 45), (46, 47), (47, 49), (49, 51), (51, 21), (21, 22), (22, 75), (75, 23)], [(11, 12), (12, 16), (16, 13), (13, 14), (15, 17), (15, 18), (18, 19), (19, 21), (52, 50), (50, 49), (47, 48), (52, 54), (19, 20), (20, 76)], [(56, 55), (41, 35), (35,
32), (32, 33), (32, 34), (32, 31), (31, 23)]])
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
    tabuSearch = TabuSearch(init_S, graph)
    tabuSearch.gen_neighbor()

