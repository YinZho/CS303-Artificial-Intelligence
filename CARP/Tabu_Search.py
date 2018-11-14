import time

class TabuSearch:
    def init(self, S):
        self.S = S
        self.S_B = S
        self.S_BF = S

    def gen_neighbor_SI(self):
        moves = []
        s_cost, s_roads = self.S
        for road_idx, road in s_roads:
             

    def tabu_solve(self):

        