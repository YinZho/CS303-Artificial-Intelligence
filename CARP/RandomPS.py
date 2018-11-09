import math
import numpy as np

class RandomPS:
    def __init__(self, carp):
        self.carp = carp

    def construct_free(self):
        free = list()
        for i in range(self.carp.graph.vertices + 1):
            for j in range(i + 1, self.carp.graph.vertices + 1):
                if self.carp.graph.edge_demand[i][j] > 0:
                    free.append((i, j))
                    free.append((j, i))
        return free

    # criteria 1 : minimization ratio cost(i, j)/rmn_dmnd(i, j) once (i, j) is treated; 
    def criteria_1(self, u, u_slt):
        u_cost = self.carp.graph.adj_matrix[u[0]][u[1]]
        u_dmnd = self.carp.graph.edge_demand[u[0]][u[1]]
        u_slt_cost = self.carp.graph.adj_matrix[u_slt[0]][u_slt[1]]
        u_slt_dmnd = self.carp.graph.edge_demand[u_slt[0]][u_slt[1]]
        
        return u_cost / u_dmnd < u_slt_cost / u_slt_dmnd

    # criteria 2 : maximization ratio cost(i, j)/rmn_dmnd(i, j); 
    def criteria_2(self, u, u_slt):
        u_cost = self.carp.graph.adj_matrix[u[0]][u[1]]
        u_dmnd = self.carp.graph.edge_demand[u[0]][u[1]]
        u_slt_cost = self.carp.graph.adj_matrix[u_slt[0]][u_slt[1]]
        u_slt_dmnd = self.carp.graph.edge_demand[u_slt[0]][u_slt[1]]
        
        return u_cost / u_dmnd > u_slt_cost / u_slt_dmnd

    # criteria 3 : maximize cost(j, depot)
    def criteria_3(self, u, u_slt):
        u_end_depot = self.carp.graph.mul_sp[u[1]][self.carp.depot]
        u_slt_end_depot = self.carp.graph.mul_sp[u_slt[1]][self.carp.depot] 

        return u_end_depot > u_slt_end_depot

    # criteria 4 : minimize cost(j, depot)
    def criteria_4(self, u, u_slt):
        u_end_depot = self.carp.graph.mul_sp[u[1]][self.carp.depot]
        u_slt_end_depot = self.carp.graph.mul_sp[u_slt[1]][self.carp.depot] 

        return u_end_depot < u_slt_end_depot
        
    # if vehicls is less than half-full than criteria 3
        # else criteria 4
    def criteria_5(self, u, u_slt, k):
        if k + 1 < self.carp.vehicles:
            return self.criteria_3(u, u_slt)
        else:
            return self.criteria_4(u, u_slt)


    
    def better(self, u, u_slt, k):
        choice = np.random.choice([i for i in range(1, 6)], size=1, p=[0.2, 0.2, 0.2, 0.2, 0.2])

        if choice == 1:
            return self.criteria_1(u, u_slt)
        elif choice == 2:
            return self.criteria_2(u, u_slt)
        elif choice == 3:
            return self.criteria_3(u, u_slt)
        elif choice == 4:
            return self.criteria_4(u, u_slt)
        else:
            return self.criteria_5(u, u_slt, k)

    
    def path_scanning(self):

        k = 0
        capacity = self.carp.capacity

        free = self.construct_free()
        road = list()
        load = list()
        cost = list()

        while free:
            road.append(list())
            load.append(0)
            cost.append(0)
            i = 1
            while True:
                d_min = math.inf
                u_slt = ()

                for u in free:
                    d = self.carp.graph.mul_sp[i][u[0]] 
                    if d < d_min:
                        d_min = d
                        u_slt = u
                    elif d == d_min and self.better(u, u_slt, k):
                        u_slt = u
                   
                if not free or d_min == math.inf:
                    break
                if load[k] + self.carp.graph.edge_demand[u_slt[0]][u_slt[1]] > capacity:
                    break
                road[k].append(u_slt)
                free.remove(u_slt)
                free.remove((u_slt[1], u_slt[0]))
                u_slt_dmnd = self.carp.graph.edge_demand[u_slt[0]][u_slt[1]]
                u_slt_cost = self.carp.graph.adj_matrix[u_slt[0]][u_slt[1]]
                load[k] = load[k] + u_slt_dmnd
                cost[k] = cost[k] + d_min + u_slt_cost
                i = u_slt[1]
                
            rtn_cost = self.carp.graph.mul_sp[i][1]
            cost[k] = cost[k] + rtn_cost
            k = k + 1
        return(sum(cost), road)
        # self.display(road, cost)

    def display(self, road, cost):
        print("***road and cost***")
        
        mssg = "s "
        for r in road:
            mssg += "0,"
            for t in r:
                mssg += "(" + str(t[0]) + "," + str(t[1]) + "),"
            mssg += "0,"
        mssg = mssg[0: -1]
        print(mssg)
        print("q " + str(cost))


        cnt = 0
        for i in road:
               cnt = cnt + len(i)
        print("\n***edge cnt***")
        print(str(cnt)) 

        cnt = 0
        print("\n***vehicles cnt***")
        print(str(len(road)))


    def run(self, rpt_time):
        best_res = None
        for _ in range(rpt_time):
            cost, road = self.path_scanning()
            if best_res is None:
                best_res = (cost, road)
            if cost < best_res[0]:
                best_res = (cost, road)
        
        self.display(best_res[1], best_res[0])
    

        
    


                

            
            


# if __name__ == '__main__':


        
