import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='social_network' ,help='the absolute path of the social network file')
    parser.add_argument('-k', dest='seed_size', help='predefined size of the seed set')
    parser.add_argument('-m', dest='diffusion_model', help='only be IC or LT')
    parser.add_argument('-t', dest='time_budget', help='the seconds that my algorithm can spend on this instance')
