from scipy.optimize import minimize
import numpy as np


def F(x, p, b, beta):
    return - b * ((x[0] / p[0]) ** beta[0]) * ((x[1] / p[1]) ** beta[1])

def optimization(seed_weights,
                 input_prices,
                 b,
                 beta,
                 method='SLSQP'):

    cons = ({'type': 'eq', 'fun': lambda x: np.array([sum(x) - 1])})

    return minimize(F, seed_weights, args=(input_prices, b, beta), constraints=cons, bounds=[(0, 1)] * len(seed_weights), method=method)
