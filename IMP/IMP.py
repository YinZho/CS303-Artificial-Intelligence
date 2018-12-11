import os
import sys
import math
import time
import heapq
import random
import argparse
import numpy as np
from collections import defaultdict
import multiprocessing as mp
'''
1. Node index starts from 1
2. The first line contains the number of nodes n and number of edges m
3. Each of the next m lines describes an edge following the format: <src> <dest> <weight>
'''


class Graph:
    def __init__(self, vertices, edges, adj_list, adj_list_rev, edge_weight):
        self.vertices = vertices
        self.edges = edges
        self.adj_list = adj_list
        self.adj_list_rev = adj_list_rev
        self.edge_weight = edge_weight

def read_social_network_graph(file_name):
    edge_weight, adj_list, adj_list_rev = [[], [], []]
    vertices, edges = [0, 0]

    with open (file_name, 'r') as fp:
        for i, line in enumerate(fp):

            line = line.split(' ')
            for e in range(len(line)):
                if e == 2:
                    line[e] = float(line[e])
                else:
                    line[e] = int(line[e])
            
            if i == 0:
                vertices, edges = line
                adj_list = [list() for i in range(vertices+1)]
                adj_list_rev = [list() for i in range(vertices+1)]
                edge_weight = [defaultdict() for i in range(vertices+1)]
            elif 0 < i <= edges:
                u,v,w = line
                adj_list[u].append(v)
                adj_list_rev[v].append(u)
                edge_weight[u][v] = w
                
    return Graph(vertices, edges, adj_list, adj_list_rev, edge_weight)

def cnt_nodes(R: list):
    node_edges = dict()
    for i, RR in enumerate(R):
        for v in RR:
            if v in node_edges:
                node_edges[v].add(i)
            else:
                node_edges[v] = {i}
    return node_edges

def node_selection(R: list, k: int):
    S = set()
    node_edges = cnt_nodes(R)
    max_heap = list()
    for key, value in node_edges.items():
        max_heap.append([-len(value), key, 0])

    heapq.heapify(max_heap)
    covered_set = set()
    i = 0
    while i < k:
        val = heapq.heappop(max_heap)
        if val[2] != i:
            node_edges[val[1]] -= covered_set
            val[0] = - len(node_edges[val[1]])
            val[2] = i
            heapq.heappush(max_heap, val)
            
        else:
            S.add(val[1])
            i += 1
            covered_set |= node_edges[val[1]]
            
    return [len(covered_set) / len(R), S]



def get_rr_IC(cnt, graph):
    R = list()
    n = graph.vertices
    for _ in range(cnt):
        rand_v = random.randint(1, n)
        isActived = {rand_v}
        activity_set = {rand_v}
        while len(activity_set) > 0:
            new_activity_set = set()
            for seed in activity_set:
                for u in graph.adj_list_rev[seed]:
                    if u not in isActived and random.uniform(0, 1) <= graph.edge_weight[u][seed]:
                        isActived.add(u)
                        new_activity_set.add(u)
                activity_set = new_activity_set
        R.append(isActived)
    return R

def get_rr_LT(cnt, graph): 
    R = list()
    n = graph.vertices
    for _ in range(cnt):         
        rand_v = random.randint(1, n)
        curnode = rand_v
        isActived = {rand_v}
        while True:
            size = len(graph.adj_list_rev[curnode])
            if size == 0:
                break
            op = random.randrange(0, size)
            if graph.adj_list_rev[curnode][op] in isActived:
                break
            isActived.add(graph.adj_list_rev[curnode][op])
            curnode = graph.adj_list_rev[curnode][op]
        R.append(isActived)
    return R


def sampling(graph: Graph, k: int, epsilon, l, mode):
    R = list()
    LB = 1
    n = graph.vertices
    epsilon_prime = math.sqrt(2) * epsilon
    f = math.factorial
    lambda_prime = (2 + (2 / 3) * epsilon_prime) * (math.log(f(n) // f(k) // f(n-k)) + l * math.log(n) + math.log(math.log(n, 2))) * n / math.pow(epsilon_prime, 2)
    alpha = math.sqrt(l*math.log(n) + math.log(2))
    beta = math.sqrt((1 - 1 / math.e)*(math.log(f(n) // f(k) // f(n-k)) + l* math.log(n) + math.log(2)))
    lambda_star = 2 * n * math.pow(((1 - 1/math.e) * alpha + beta), 2) * math.pow(epsilon, -2)

    for i in range(1, int(math.log(n, 2))):
        x = n / math.pow(2, i)
        theta = lambda_prime / x

        start = time.time()
        for i in range(worker_cnt):
            worker[i].inQ.put(math.ceil((theta-len(R))/worker_cnt))
        for i in range(worker_cnt):
            R += worker[i].outQ.get()
        start = time.time()
        FR = node_selection(R, k)[0]
        if n * FR >= (1 + epsilon_prime) * x:
            LB = n * FR / (1 + epsilon_prime)
            break

    theta = lambda_star / LB

    for i in range(worker_cnt):
        worker[i].inQ.put(math.ceil((theta-len(R))/worker_cnt))
    for i in range(worker_cnt):
        R += worker[i].outQ.get()

    return R
        

def IMM(graph: Graph, k: int, epsilon, l, mode):
    n = graph.vertices
    l = l * (1 + math.log(2) / math.log(n))
    R = sampling(graph, k, epsilon, l, mode)
    S = node_selection(R, k)[1]
    return S
    
# def ISE(S, model, fn):
#     print('''==================ISE TEST=================''')
#     fw = 'IMP2018/seeds_out.txt'
#     with open(fw, 'w') as fp:
#         for s in S:
#             fp.write('{s}\n'.format(s=s))
#     if model == 'IC':
#         os.system('python ISE.py -i {} -s {} -m IC -t 60'.format(fn, fw))
#     elif model == 'LT':
#         os.system('python ISE.py -i {} -s {} -m LT -t 60'.format(fn, fw))

'''=============================================='''
class Worker(mp.Process):
    def __init__ (self, inQ, outQ, mode, graph):
        super(Worker, self).__init__(target=self.start)
        self.inQ = inQ
        self.outQ = outQ
        self.mode = mode
        self.graph = graph
        np.random.seed(random.randrange(1, 100))

    def run (self):
        while True:
            task = self.inQ.get()
            cnt = task     # 解析任务
            if self.mode == 'IC':
                res = get_rr_IC(cnt, self.graph)   # 执行任务
            else:
                res = get_rr_LT(cnt, self.graph)
            self.outQ.put(res)  # 返回结果

def create_worker (num, mode):
    for i in range(num):
        worker.append(Worker(mp.Queue(), mp.Queue(), mode, graph))
        worker[i].start()

def finish_worker ():
    for w in worker:
        w.terminate()

'''=============================================='''


if __name__ == "__main__":
    curtime = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='social_network' ,help='the absolute path of the social network file')
    parser.add_argument('-k', dest='seed_size', help='predefined size of the seed set')
    parser.add_argument('-m', dest='diffusion_model', help='only be IC or LT')
    parser.add_argument('-t', dest='time_budget', help='the seconds that my algorithm can spend on this instance')
    parse_res = parser.parse_args()

    graph = read_social_network_graph(parse_res.social_network)

    global worker_cnt
    worker_cnt = 8
        
    global worker
    worker = []
    create_worker(worker_cnt, parse_res.diffusion_model)
    k = int(parse_res.seed_size)
    epsilon = 0.1

    if graph.edges > 80000 and parse_res.time_budget <= 60:
        epsilon = 0.2
        if parse_res.time_budget <= 30:
            epsilon = 0.5
    

    l = 1
    model = parse_res.diffusion_model
    S = IMM(graph, k, epsilon, l, model)

    for s in S:
        print(s)
    # ISE(S, parse_res.diffusion_model, parse_res.social_network)
    finish_worker()
    sys.stdout.flush()
    os._exit(0)



    
