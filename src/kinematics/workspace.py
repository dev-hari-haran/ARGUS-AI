import numpy as np

class Workspace:
    def get_boundaries(self, l1: np.ndarray, l2: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Returns the minimum and maximum reach (radius) of the manipulator.
        """
        min_radius = np.abs(l1 - l2)
        max_radius = l1 + l2
        return min_radius, max_radius
        
    def is_in_workspace(self, x: np.ndarray, y: np.ndarray, l1: np.ndarray, l2: np.ndarray) -> np.ndarray:
        """
        Checks if given (x, y) coordinates fall within the reachable workspace.
        """
        min_r, max_r = self.get_boundaries(l1, l2)
        r_squared = x**2 + y**2
        return (r_squared >= min_r**2 - 1e-6) & (r_squared <= max_r**2 + 1e-6)
