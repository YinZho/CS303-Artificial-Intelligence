import sys
import time
import numpy as np

matrix_train = None
matrix_test = None

def train(learning_rate=0.01):
    size = matrix_train.shape[0]
    dimension = matrix_train.shape[1] - 1

    w = np.zeros((dimension,), dtype=float)
    t = 0

    for _ in range(20):
        for i in range(size):
            t += 1
            eta = 1 / (t*learning_rate)
            print(eta)
            if matrix_train[i][-1] * np.dot(w, matrix_train[i][:dimension]) < 1:
                w = (1-eta*learning_rate)*w + eta* np.dot(matrix_train[i][-1], matrix_train[i][:dimension])
            else:
                w = (1-eta*learning_rate)*w
    return w
    
def predict(w):
    size = matrix_test.shape[0]
    for i in range(size):
        print(np.sign(np.dot(matrix_test[i], w)))


if __name__ == "__main__":
    train_data = sys.argv[1]
    test_data = sys.argv[2]
    time_budget = sys.argv[4]
    matrix_train = np.loadtxt(train_data, dtype=float)
    matrix_test = np.loadtxt(test_data, dtype=float)
    predict(train())
