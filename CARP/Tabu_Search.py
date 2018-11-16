import time
import copy
import heapq
import numpy as np
from Graph import Graph
from collections import defaultdict
from CARP_solver import read_file, CARP, argparse
from multiprocessing import Process, Manager



class TabuSearch:
    def __init__(self, S, N, graph):
        self.S = S
        self.S_B = S
        self.S_BF = S
        self.N = N
        self.graph = graph


    def cal_sol_cost(self, roads):
        cost = 0
        for road in roads:
            r_len = len(road)
            cost += self.graph.adj_matrix[road[0][0]][road[0][1]]
            cost += self.graph.mul_sp[1][road[0][0]]
            cost += self.graph.mul_sp[road[0][1]][road[1][0]]
            for i in range(1, r_len-1):
                cost += self.graph.adj_matrix[road[i][0]][road[i][1]]
                cost += self.graph.mul_sp[road[i][1]][road[i+1][0]]
            cost += self.graph.adj_matrix[road[r_len-1][0]][road[r_len-1][1]]
            cost += self.graph.mul_sp[road[r_len-1][1]][1]
        return cost
                         

    def gen_neighbor_SI(self, not_adj, neighbor_S):
        s_roads = self.S[1]
        best_S = self.S_B
        
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
                            
                            
                            cost = self.cal_sol_cost(s_roads)
                            if cost < best_S[0]:
                                best_S = (cost, copy.deepcopy(s_roads))
                            del s_roads[idx][pos+1]
                    
                        direction_l_cost = self.graph.mul_sp[1][edge[0]] + self.graph.mul_sp[edge[1]][s_roads[idx][0][0]]
                        direction_r_cost = self.graph.mul_sp[1][edge[1]] + self.graph.mul_sp[edge[0]][s_roads[idx][0][0]]
                        if direction_l_cost < direction_r_cost:
                            s_roads[idx].insert(0, edge)
                        else:
                            s_roads[idx].insert(0, (edge[1], edge[0]))
                        cost = self.cal_sol_cost(s_roads)
                        if cost < best_S[0]:
                            best_S = (cost, copy.deepcopy(s_roads))
                        del s_roads[idx][0]


                        r_len = len(s_roads[idx])
                        direction_l_cost = self.graph.mul_sp[s_roads[idx][r_len-1][1]][edge[0]] + self.graph.mul_sp[edge[1]][1]
                        direction_r_cost = self.graph.mul_sp[s_roads[idx][r_len-1][1]][edge[1]] + self.graph.mul_sp[edge[0]][1]
                        if direction_l_cost < direction_r_cost:
                            s_roads[idx].insert(r_len, edge)
                        else:
                            s_roads[idx].insert(r_len, (edge[1], edge[0]))
                        cost = self.cal_sol_cost(s_roads)
                        if cost < best_S[0]:
                            best_S = (cost, copy.deepcopy(s_roads))
                        del s_roads[idx][r_len]

                s_roads[r_idx].insert(i, edge)

        neighbor_S.append(best_S)


         
    
    def gen_neighbor_DI(self, not_adj, neighbor_S):
        s_roads = self.S[1]
        best_S = self.S_B
            
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
                               

                             
                            cost = self.cal_sol_cost(s_roads)
                            if cost < best_S[0]:
                                best_S = (cost, copy.deepcopy(s_roads))


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
                        
                        cost = self.cal_sol_cost(s_roads)
                        if cost < best_S[0]:
                            best_S = (cost, copy.deepcopy(s_roads))
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
                        
                        cost = self.cal_sol_cost(s_roads)
                        if cost < best_S[0]:
                            best_S = (cost, copy.deepcopy(s_roads))
                        del s_roads[idx][r_len]
                        del s_roads[idx][r_len]

                s_roads[r_idx].insert(i, edge_0)
                s_roads[r_idx].insert(i+1, edge_1)

        neighbor_S.append(best_S)
        

    def gen_neighbor_SWAP(self, neighbor_S):
        s_roads = self.S[1]
        best_S = self.S_B
  
        combine = []
        for i in range(len(s_roads)):
            for j in range(i+1, len(s_roads)):
                combine.append((i,j))
        for com in combine:
            i,j = com
            for k in range(len(s_roads[i])):
                for g in range(len(s_roads[j])):
                    x = s_roads[i][k]
                    y = s_roads[j][g]
                    s_roads[i][k] = y
                    s_roads[j][g] = x

                    cost = self.cal_sol_cost(s_roads)
                    if cost < best_S[0]:
                        best_S = (cost, copy.deepcopy(s_roads))

                    s_roads[i][k] = x
                    s_roads[j][g] = y
        neighbor_S.append(best_S)
        

    def gen_neighbor(self):
        s_roads = self.S[1]
        not_adj = defaultdict()
        for r_idx, road in enumerate(s_roads):
            not_adj[r_idx] = []
            for i in range(len(road) - 1):
                if road[i][1] != road[i + 1][0]:
                    not_adj[r_idx].append(i)
        start = time.time()
        procs = []
        with Manager() as manager:
            neighbor_S = manager.list()
            
            SI_proc = Process(target=self.gen_neighbor_SI, args=(not_adj,neighbor_S))
            procs.append(SI_proc)
            SI_proc.start()

            DI_proc = Process(target=self.gen_neighbor_DI, args=(not_adj,neighbor_S))
            procs.append(DI_proc)
            DI_proc.start()

            SWAP_proc = Process(target=self.gen_neighbor_SWAP, args=(neighbor_S,))
            procs.append(SWAP_proc)
            SWAP_proc.start()


            for proc in procs:
                proc.join()    

            print(neighbor_S)
            end = time.time()
            print("***multiprocessing***")
            t = end-start
            print(t)
        neighbor_S = []
        start = time.time()
        self.gen_neighbor_SI(not_adj, neighbor_S)
        self.gen_neighbor_DI(not_adj, neighbor_S)
        self.gen_neighbor_SWAP(neighbor_S)
        end = time.time()
        print("***without multiprocessing***")
        t = end -start
        print(t)

        # print(move.values)

        # self.cal_sol_cost(moves)

    def run(self):
        k = 0
        tabu_list = list()
        tenure = self.N / 2
        F_SI = 1
        F_DI = 5
        F_SWAP = 5
        P = 1
        self.gen_neighbor()
        

        


if __name__ == '__main__':
    init_S = (5456, [[(1, 116), (116, 117), (117, 2), (117, 119), (118, 114), (114, 113), (113, 112), (112, 107), (107, 110), (110, 112)], [(110, 111), (107, 108), (108, 109), (107, 106), (106, 105), (105, 104), (104, 102)], [(87, 86), (86, 85), (85, 84), (84, 82), (82, 80), (80, 79), (79, 78), (78, 77), (77, 46), (46, 43), (43, 37), (37, 36), (36, 38), (38, 39), (39, 40)], [(124, 126), (126, 130), (66, 67), (67, 68), (67, 69), (69, 71), (71, 72), (72, 73), (73, 44), (44, 45), (45, 34)], [(66, 62), (62, 63), (63, 64), (64, 65), (56, 55), (55, 54), (55, 140), (140, 49), (49, 48), (139, 34), (44, 43)], [(95, 96), (96, 97), (97, 98), (139, 33), (33, 11), (11, 8), (8, 6), (6, 5), (8, 9), (13, 12)], [(11, 12), (13, 14), (11, 27), (27, 28), (28, 29), (28, 30), (30, 32), (27, 25), (25, 24), (24, 20), (20, 22)]])
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
    tabuSearch = TabuSearch(init_S, carp.required_edges, graph)
    tabuSearch.gen_neighbor()

