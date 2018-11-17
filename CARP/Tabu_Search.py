import time
import copy
import math
import heapq
import logging
import numpy as np
from Graph import Graph
from collections import defaultdict
from multiprocessing import Process, Manager



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
            w += w_tmp
        return cost + self.P * w

    def cal_sol_cost(self, S):
        roads = S[1]
        cost = 0

        for road in roads:
            r_len = len(road) 
            if r_len >= 2:           
                cost += self.graph.adj_matrix[road[0][0]][road[0][1]]
                cost += self.graph.mul_sp[1][road[0][0]]
                cost += self.graph.mul_sp[road[0][1]][road[1][0]]
                for i in range(1, r_len-1):
                    cost += self.graph.adj_matrix[road[i][0]][road[i][1]]
                    cost += self.graph.mul_sp[road[i][1]][road[i+1][0]]
                cost += self.graph.adj_matrix[road[r_len-1][0]][road[r_len-1][1]]
                cost += self.graph.mul_sp[road[r_len-1][1]][1]
            elif r_len == 1:
                cost += self.graph.adj_matrix[road[0][0]][road[0][1]]
                cost += self.graph.mul_sp[1][road[0][0]]
                cost += self.graph.mul_sp[road[0][1]][1]
        return cost

    def is_in_tabu_list(self, c):
        
        for e in self.tabu_list:      
            if c == e[1]:
                return True
        return False
        
    def gen_neighbor_SI(self):
        best_S = [math.inf]
        s_roads = self.S[1]
        combine = []
        for i in range(len(s_roads)):
            for j in range(i, len(s_roads)):
                combine.append([i,j])
        for com in combine:
            i,j = com
            for k in range(len(s_roads[i])):
                edge = s_roads[i][k]
                del s_roads[i][k]
                r_len = len(s_roads[j])
                if r_len >= 1:
                    for g in range(r_len+1):
                        if g == 0:
                            direct_0 = self.graph.mul_sp[edge[1]][s_roads[j][g][0]]
                            direct_1 = self.graph.mul_sp[edge[0]][s_roads[j][g][0]]
                        elif g == r_len:
                            direct_0 = self.graph.mul_sp[s_roads[j][g-1][1]][edge[0]]
                            direct_1 = self.graph.mul_sp[s_roads[j][g-1][1]][edge[1]]
                        else:
                            direct_0 = self.graph.mul_sp[s_roads[j][g-1][1]][edge[0]] + self.graph.mul_sp[edge[1]][s_roads[j][g][0]]
                            direct_1 = self.graph.mul_sp[s_roads[j][g-1][1]][edge[1]] + self.graph.mul_sp[edge[0]][s_roads[j][g][0]]
                        if direct_0 <= direct_1:
                            s_roads[j].insert(g, edge)
                        else:
                            s_roads[j].insert(g, (edge[1], edge[0]))
                    
                        value = self.cal_obj_func([0, s_roads])
                        if not self.is_in_tabu_list(value):
                            if value < best_S[0]:
                                # print(str(edge) + "--- insert in ---" + str((j, g)) +  " --- " + str(value) + "   " + str(self.is_in_tabu_list(value)))
                                best_S = [value, copy.deepcopy(s_roads)]
                            if self.is_feasible([0,s_roads]) and value < self.S_BF[0]:        
                                self.S_BF = [value, copy.deepcopy(s_roads)]

                        del s_roads[j][g]
                else:
                    s_roads[j].insert(0, edge)
                    value = self.cal_obj_func([0, s_roads])
                    if not self.is_in_tabu_list(value):
                        if value < best_S[0]:
                            best_S = [value, copy.deepcopy(s_roads)]
                            # print(str(edge) + "--- insert in ---" + str((j, g)) + " --- " + str(value))
                        if self.is_feasible([0,s_roads]) and value < self.S_BF[0]:
                            # self.change_BF(value, "SI")
                            self.S_BF = [value, copy.deepcopy(s_roads)]
                    del s_roads[j][0]
                s_roads[i].insert(k, edge)
        return best_S

    
    
    def gen_neighbor_DI(self):
        best_S = [math.inf]
        s_roads = self.S[1]
        combine = []
        for i in range(len(s_roads)):
            for j in range(i, len(s_roads)):
                combine.append([i,j])
        for com in combine:
            i,j = com
            for k in range(len(s_roads[i])-1):
                edge_0 = s_roads[i][k]
                edge_1 = s_roads[i][k+1]
                del s_roads[i][k]
                del s_roads[i][k]
                r_len = len(s_roads[j])
                
                if r_len >= 1:    
                    for g in range(r_len+1):
                        if g == 0:
                            direct_0 = self.graph.mul_sp[edge_1[1]][s_roads[j][g][0]]
                            direct_1 = self.graph.mul_sp[edge_0[0]][s_roads[j][g][0]]
                        elif g == r_len:
                            direct_0 = self.graph.mul_sp[s_roads[j][g-1][1]][edge_0[0]]
                            direct_1 = self.graph.mul_sp[s_roads[j][g-1][1]][edge_1[1]]
                        else:
                            direct_0 = self.graph.mul_sp[s_roads[j][g-1][1]][edge_0[0]] + self.graph.mul_sp[edge_1[1]][s_roads[j][g][0]]
                            direct_1 = self.graph.mul_sp[s_roads[j][g-1][1]][edge_1[1]] + self.graph.mul_sp[edge_1[0]][s_roads[j][g][0]]
                    
                        if direct_0 <= direct_1:
                            s_roads[j].insert(g, edge_0)
                            s_roads[j].insert(g+1, edge_1)
                        else:
                            s_roads[j].insert(g, (edge_1[1], edge_1[0]))
                            s_roads[j].insert(g+1, (edge_0[1], edge_0[0]))
                    
                        value = self.cal_obj_func([0, s_roads])
                        if not self.is_in_tabu_list(value):                   
                            if value < best_S[0]:                       
                                # print("DI    " + str(value))
                                # print(str(edge_0) + " " + str(edge_1) + "--- insert in ---" + str((j, g)))
                                best_S = [value, copy.deepcopy(s_roads)]
                            if self.is_feasible([0,s_roads]) and value < self.S_BF[0]:
                                # self.change_BF(value, "DI")
                                self.S_BF = [value, copy.deepcopy(s_roads)]

                        del s_roads[j][g]
                        del s_roads[j][g]
                else:
                    s_roads[j].insert(0, edge_0)
                    s_roads[j].insert(1, edge_1)
                    value = self.cal_obj_func([0, s_roads])
                    if not self.is_in_tabu_list(value):    
                        if value < best_S[0]:                       
                            # print("DI    " + str(value))
                            # print(str(edge_0) + " " + str(edge_1) + "--- insert in ---" + str((j, g)))
                            best_S = [value, copy.deepcopy(s_roads)]
                        if self.is_feasible([0,s_roads]) and value < self.S_BF[0]:
                            # self.change_BF(value, "DI")
                            self.S_BF = [value, copy.deepcopy(s_roads)]

                    del s_roads[j][0]
                    del s_roads[j][0]

                s_roads[i].insert(k, edge_0)
                s_roads[i].insert(k+1, edge_1)
        return best_S



    def gen_neighbor_SWAP(self):
        best_S = [math.inf]
        s_roads = self.S[1]
        combine = []
        for i in range(len(s_roads)):
            for j in range(i, len(s_roads)):
                combine.append([i,j])
        for com in combine:
            i,j = com
            for k in range(len(s_roads[i])):
                for g in range(len(s_roads[j])):
                    x = s_roads[i][k]
                    y = s_roads[j][g]
                    s_roads[i][k] = y
                    s_roads[j][g] = x
                    value = self.cal_obj_func([0, s_roads])
                    if not self.is_in_tabu_list(value):
                        if value < best_S[0]:                            
                            # print("SWAP  " + str(value))
                            # print(str((i, k)) + " swap with " + str((i,g)))
                            best_S = [value, copy.deepcopy(s_roads)]
                        if self.is_feasible([0,s_roads]) and value < self.S_BF[0]:
                            # self.change_BF(value, "SW")
                            self.S_BF = [value, copy.deepcopy(s_roads)]

                    s_roads[i][k] = x
                    s_roads[j][g] = y

        return best_S
        

    def gen_neighbor(self, k, F_SI, F_DI, F_SWAP):

        procs = []
        best_S = [[math.inf] for i in range(3)]
        # with Manager() as manager:
            # if k % F_SI == 0:
            #     best_S = manager.list([None for i in range(3)])
            #     SI_proc = Process(target=self.gen_neighbor_SI, args=(best_S[0],))
            #     procs.append(SI_proc)
            #     SI_proc.start()

            # if k % F_DI == 0:
            #     DI_proc = Process(target=self.gen_neighbor_DI, args=(best_S[1],))
            #     procs.append(DI_proc)
            #     DI_proc.start()

            # if k % F_SWAP == 0:
            #     # self.write.info_to_file("Swap...")
            #     SWAP_proc = Process(target=self.gen_neighbor_SWAP, args=(best_S[2],))
            #     procs.append(SWAP_proc)
            #     SWAP_proc.start()


            # for proc in procs:
            #     proc.join()  
        # best_S[0] = self.gen_neighbor_SI()
        # best_S[1] = self.gen_neighbor_DI()
     
        if k % F_SI == 0:
            # print("SI")
            best_S[0] = self.gen_neighbor_SI()
        if k % F_DI == 0:
            # print("DI")
            best_S[1] = self.gen_neighbor_DI()
        if k % F_SWAP == 0:
            # print("SWAP")
            best_S[2] = self.gen_neighbor_SWAP()
        # print(best_S)
        idx = best_S.index(min(best_S))   
        best_Val = min(best_S) 
        m = {0:'SI', 1:'DI', 2:'SWAP'}
        # if self.is_feasible(best_Val):
        #     print(str(k) + "   " + str(best_Val[0]) + "  ------  " + str(self.S_BF[0])+ "   " + str(self.P)+ "   " + m[idx])
        # else:
        #     print(str(k) + "   " + "False   " + str(best_Val[0]) + "   " + str(self.S_BF[0]) + "   " + str(self.P) + "   " + m[idx])
        
        return best_Val


    def run(self, t):
        # print("min: " + str(self.S_B[0]))
        start = time.time()
        k = 0
        tenure = self.N // 2
        F_SI = 1
        F_DI = 1
        F_SWAP = 1
        k_F = 0
        k_I = 0
        k_B = 0 
        k_L = 8 * self.N
        k_BF = 0
        k_BT = 0
        while True:
            s = self.gen_neighbor(k, F_SI, F_DI, F_SWAP)  
            self.S = s
            if len(self.tabu_list) > 0:
                for i, e in enumerate(self.tabu_list):
                    if e[0] + tenure < k:
                        del self.tabu_list[i]

            if len(self.tabu_list) >= self.N // 2:
                tmp = max(self.tabu_list, key=lambda x:x[1])
                if tmp[1] >= s[0]:
                    self.tabu_list.remove(tmp)
                    heapq.heappush(self.tabu_list, [k, s[0]]) 
            else:
                heapq.heappush(self.tabu_list, [k, s[0]])

            k += 1

            if self.is_feasible(s):
                k_F += 1
            else:
                k_I += 1

            if self.is_feasible(s) and s[0] < self.S_BF[0]:
                k_B = 0
                k_BT = 0

            if s[0] < self.S_B[0]:
                self.S_B = s
                k_B += 1
                k_BF += 1
                k_BT += 1
            
            if k_F == 10:
                # print("***Penalty Half!***")
                self.P = self.P / 2
            elif k_I == 10:
                # print("***Penalty Double!***")
                self.P = 2 * self.P
                if self.P >= 8:
                    self.S = copy.deepcopy(self.S_BF)
           
            if k_F == 10 or k_I == 10:
                self.S_B[0] = self.cal_obj_func(self.S_B)
                self.S[0] = self.cal_obj_func(self.S)
                k_F = 0
                k_I = 0

            if k_B == k_L // 2:
                F_SI = 1
                F_DI = 1
                F_SWAP = 1
            
            if k_B == k_L:
                self.S = self.S_BF
                k_B = 0
                p = 1
                k_F = 0
                k_I = 0
                F_SI = 1
                F_DI = 1
                F_SWAP = 1
                k_L += 2 * self.N
                self.S_B[1] = self.cal_obj_func(self.S_B)
                self.tabu_list = []
        
            end = time.time()
            # print(str(start) + "    " + str(end))
            if end - start > t - 1:
                break
        return self.S_BF
    
