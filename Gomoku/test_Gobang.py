import unittest
import GoBang
import numpy as np

class Test_Gobang(unittest.TestCase):
    chessboard = np.zeros((15, 15))
    log_file = open('./log/chess_log (2).txt', 'r')
    for line in log_file.readlines():
        line = line.replace('\n', '')
        e = line.split(',')
        # print(e)
        chessboard[int(e[0]), int(e[1])] = int(e[2])
    ai = GoBang.AI(15, -1, 5)

    ai.go(chessboard)
    print(ai.candidate_list)
    chessboard[ai.candidate_list[-1][0], ai.candidate_list[-1][1]] = 1





