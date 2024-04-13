# Utilities for np arrays
import numpy as np


def normalize_matrix(matrix: np.ndarray) -> np.ndarray:
    # Divide each row by its sum to normalize it
    for i in range(matrix.shape[0]):
        matrix[i] /= np.sum(matrix[i])
    return matrix
