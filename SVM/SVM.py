import sys
import time
import numpy as np

def train(learning_rate=0.05):
    w = np.zeros((X.shape[1],), dtype=float)
    t = 0

    for _ in range(20):
        for j in range(X.shape[0]):
            t += 1
            eta = 1 / (t*learning_rate)
            if Y[j] * np.dot(w, X[j]) < 1:
                w = w - eta*(learning_rate*w - Y[j]*X[j])
            else:
                w = w - eta*(learning_rate*w)
    return w
    
def predict(w):
    if matrix_test.shape[1] == X.shape[1] + 1:
        vector = matrix_test[:, :-1]
    for v in vector:
        print(np.sign(np.dot(w, v)))

if __name__ == "__main__":
    train_data = sys.argv[1]
    test_data = sys.argv[2]
    time_budget = sys.argv[4]
    global X, Y, matrix_test
    matrix_train = np.loadtxt(train_data, dtype=float)
    X = matrix_train[:, :-1]
    Y = matrix_train[:, -1]
    matrix_test = np.loadtxt(test_data, dtype=float)
    predict(train())
