import time
import copy
import math
import heapq
import logging
import numpy as np
from Graph import Graph
from collections import defaultdict
from CARP_solver import read_file, CARP, argparse
from multiprocessing import Process, Manager
import WriteToFile



class TabuSearch:
    def __init__(self, S, N, Q, graph):
        self.S = S
        self.S_B = S
        self.S_BF = S
        self.N = N
        self.Q = Q
        self.P = 1
        self.graph = graph
        self.tabu_list = list()

    def is_feasible(self, S):
        roads = S[1]
        for road in roads:
            capacity = 0
            for edge in road:
                capacity += self.graph.edge_demand[edge[0]][edge[1]]
            if capacity > self.Q:
                return False
        return True


    def cal_obj_func(self, S):
        cost = self.cal_sol_cost(S)
        roads = S[1]
        w = 0
        for road in roads:
            capacity = 0
            for edge in road:
                capacity += self.graph.edge_demand[edge[0]][edge[1]]
            w_tmp = max(capacity - self.Q, 0)
            w = max(w, w_tmp)
        return cost + self.P * w

    def cal_sol_cost(self, S):
        roads = S[1]
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

    def is_in_tabu_list(self, r):
        r = sorted(r)
        for e in self.tabu_list:
            roads = e[1][1]
            if r == roads:
                return True
        return False
                         

    def gen_neighbor_SI(self, not_adj, neighbor_S):
        s_roads = self.S[1]
        best_S = None
        
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

                            if not self.is_in_tabu_list(s_roads):
                                value = self.cal_obj_func([0, s_roads])
                                if best_S is None:
                                    best_S = [value, copy.deepcopy(s_roads)]
                                else:
                                    if value < best_S[0]:
                                        best_S = [value, copy.deepcopy(s_roads)]

                            del s_roads[idx][pos+1]
                    
                        direction_l_cost = self.graph.mul_sp[1][edge[0]] + self.graph.mul_sp[edge[1]][s_roads[idx][0][0]]
                        direction_r_cost = self.graph.mul_sp[1][edge[1]] + self.graph.mul_sp[edge[0]][s_roads[idx][0][0]]
                        if direction_l_cost < direction_r_cost:
                            s_roads[idx].insert(0, edge)
                        else:
                            s_roads[idx].insert(0, (edge[1], edge[0]))
        
                        if not self.is_in_tabu_list(s_roads):
                            value = self.cal_obj_func([0, s_roads])
                            if value < best_S[0]:
                                best_S = [value, copy.deepcopy(s_roads)]

                        del s_roads[idx][0]


                        r_len = len(s_roads[idx])
                        direction_l_cost = self.graph.mul_sp[s_roads[idx][r_len-1][1]][edge[0]] + self.graph.mul_sp[edge[1]][1]
                        direction_r_cost = self.graph.mul_sp[s_roads[idx][r_len-1][1]][edge[1]] + self.graph.mul_sp[edge[0]][1]
                        if direction_l_cost < direction_r_cost:
                            s_roads[idx].insert(r_len, edge)
                        else:
                            s_roads[idx].insert(r_len, (edge[1], edge[0]))

                        if not self.is_in_tabu_list(s_roads):
                            value = self.cal_obj_func([0, s_roads])
                            if value < best_S[0]:
                                best_S = [value, copy.deepcopy(s_roads)]

                        del s_roads[idx][r_len]

                s_roads[r_idx].insert(i, edge)

        neighbor_S.append(best_S)


         
    
    def gen_neighbor_DI(self, not_adj, neighbor_S):
        s_roads = self.S[1]
        best_S = None
            
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
                               

                             
                            if not self.is_in_tabu_list(s_roads):
                                value = self.cal_obj_func([0, s_roads])
                                if best_S is None:
                                    best_S = [value, copy.deepcopy(s_roads)]
                                else:
                                    if value < best_S[0]:
                                        best_S = [value, copy.deepcopy(s_roads)]


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
                    
                        if not self.is_in_tabu_list(s_roads):
                            value = self.cal_obj_func([0, s_roads])
                            if value < best_S[0]:
                                best_S = [value, copy.deepcopy(s_roads)]

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
                        
                      
                        if not self.is_in_tabu_list(s_roads):
                            value = self.cal_obj_func([0, s_roads])
                            if value < best_S[0]:
                                best_S = [value, copy.deepcopy(s_roads)]


                        del s_roads[idx][r_len]
                        del s_roads[idx][r_len]

                s_roads[r_idx].insert(i, edge_0)
                s_roads[r_idx].insert(i+1, edge_1)

        neighbor_S.append(best_S)
        

    def gen_neighbor_SWAP(self, neighbor_S):
        s_roads = self.S[1]
        best_S = None
  
        combine = []
        for i in range(len(s_roads)):
            for j in range(i+1, len(s_roads)):
                combine.append([i,j])
        for com in combine:
            i,j = com
            for k in range(len(s_roads[i])):
                for g in range(len(s_roads[j])):
                    x = s_roads[i][k]
                    y = s_roads[j][g]
                    s_roads[i][k] = y
                    s_roads[j][g] = x

                    if not self.is_in_tabu_list(s_roads):
                        value = self.cal_obj_func([0, s_roads])
                        if best_S is None:
                            best_S = [value, copy.deepcopy(s_roads)]
                        else:
                            if value < best_S[0]:
                                best_S = [value, copy.deepcopy(s_roads)]

                    s_roads[i][k] = x
                    s_roads[j][g] = y
        neighbor_S.append(best_S)
        

    def gen_neighbor(self, k, F_SI, F_DI, F_SWAP):
        s_roads = self.S[1]
        not_adj = defaultdict()
        for r_idx, road in enumerate(s_roads):
            not_adj[r_idx] = []
            for i in range(len(road) - 1):
                if road[i][1] != road[i + 1][0]:
                    not_adj[r_idx].append(i)

        procs = []
        with Manager() as manager:
            neighbor_S = manager.list()
            if k % F_SI == 0:
 
                SI_proc = Process(target=self.gen_neighbor_SI, args=(not_adj,neighbor_S))
                procs.append(SI_proc)
                SI_proc.start()

            if k % F_DI == 0:

                DI_proc = Process(target=self.gen_neighbor_DI, args=(not_adj,neighbor_S))
                procs.append(DI_proc)
                DI_proc.start()

            if k % F_SWAP == 0:
                # self.write.info_to_file("Swap...")
                SWAP_proc = Process(target=self.gen_neighbor_SWAP, args=(neighbor_S,))
                procs.append(SWAP_proc)
                SWAP_proc.start()


            for proc in procs:
                proc.join()   
            return max(neighbor_S)


    def run(self):
        k = 1
       
        tenure = self.N // 2
        F_SI = 1
        F_DI = 5
        F_SWAP = 5
        k_F = 0
        k_I = 0
        k_B = 0 
        k_L = 8 * self.N
        k_BF = 0
        k_BT = 0
        while True:
            s = self.gen_neighbor(k, F_SI, F_DI, F_SWAP)
            
            if self.is_feasible(s):
                print(str(s[0]) + "  ------  " + str("T"))
            else:
                print(str(s[0]) + "    " + str("F"))

            s[1] = sorted(s[1])

            if len(self.tabu_list) > 0:
                for i, e in enumerate(self.tabu_list):
                    if e[0] + tenure < k:
                        del self.tabu_list[i]

            if len(self.tabu_list) >= self.N // 2:
                tmp = max(self.tabu_list, key=lambda x:x[1])
                if tmp[1][0] >= s[0]:
                    self.tabu_list.remove(tmp)
                    heapq.heappush(self.tabu_list, [k, s]) 
            else:
                heapq.heappush(self.tabu_list, [k, s])


            if self.is_feasible(s):
                k_F += 1
            else:
                k_I += 1

            if self.is_feasible(s) and s[0] < self.S_BF[0]:
                self.S_BF = s
                k_B = 0
                k_BF = 0
                k_BT = 0
            if s[0] < self.S_B[0]:
                self.S_B = s
                k_B = 0
                k_BT = 0
            k += 1
            k_B += 1
            k_BF += 1
            k_BT += 1
            if  k % 10 ==0:
                if k_F == 10:
                    self.P = self.P / 2
                elif k_I == 10:
                    self.P = 2 * self.P
            if k_F == 10 or k_I == 10:
                self.S_B[0] = self.cal_obj_func(self.S_B)
                k_F = 0
                k_I = 0
            
            if k_B == k_L // 2:
                F_SI = 5
                F_DI = 1
                F_SWAP = 10
            
            if k_B == k_L:
                # (1)
                self.s = self.S_BF

                # (2)
                k_B = 0
                
                k_F = 0
                k_I = 0
                F_SI = 1
                F_DI = 5
                F_SWAP = 5
                k_L += 2 * self.N

                # (3) 
                self.S_B[0] = self.cal_obj_func(self.S_B)
                self.tabu_list = []

            # if (k >= 900 * math.sqrt(self.N) and k_BF >= 10 * self.N) or k_BT == 2 * k_L:
            if k >= 1000:
                break

        
        print(self.S_BF)
    




################################################################

    def print_lists(self, l):
        if isinstance(l[0], list):
            for e in l:
                print(str(e))

    def gen_neighbor_test(self):
        s_roads = self.S[1]
        not_adj = defaultdict()
        for r_idx, road in enumerate(s_roads):
            not_adj[r_idx] = []
            for i in range(len(road) - 1):
                if road[i][1] != road[i + 1][0]:
                    not_adj[r_idx].append(i)
        # start = time.time() 
        neighbor_S = []
        self.gen_neighbor_DI_test(not_adj,neighbor_S)


    def gen_neighbor_SI_test(self, not_adj, neighbor_S):
        s_roads = self.S[1]
        best_S = self.S
        
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
                            
                            
                            if not self.is_in_tabu_list(s_roads):
                                value = self.cal_obj_func([0, s_roads])
                                if value < best_S[0]:
                                    print(str(value)+" "+str(best_S[0]))
                                    best_S = [value, copy.deepcopy(s_roads)]

                            del s_roads[idx][pos+1]
                    
                        direction_l_cost = self.graph.mul_sp[1][edge[0]] + self.graph.mul_sp[edge[1]][s_roads[idx][0][0]]
                        direction_r_cost = self.graph.mul_sp[1][edge[1]] + self.graph.mul_sp[edge[0]][s_roads[idx][0][0]]
                        if direction_l_cost < direction_r_cost:
                            s_roads[idx].insert(0, edge)
                        else:
                            s_roads[idx].insert(0, (edge[1], edge[0]))
        
                        if not self.is_in_tabu_list(s_roads):
                            value = self.cal_obj_func([0, s_roads])
                            if value < best_S[0]:
                                print(str(value)+" "+str(best_S[0]))
                                best_S = [value, copy.deepcopy(s_roads)]

                        del s_roads[idx][0]


                        r_len = len(s_roads[idx])
                        direction_l_cost = self.graph.mul_sp[s_roads[idx][r_len-1][1]][edge[0]] + self.graph.mul_sp[edge[1]][1]
                        direction_r_cost = self.graph.mul_sp[s_roads[idx][r_len-1][1]][edge[1]] + self.graph.mul_sp[edge[0]][1]
                        if direction_l_cost < direction_r_cost:
                            s_roads[idx].insert(r_len, edge)
                        else:
                            s_roads[idx].insert(r_len, (edge[1], edge[0]))

                        
                        if not self.is_in_tabu_list(s_roads):
                            value = self.cal_obj_func([0, s_roads])
                            if value < best_S[0]:
                                print(str(value)+" "+str(best_S[0]))
                                best_S = [value, copy.deepcopy(s_roads)]

                        del s_roads[idx][r_len]

                s_roads[r_idx].insert(i, edge)
        print(self.S[0])
        print(best_S[0])
        neighbor_S.append(best_S)


                

    def gen_neighbor_DI_test(self, not_adj, neighbor_S):
        s_roads = self.S[1]
        best_S = self.S
            
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
                               

                             
                            if not self.is_in_tabu_list(s_roads):
                                value = self.cal_obj_func([0, s_roads])
                                print(str(value)+" "+str(best_S[0]))
                                if value < best_S[0]:
                                    
                                    best_S = [value, copy.deepcopy(s_roads)]


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
                    
                        if not self.is_in_tabu_list(s_roads):
                            value = self.cal_obj_func([0, s_roads])
                            if value < best_S[0]:
                                print(str(value)+" "+str(best_S[0]))
                                best_S = [value, copy.deepcopy(s_roads)]

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
                        
                      
                        if not self.is_in_tabu_list(s_roads):
                            value = self.cal_obj_func([0, s_roads])
                            if value < best_S[0]:
                                print(str(value)+" "+str(best_S[0]))
                                best_S = [value, copy.deepcopy(s_roads)]

                        del s_roads[idx][r_len]
                        del s_roads[idx][r_len]

                s_roads[r_idx].insert(i, edge_0)
                s_roads[r_idx].insert(i+1, edge_1)

        neighbor_S.append(best_S)

        


if __name__ == '__main__':
    init_S = [5456, [[(1, 116), (116, 117), (117, 2), (117, 119), (118, 114), (114, 113), (113, 112), (112, 107), (107, 110), (110, 112)], [(110, 111), (107, 108), (108, 109), (107, 106), (106, 105), (105, 104), (104, 102)], [(87, 86), (86, 85), (85, 84), (84, 82), (82, 80), (80, 79), (79, 78), (78, 77), (77, 46), (46, 43), (43, 37), (37, 36), (36, 38), (38, 39), (39, 40)], [(124, 126), (126, 130), (66, 67), (67, 68), (67, 69), (69, 71), (71, 72), (72, 73), (73, 44), (44, 45), (45, 34)], [(66, 62), (62, 63), (63, 64), (64, 65), (56, 55), (55, 54), (55, 140), (140, 49), (49, 48), (139, 34), (44, 43)], [(95, 96), (96, 97), (97, 98), (139, 33), (33, 11), (11, 8), (8, 6), (6, 5), (8, 9), (13, 12)], [(11, 12), (13, 14), (11, 27), (27, 28), (28, 29), (28, 30), (30, 32), (27, 25), (25, 24), (24, 20), (20, 22)]]]
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
    tabuSearch = TabuSearch(init_S, carp.required_edges, carp.capacity, graph)
    tabuSearch.run()
    # tabuSearch.gen_neighbor_test()
    # print(tabuSearch.is_feasible(init_S))
