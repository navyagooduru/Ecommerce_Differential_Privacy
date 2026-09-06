import numpy as np


def add_laplace_noise(value, sensitivity=1, epsilon=1.0):
    """
    Add Laplace noise to a value for Differential Privacy.

    value       : Original value
    sensitivity : How much one user's data can change the result
    epsilon     : Privacy level
                  Smaller epsilon = more privacy
                  Larger epsilon = less noise
    """

    scale = sensitivity / epsilon

    noise = np.random.laplace(0, scale)

    noisy_value = value + noise

    return noisy_value