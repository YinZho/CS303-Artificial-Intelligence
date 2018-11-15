import time
from collections import defaultdict
from Graph import Graph
import numpy as np
from CARP_solver import read_file, CARP, argparse
import heapq
import copy

class TabuSearch:
    def __init__(self, S, graph):
        self.S = S
        self.S_B = S
        self.S_BF = S
        self.graph = graph


    def cal_sol_cost(self, moves):
        for move in moves:
            cost = 0
            cnt = 0
            for road in move:
                cnt += len(road)
                r_len = len(road)
                cost += self.graph.adj_matrix[road[0][0]][road[0][1]]
                cost += self.graph.mul_sp[1][road[0][0]]
                cost += self.graph.mul_sp[road[0][1]][road[1][0]]
                for i in range(1, r_len-1):
                    cost += self.graph.adj_matrix[road[i][0]][road[i][1]]
                    cost += self.graph.mul_sp[road[i][1]][road[i+1][0]]
                cost += self.graph.adj_matrix[road[r_len-1][0]][road[r_len-1][1]]
                cost += self.graph.mul_sp[road[r_len-1][1]][1]
                
                    
            print(str(cost) + " " + str(cnt))
                
    

    def gen_neighbor_SI(self, not_adj):
        s_roads = self.S[1]
        move = []
        
        for r_idx, road in enumerate(s_roads):
            for i in range(len(road)):
                edge = road[i]
                del s_roads[r_idx][i]
                
                for idx, not_adj_edge in not_adj.items():
                    if r_idx == idx:
                        pass
                    else:
                        for pos in not_adj_edge:
                            direction_l_cost = self.graph.mul_sp[s_roads[idx][pos][1]][edge[0]] + self.graph.mul_sp[edge[1]][s_roads[idx][pos+1][0]]
                            direction_r_cost = self.graph.mul_sp[s_roads[idx][pos][1]][edge[1]] + self.graph.mul_sp[edge[0]][s_roads[idx][pos+1][0]]
                            if direction_l_cost < direction_r_cost:
                                s_roads[idx].insert(pos+1, edge)
                            else:
                                s_roads[idx].insert(pos+1, (edge[1], edge[0]))
                            
                            
                            move.append(copy.deepcopy(s_roads))
                            del s_roads[idx][pos+1]
                    
                        direction_l_cost = self.graph.mul_sp[1][edge[0]] + self.graph.mul_sp[edge[1]][s_roads[idx][0][0]]
                        direction_r_cost = self.graph.mul_sp[1][edge[1]] + self.graph.mul_sp[edge[0]][s_roads[idx][0][0]]
                        if direction_l_cost < direction_r_cost:
                            s_roads[idx].insert(0, edge)
                        else:
                            s_roads[idx].insert(0, (edge[1], edge[0]))
                        move.append(copy.deepcopy(s_roads))
                        del s_roads[idx][0]


                        r_len = len(s_roads[idx])
                        direction_l_cost = self.graph.mul_sp[s_roads[idx][r_len-1][1]][edge[0]] + self.graph.mul_sp[edge[1]][1]
                        direction_r_cost = self.graph.mul_sp[s_roads[idx][r_len-1][1]][edge[1]] + self.graph.mul_sp[edge[0]][1]
                        if direction_l_cost < direction_r_cost:
                            s_roads[idx].insert(r_len, edge)
                        else:
                            s_roads[idx].insert(r_len, (edge[1], edge[0]))
                        move.append(copy.deepcopy(s_roads))
                        del s_roads[idx][r_len]

                s_roads[r_idx].insert(i, edge)


        return move    

    
    def gen_neighbor_DI(self, not_adj):
        s_roads = self.S[1]
        move = []
        
        for r_idx, road in enumerate(s_roads):
            for i in range(len(road)-1):

                edge_0 = road[i]
                edge_1 = road[i+1]
                del s_roads[r_idx][i]
                del s_roads[r_idx][i]

                for idx, not_adj_edge in not_adj.items():
                    if r_idx == idx:
                        pass
                    else:
                        for pos in not_adj_edge:
                            direction_l_cost = self.graph.mul_sp[s_roads[idx][pos][1]][edge_0[0]] + self.graph.mul_sp[edge_1[1]][s_roads[idx][pos+1][0]]
                            direction_r_cost = self.graph.mul_sp[s_roads[idx][pos][1]][edge_1[1]] + self.graph.mul_sp[edge_0[0]][s_roads[idx][pos+1][0]]
                            if direction_l_cost < direction_r_cost:
                                s_roads[idx].insert(pos+1, edge_0)
                                s_roads[idx].insert(pos+2, edge_1)
                                
                            else:
                                s_roads[idx].insert(pos+1, (edge_1[1], edge_1[0]))
                                s_roads[idx].insert(pos+2, (edge_0[1], edge_0[0]))
                               

                            move.append(copy.deepcopy(s_roads))            
                            del s_roads[idx][pos+1]
                            del s_roads[idx][pos+1]
                        
                        # front end
                        direction_l_cost = self.graph.mul_sp[1][edge_0[0]] + self.graph.mul_sp[edge_1[1]][s_roads[idx][0][0]]
                        direction_r_cost = self.graph.mul_sp[1][edge_1[1]] + self.graph.mul_sp[edge_0[0]][s_roads[idx][0][0]]
                        if direction_l_cost < direction_r_cost:
                            s_roads[idx].insert(0, edge_0)
                            s_roads[idx].insert(1, edge_1)
                        else:
                            s_roads[idx].insert(0, (edge_1[1], edge_1[0]))
                            s_roads[idx].insert(1, (edge_0[1], edge_0[0]))
                        
                        move.append(copy.deepcopy(s_roads))
                        del s_roads[idx][0]
                        del s_roads[idx][0]

                        
                        # back end
                        r_len = len(s_roads[idx])
                        direction_l_cost = self.graph.mul_sp[s_roads[idx][r_len-1][1]][edge_0[0]] + self.graph.mul_sp[edge_1[1]][1]
                        direction_l_cost = self.graph.mul_sp[s_roads[idx][r_len-1][1]][edge_1[1]] + self.graph.mul_sp[edge_0[0]][1]
                        if direction_l_cost < direction_r_cost:
                            s_roads[idx].insert(r_len, edge_0)
                            s_roads[idx].insert(r_len+1, edge_1)
                        else:
                            s_roads[idx].insert(r_len, (edge_1[1], edge_1[0]))
                            s_roads[idx].insert(r_len+1, (edge_0[1], edge_0[0]))
                        
                        move.append(copy.deepcopy(s_roads))
                        del s_roads[idx][r_len]
                        del s_roads[idx][r_len]

                s_roads[r_idx].insert(i, edge_0)
                s_roads[r_idx].insert(i+1, edge_1)
        return move

    # def gen_neighbor_SWAP(self):

        
    def gen_neighbor(self):
        moves = []
        s_roads = self.S[1]
        not_adj = defaultdict()
        for r_idx, road in enumerate(s_roads):
            not_adj[r_idx] = []
            for i in range(len(road) - 1):
                if road[i][1] != road[i + 1][0]:
                    not_adj[r_idx].append(i)
        moves += self.gen_neighbor_SI(not_adj)
        moves += self.gen_neighbor_DI(not_adj)
        # heapq.heapify(moves)
        with open("out.txt", 'w') as file:
            for s in moves:
                file.write(str(s))
                file.write("\n\n")
        self.cal_sol_cost(moves)

             

    def tabu_solve(self):
        pass
        

if __name__ == '__main__':
    init_S = (3762, [[(1, 2), (2, 3), (2, 4), (4, 5), (9, 10), (11, 59), (59, 69), (69, 4)], [(69, 58), (58, 60), (60, 62), (62, 66), (66, 68), (62, 63), (63, 65), (60, 61), (58, 59), (59, 44), (44, 46)], [(58, 57), (57, 42), (43, 44), (44, 45), (46, 47), (47, 49), (49, 51), (51, 21), (21, 22), (22, 75), (75, 23)], [(11, 12), (12, 16), (16, 13), (13, 14), (15, 17), (15, 18), (18, 19), (19, 21), (52, 50), (50, 49), (47, 48), (52, 54), (19, 20), (20, 76)], [(56, 55), (41, 35), (35,
32), (32, 33), (32, 34), (32, 31), (31, 23)]])
    parser = argparse.ArgumentParser()
    parser.add_argument('instance_file', help='the absolute path of the test CARP instance file')
    parser.add_argument('-t', dest='termination', help='a positive number which indicates how many seconds the algorithm can spend on this instance.')
    parser.add_argument('-s', dest='random_seed', help='the random seed used in this run.')
    parse_res = parser.parse_args()

    strt_time = time.time()
    dict = read_file(parse_res.instance_file)
    carp = CARP(dict['name'], dict['vertices'], dict['depot'], dict['required_edges'], dict['non_required_edges'], dict['vehicles'], dict['capacity'], dict['total_cost_of_required_edges'], dict['matrix'])
    graph = Graph(carp.vertices, carp.matrix)
    graph.multiple_shortest_path()
    tabuSearch = TabuSearch(init_S, graph)
    tabuSearch.gen_neighbor()

