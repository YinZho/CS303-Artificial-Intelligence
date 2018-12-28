import sys
import time
import numpy as np

matrix_train = None
matrix_test = None

def read_file(file_name, data_type):
    tmp = []
    with open(file_name, 'r') as fp:
        for line in fp:
            line = line.split()
            data = [float(i) for i in line]
            tmp.append(data)
    if data_type == 'train':
        global matrix_train
        matrix_train = np.array(tmp)
    else:
        global matrix_test
        matrix_test = np.array(tmp)

def train(learning_rate=0.01):
    size = matrix_train.shape[0]
    dimension = matrix_train.shape[1] - 1

    w = np.zeros((dimension,), dtype=float)
    t = 0

    for _ in range(20):
        for i in range(size):
            t += 1
            eta = 1 / (t*learning_rate)
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
    curtime = time.time()
    train_data = sys.argv[1]
    test_data = sys.argv[2]
    time_budget = sys.argv[4]
    read_file(train_data, 'train')
    read_file(test_data, 'test')
    predict(train())
    print(time.time() - curtime)
