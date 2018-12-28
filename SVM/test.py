import os
import sys
import random
import numpy as np


if __name__ == "__main__":
    file_name = sys.argv[1]
    propotion = sys.argv[2]
    data = np.loadtxt(file_name)
    size = data.shape[0]
    idx = [i for i in range(size)]
    random.shuffle(idx)
    select_train = idx[:int(size*propotion)]
    
    matrix_train = []
    matrix_test = []
    test_ans = []

    for i in range(size):
        if i in select_train:
            matrix_train.append(data[i].tolist())
        else:
            matrix_test.append(data[i][:-1].tolist())
            test_ans.append(data[i][-1].tolist())

    train_file_path = './test/train.txt'
    test_file_path = './test/test.txt'
    ans_path = './test/ans.txt'
    out_path = './test/out.txt'

    with open(train_file_path, 'w') as f:
        for item in matrix_train:
            f.write(" ".join(str(x) for x in item))
            f.write("\n")

    with open(test_file_path, 'w') as f:
        for item in matrix_test:
            f.write(" ".join(str(x) for x in item))
            f.write("\n")

    with open(ans_path, 'w') as f:
        f.write("\n".join(str(x) for x in test_ans))

    os.system('python SVM.py {} {} -t 60 > {}'.format(train_file_path, test_file_path, out_path))
    f1 = open(ans_path)
    f2 = open(out_path)

    cnt = 0
    total = 0
    for line1 in f1:
        for line2 in f2:
            total += 1
            if line1 != line2:
                cnt += 1
    print(cnt/total)
                
                

    

    