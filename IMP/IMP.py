import os
import math
import time
import heapq
import random
import argparse
from collections import defaultdict
from multiprocessing import Pool
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
                edge_weight[v][u] = w
                
    return Graph(vertices, edges, adj_list, adj_list_rev, edge_weight)


def node_selection(R: list, k: int):
    # print(len(R))
    S = set()
    node_edges = dict()
    for i, RR in enumerate(R):
        for v in RR:
            if v in node_edges:
                node_edges[v].add(i)
            else:
                node_edges[v] = {i}
    
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
            # print("node selet: ", val[1], -val[0])
            i += 1
            covered_set = covered_set.union(node_edges[val[1]])
            
    return [len(covered_set) / len(R), S]



def sampling_IC(cnt):
    R = list()
    for _ in range(cnt):
        rand_v = random.randint(1, n)
        isActived = {rand_v}
        activity_set = {rand_v}
    
        while activity_set:
            new_activity_set = set()
            for seed in activity_set:
                for u in graph.adj_list_rev[seed]:
                    if u not in isActived and random.uniform(0.0, 1.0) < graph.edge_weight[u][seed]:
                        isActived.add(u)
                        new_activity_set.add(u)
            activity_set = new_activity_set          
        R.append(isActived)
    return R

def sampling_LT(cnt): 
    R = list()
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

def log_binomial(n, k):
    fraction = 0
    for i in range(k + 1, n + 1):
        fraction += math.log(i)
    for i in range(1, n - k + 1):
        fraction -= math.log(i)
    # print(fraction)
    return fraction

def sampling(graph: Graph, k: int, epsilon, l, mode):
    R = list()
    LB = 1
    n = graph.vertices
    epsilon_prime = math.sqrt(2) * epsilon
    f = math.factorial
    log_nk = math.log(f(n)//f(k)//f(n-k))
    lambda_prime = ((2 + 2 * epsilon_prime / 3) * (
            log_nk + l * math.log(n) + math.log(math.log2(n))) * n) / pow(epsilon_prime, 2)
    alpha = math.sqrt(l*math.log(n) + math.log(2))
    beta = math.sqrt((1 - 1 / math.e)*(log_nk + l* math.log(n) + math.log(2)))
    lambda_star = 2 * n * math.pow(((1 - 1/math.e) * alpha + beta), 2) * math.pow(epsilon, -2)

    for i in range(1, int(math.log2(n-1)) + 1):
        x = n / math.pow(2, i)
        theta = lambda_prime / x
        # print(x, lambda_prime)
        # print("theta: " + str(theta))
        curtime = time.time()
        if mode == 'IC':
            res = sampling_IC(math.ceil(theta-len(R)))
        elif mode == 'LT':
            res = sampling_LT(math.ceil(theta-len(R)))
        R += res
        if i == 1:
            for r in R:
                print(r)

        # print("sampling phase time: " + str(time.time() - curtime))

        # start = time.time()
        FR = node_selection(R, k)[0]
        # print(FR)

        # print('selection time:', time.time()-start)
    
        if n * FR >= (1 + epsilon_prime) * x:
            LB = n * FR / (1 + epsilon_prime)
            break

    theta = lambda_star / LB

    if mode == 'IC':
        res = sampling_IC(math.ceil(theta-len(R)))
    elif mode == 'LT':
        res = sampling_LT(math.ceil(theta-len(R)))
    R += res
    return R
        

def IMM(graph: Graph, k: int, epsilon, l, mode):
    n = graph.vertices
    l = l * (1 + math.log(2) / math.log(n))
    R = sampling(graph, k, epsilon, l, mode)
    S = node_selection(R, k)[1]
    return S
    
# def ISE(S, model):
#     print('''==================ISE TEST=================''')
#     with open('IMP2018/seeds_out.txt', 'w') as fp:
#         for s in S:
#             fp.write('{s}\n'.format(s=s))
#     if model == 'IC':
#         os.system('python3 ISE.py -i IMP2018/NetHEPT1.txt -s IMP2018/seeds_out.txt -m IC -t 60')
#     elif model == 'LT':
#         os.system('python3 ISE.py -i IMP2018/NetHEPT1.txt -s IMP2018/seeds_out.txt -m LT -t 60')


if __name__ == "__main__":
    random.seed(1)
    curtime = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='social_network' ,help='the absolute path of the social network file')
    parser.add_argument('-k', dest='seed_size', help='predefined size of the seed set')
    parser.add_argument('-m', dest='diffusion_model', help='only be IC or LT')
    parser.add_argument('-t', dest='time_budget', help='the seconds that my algorithm can spend on this instance')
    parse_res = parser.parse_args()

    global graph
    graph = read_social_network_graph(parse_res.social_network)

    global n
    n = graph.vertices

    k = int(parse_res.seed_size)
    epsilon = 0.1
    l = 1
    model = parse_res.diffusion_model
    S = IMM(graph, k, epsilon, l, model)

    # for s in S:
    #     print(s)
    
    # print("elapsed time: ", time.time() - curtime)
    # ISE(S, model)




    
    
