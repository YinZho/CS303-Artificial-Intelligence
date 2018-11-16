from multiprocessing import Process
def f(name):
    print('hello', name)

if __name__ == '__main__':
    procs = []
    p0 = Process(target=f, args=('alice',))
    procs.append(p0)
    p0.start()
    p1 = Process(target=f, args=('bob',))
    procs.append(p0)
    p1.start()
    p2 = Process(target=f, args=('caile',))
    procs.append(p2)
    p2.start()

    # for p in procs:
    #     p.join()