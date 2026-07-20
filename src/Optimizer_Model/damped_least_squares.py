import numpy as np
from src.kinematics.forward_kinematics import ForwardKinematics

class DampedLeastSquares:
    def __init__(self, damping_factor: float = 0.1, max_iterations: int = 100, tolerance: float = 1e-4):
        """
        Damped Least Squares (DLS) Inverse Kinematics solver.
        Provides robust convergence near singularities.
        
        Args:
            damping_factor: The lambda value used for damping.
            max_iterations: Maximum number of optimization steps.
            tolerance: Convergence threshold for positional error.
        """
        self.damping_factor = damping_factor
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.fk = ForwardKinematics()

    def compute_jacobian(self, q1: float, q2: float, l1: float, l2: float) -> np.ndarray:
        """Computes the 2x2 Jacobian matrix for the 2-DOF planar arm."""
        J = np.zeros((2, 2))
        # dx/dq
        J[0, 0] = -l1 * np.sin(q1) - l2 * np.sin(q1 + q2)
        J[0, 1] = -l2 * np.sin(q1 + q2)
        # dy/dq
        J[1, 0] = l1 * np.cos(q1) + l2 * np.cos(q1 + q2)
        J[1, 1] = l2 * np.cos(q1 + q2)
        return J

    def solve(self, target_x: float, target_y: float, initial_q: np.ndarray, link_lengths: tuple[float, float]) -> np.ndarray:
        """
        Solves the IK problem for the given target.
        
        Args:
            target_x: Target X coordinate.
            target_y: Target Y coordinate.
            initial_q: Initial joint angles [q1, q2].
            link_lengths: Lengths of the two links (l1, l2).
            
        Returns:
            Optimized joint angles [q1, q2].
        """
        q = np.array(initial_q, dtype=float)
        l1, l2 = link_lengths
        target = np.array([target_x, target_y])
        
        for _ in range(self.max_iterations):
            current_x, current_y = self.fk.compute(q[0], q[1], l1, l2)
            current_pos = np.array([current_x, current_y])
            
            error = target - current_pos
            if np.linalg.norm(error) < self.tolerance:
                break
                
            J = self.compute_jacobian(q[0], q[1], l1, l2)
            
            # Damped Least Squares update: delta_q = (J^T J + lambda^2 I)^-1 J^T e
            J_T = J.T
            I = np.eye(2)
            
            # Compute pseudo-inverse with damping
            matrix_to_invert = J_T @ J + (self.damping_factor ** 2) * I
            delta_q = np.linalg.inv(matrix_to_invert) @ J_T @ error
            
            q += delta_q
            
        return q
