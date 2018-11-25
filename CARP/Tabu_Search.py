import time
import copy
import math
import heapq
import random
import logging
import numpy as np
from Graph import Graph
from collections import defaultdict
from multiprocessing import Process, Manager, Pool



class TabuSearch:
    def __init__(self, S, N, Q, graph, V):
        self.S = copy.deepcopy(S)
        
        self.S_BF = copy.deepcopy(S)
        self.N = N
        self.Q = Q
        self.P = 1
        self.graph = graph
        self.V = V
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
        return [cost, self.P * w]

    def cal_road_cost(self,road):
        cost = 0
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
        s_roads = copy.deepcopy(self.S[1])
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
                    
                        cost, penalty = self.cal_obj_func([0, s_roads])
                        value = cost + penalty
                        if not self.is_in_tabu_list(cost):
                            if value < best_S[0]:
                                # print(str(edge) + "--- insert in ---" + str((j, g)) +  " --- " + str(value) + "   " + str(self.is_in_tabu_list(value)))
                                best_S = [value, copy.deepcopy(s_roads)]
                            if self.is_feasible([0,s_roads]) and cost < self.S_BF[0]:        
                                self.S_BF = [cost, copy.deepcopy(s_roads)]

                        del s_roads[j][g]
                else:
                    s_roads[j].insert(0, edge)
                    cost, penalty = self.cal_obj_func([0, s_roads])
                    value = cost + penalty
                    if not self.is_in_tabu_list(cost):
                        if value < best_S[0]:
                            best_S = [value, copy.deepcopy(s_roads)]
                            # print(str(edge) + "--- insert in ---" + str((j, g)) + " --- " + str(value))
                        if self.is_feasible([0,s_roads]) and cost < self.S_BF[0]:
                            # self.change_BF(value, "SI")
                            self.S_BF = [cost, copy.deepcopy(s_roads)]
                    del s_roads[j][0]
                s_roads[i].insert(k, edge)
        return best_S

    
    
    def gen_neighbor_DI(self):
        best_S = [math.inf]
        s_roads = copy.deepcopy(self.S[1])
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
                    
                        cost, penalty = self.cal_obj_func([0, s_roads])
                        value = cost + penalty
                        if not self.is_in_tabu_list(cost):                   
                            if value < best_S[0]:                       
                                # print("DI    " + str(value))
                                # print(str(edge_0) + " " + str(edge_1) + "--- insert in ---" + str((j, g)))
                                best_S = [value, copy.deepcopy(s_roads)]
                            if self.is_feasible([0,s_roads]) and cost < self.S_BF[0]:
                                # self.change_BF(value, "DI")
                                self.S_BF = [cost, copy.deepcopy(s_roads)]

                        del s_roads[j][g]
                        del s_roads[j][g]
                else:
                    s_roads[j].insert(0, edge_0)
                    s_roads[j].insert(1, edge_1)
                    cost, penalty = self.cal_obj_func([0, s_roads])
                    value = cost + penalty
                    if not self.is_in_tabu_list(cost):    
                        if value < best_S[0]:                       
                            # print("DI    " + str(value))
                            # print(str(edge_0) + " " + str(edge_1) + "--- insert in ---" + str((j, g)))
                            best_S = [value, copy.deepcopy(s_roads)]
                        if self.is_feasible([0,s_roads]) and cost < self.S_BF[0]:
                            # self.change_BF(value, "DI")
                            self.S_BF = [cost, copy.deepcopy(s_roads)]

                    del s_roads[j][0]
                    del s_roads[j][0]

                s_roads[i].insert(k, edge_0)
                s_roads[i].insert(k+1, edge_1)

        return best_S



    def gen_neighbor_SW(self):
        best_S = [math.inf]
        s_roads = copy.deepcopy(self.S[1])
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
                    cost, penalty = self.cal_obj_func([0, s_roads])
                    value = cost + penalty
                    if not self.is_in_tabu_list(cost):
                        if value < best_S[0]:                            
                            # print("SWAP  " + str(value))
                            # print(str((i, k)) + " swap with " + str((i,g)))
                            best_S = [value, copy.deepcopy(s_roads)]
                        if self.is_feasible([0,s_roads]) and cost < self.S_BF[0]:
                            # self.change_BF(value, "SW")
                            self.S_BF = [cost, copy.deepcopy(s_roads)]

                    s_roads[i][k] = x
                    s_roads[j][g] = y
    
        return best_S


    def gen_neighbor_MS(self):
        best_S = [math.inf]
        s_roads = copy.deepcopy(self.S[1])
        road_cost = [0 for i in range(len(s_roads))]
        for r in range(len(s_roads)):
            road_cost[r] = self.cal_road_cost(s_roads[r])
        s_cost = sum(road_cost)

        combine = []
        for x in range(len(s_roads)):
            for y in range(x+1, len(s_roads)):
                combine.append([x,y])
        for com in combine:
            e_0,e_1 = com
            # print(str(e_0) + "  merge with  " +str(e_1))
            k = 0
            road = list()
            load = list()
            cost = list()
            free = copy.deepcopy(s_roads[e_0]) + copy.deepcopy(s_roads[e_1])
            free_1 = copy.deepcopy(free)
            for i in free_1:
                free.append((i[1], i[0]))
            del free_1
            while free:
                road.append(list())
                load.append(0)
                cost.append(0)
                i = 1
                while True:
                    d_min = math.inf
                    for u in free:
                        d = self.graph.mul_sp[i][u[0]] 
                        if d < d_min:
                            d_min = d
                            u_slt = u
                        elif d == d_min:
                            choice = random.randint(0,1)
                            if choice == 1:
                                u_slt = u
                    
                    if not free or d_min == math.inf:
                        break
        
                    if load[k] + self.graph.edge_demand[u_slt[0]][u_slt[1]] > self.Q:
                        break
                    
                    road[k].append(u_slt)
                    free.remove(u_slt)
                    free.remove((u_slt[1], u_slt[0]))
                    u_slt_dmnd = self.graph.edge_demand[u_slt[0]][u_slt[1]]
                    u_slt_cost = self.graph.adj_matrix[u_slt[0]][u_slt[1]]
                    load[k] = load[k] + u_slt_dmnd
                    cost[k] = cost[k] + d_min + u_slt_cost
                    i = u_slt[1]
                    
                rtn_cost = self.graph.mul_sp[i][1]
                cost[k] = cost[k] + rtn_cost
                k = k + 1

            cost_of_two = sum(cost)
            v = s_cost + cost_of_two - (road_cost[e_0] + road_cost[e_1])
            if  v < best_S[0] and not self.is_in_tabu_list(v) and len(road) <= 2:
                tmp = copy.deepcopy(self.S[1]) 
                if e_0 < e_1:
                    del tmp[e_0]
                    del tmp[e_1-1]
                else:
                    del tmp[e_1]
                    del tmp[e_0-1]
                for r in road:
                    tmp.append(r)
                best_S = [v, tmp]
                if v < self.S_BF[0]:
                    if self.is_feasible(best_S):
                        self.S_BF = copy.deepcopy(best_S)
             

        return best_S


    def gen_neighbor(self, k):
        # curtime = time.time()
        best_S = [math.inf for i in range(4)]
        
        best_S[0] = self.gen_neighbor_SI()
        best_S[1] = self.gen_neighbor_DI()
        best_S[2] = self.gen_neighbor_SW()
        best_S[3] = self.gen_neighbor_MS()
    
        # print("Without multiple threading time:" + str(time.time() - curtime))
        idx = best_S.index(min(best_S))   
        best_Val = min(best_S) 
        m = {0:'SI', 1:'DI', 2:'SW', 3:"MS"}
        # print(best_Val)
        # if self.is_feasible(best_Val):
        #     print(str(k) + "   " + str(best_Val[0]) + "  ------  " + str(self.S_BF[0])+ "   " + str(self.P)+ "   " + m[idx])
        # else:
        #     print(str(k) + "   " + "False   " + str(best_Val[0]) + "   " + str(self.S_BF[0]) + "   " + str(self.P) + "   " + m[idx])
        
        
        return best_Val




    def run(self, t):
        # print("min: " + str(self.S_BF[0]))
        curtime = time.time()
        k = 0
        tenure = self.N
        k_F = 0
        k_I = 0
        while True:
            s = self.gen_neighbor(k)  
            self.S = s
            if len(self.tabu_list) > 0:
                for i, e in enumerate(self.tabu_list):
                    if e[0] + tenure < k:
                        del self.tabu_list[i]

            s_cost = self.cal_sol_cost(s)
            if len(self.tabu_list) >= self.N:
                tmp = max(self.tabu_list, key=lambda x:x[1])
                if tmp[1] >= s[0]:
                    self.tabu_list.remove(tmp)
                    heapq.heappush(self.tabu_list, [k, s_cost]) 
            else:
                heapq.heappush(self.tabu_list, [k, s_cost])

            k += 1

            if self.is_feasible(s):
                k_F += 1
            else:
                k_I += 1
            
            if k_F == 5:
                self.P = self.P / 2
            elif k_I == 5:
                self.P = 2 * self.P
                if self.P >= 64:
                    self.S = copy.deepcopy(self.S_BF)
                    self.P = 2
           
            if k_F == 5 or k_I == 5:
                self.S[0] = sum(self.cal_obj_func(self.S))
                k_F = 0
                k_I = 0
    
<<<<<<< HEAD
            if time.time() - curtime > t - 1:
=======
            if time.time() - curtime > t - 5:
>>>>>>> 045905b72dba6cc48d3a070ce2c4cbefc4249215
                break
        return self.S_BF
    
