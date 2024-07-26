import math


def binomial_coefficient(n, k):
    if k > n:
        return 0
    if k == 0 or k == n:
        return 1
    
    return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))


total_nodes = 50
print(binomial_coefficient(total_nodes, int(total_nodes*2/3)))
