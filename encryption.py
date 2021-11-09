import math
from random import randint

def is_prime(x):
    i = 2
    root = math.ceil(math.sqrt(x))
    while i <= root:
        if x % i == 0:
            return False
        i += 1
    return True


def generate_prime():
    x = randint(100, 9999)
    while True:
        if is_prime(x):
            break
        else:
            x += 1
    return x

def main():
    p = generate_prime()
    q = generate_prime()
    while q == p:
        q = generate_prime()

    n = p * q

    n1 = (p - 1) * (q - 1)

