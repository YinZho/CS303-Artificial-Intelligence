

if __name__ == '__main__':
    fn = 'epinions-d-5.txt'
    fr = open(fn, 'r')
    fw = open('epinions-d-5_tran.txt', 'w')
    for i, line in enumerate(fr):
        if i == 0:
            fw.write(line)
        else:
            line = line.split(' ')
            line[0] = int(line[0])
            line[1] = int(line[1])
            fw.write('{0} {1} {2}'.format(line[0]+1, line[1]+1, line[2]))
    