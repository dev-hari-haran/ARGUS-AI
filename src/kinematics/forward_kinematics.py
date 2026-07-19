import numpy as np

class ForwardKinematics:
    def compute(self, q1: np.ndarray, q2: np.ndarray, l1: np.ndarray, l2: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Vectorized computation of Forward Kinematics.
        Args:
            q1: Array of joint 1 angles (radians).
            q2: Array of joint 2 angles (radians).
            l1: Array of link 1 lengths.
            l2: Array of link 2 lengths.
        Returns:
            Tuple of (x, y) coordinates.
        """
        x = l1 * np.cos(q1) + l2 * np.cos(q1 + q2)
        y = l1 * np.sin(q1) + l2 * np.sin(q1 + q2)
        return x, y
