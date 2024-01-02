# __init__.py

import argparse
import numpy as np

def gen_numbers(n_numbers):
    '''
    Generates n_numbers integers ranging from 0 to 99
    '''
    return np.random.randint(100, size=n_numbers)

def summarize(numbers):
    '''
    Computes the mean of the numbers ndarray
    '''
    return np.mean(numbers)

def main():
    # CLI arguments
    parser = argparse.ArgumentParser(description='A simple tool for computing the mean of a random list')
    parser.add_argument('-N', metavar='INT', type=int, help='Number of random integers [%(default)s]', default=5)
    args = parser.parse_args()
    # Generate the random numbers
    numbers = gen_numbers(args.N)
    # Calculate the mean
    mean = summarize(numbers)
    # Print the mean
    print(mean)

if __name__ == "__main__":
    main()
