import time
import argparse
import numpy as np
from RandomPS import *
from Graph import *

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

    # parser = argparse.ArgumentParser()
    # parser.add_argument('instance_file', help='the absolute path of the test CARP instance file')
    # parser.add_argument('-t', dest='termination', help='a positive number which indicates how many seconds the algorithm can spend on this instance.')
    # parser.add_argument('-s', dest='random_seed', help='the random seed used in this run.')
    # parse_res = parser.parse_args()

    strt_time = time.time()
    dict = read_file("./CARP_samples/egl-s1-A.dat")
    
    carp = CARP(dict['name'], dict['vertices'], dict['depot'], dict['required_edges'], dict['non_required_edges'], dict['vehicles'], dict['capacity'], dict['total_cost_of_required_edges'], dict['matrix'])
    randomPS = RandomPS(carp)
  
    randomPS.run(500)
    end_time = time.time()
    print("***time cnt***")
    print(str(end_time - strt_time))
    