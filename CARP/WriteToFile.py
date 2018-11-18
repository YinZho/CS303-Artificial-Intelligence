


class Write:
    def __init__(self):
        self.file = open('testout.txt','w')

    def info_to_file(self, information):
        self.file.write("***{}***\n".format(information))

    def cont_to_file(self, object):
        self.file.write(str(object) + "\n")
