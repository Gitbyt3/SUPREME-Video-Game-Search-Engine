import numpy as np
import math
def sigmoid_scaling(scores, shift=None, slope=None):
    """
    Apply logistic (sigmoid) scaling to a list of scores.

    Args:
        scores (list or array-like of float): The raw scores.
        shift (float, optional): A value to subtract from each score. 
            If None, the mean of scores is used.
        slope (float, optional): A multiplier for the scaled score.
            If None, the slope is set to 1/std(scores) (or 1 if std=0).

    Returns:
        list of float: The scores after applying the logistic scaling, which will be in (0, 1).
    """

    # If shift is not provided, use the mean
    if shift is None:
        shift = np.mean(scores)
    
    # If slope is not provided, compute it as the inverse of the standard deviation.
    std = np.std(scores)
    if slope is None:
        slope = 1.0 / std if std != 0 else 1.0
        
    # Apply the sigmoid function to each score
    return np.array([1 / (1 + math.exp(-slope * ((0 if score is None else score) - shift))) for score in scores])

def max_min_scaling(scores):
    return (scores - scores.min()) / (scores.max() - scores.min())

def standard_scaling(scores):
    return (scores - np.mean(scores)) / np.std(scores)