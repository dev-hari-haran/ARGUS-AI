import numpy as np
from src.kinematics.forward_kinematics import ForwardKinematics

class LevenbergMarquardt:
    def __init__(self, initial_lambda: float = 0.1, lambda_multiplier: float = 10.0, max_iterations: int = 100, tolerance: float = 1e-4):
        """
        Levenberg-Marquardt (LM) Inverse Kinematics solver.
        A robust default that offers faster convergence near singularities.
        
        Args:
            initial_lambda: Starting value for the damping factor.
            lambda_multiplier: Factor to increase/decrease lambda.
            max_iterations: Maximum number of optimization steps.
            tolerance: Convergence threshold for positional error.
        """
        self.initial_lambda = initial_lambda
        self.lambda_multiplier = lambda_multiplier
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
        Solves the IK problem for the given target using Levenberg-Marquardt.
        
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
        
        current_lambda = self.initial_lambda
        
        current_x, current_y = self.fk.compute(q[0], q[1], l1, l2)
        current_pos = np.array([current_x, current_y])
        error = target - current_pos
        error_norm = np.linalg.norm(error)
        
        for _ in range(self.max_iterations):
            if error_norm < self.tolerance:
                break
                
            J = self.compute_jacobian(q[0], q[1], l1, l2)
            J_T = J.T
            
            # Marquardt's contribution: use diag(J^T J) instead of identity
            # to adapt to the curvature in different directions.
            JT_J = J_T @ J
            diag_JT_J = np.diag(np.diag(JT_J))
            
            # Avoid division by zero if diagonal is exactly 0
            if np.all(diag_JT_J == 0):
                diag_JT_J = np.eye(2)
                
            matrix_to_invert = JT_J + current_lambda * diag_JT_J
            delta_q = np.linalg.inv(matrix_to_invert) @ J_T @ error
            
            q_new = q + delta_q
            
            # Evaluate new position
            new_x, new_y = self.fk.compute(q_new[0], q_new[1], l1, l2)
            new_pos = np.array([new_x, new_y])
            new_error = target - new_pos
            new_error_norm = np.linalg.norm(new_error)
            
            if new_error_norm < error_norm:
                # Improvement: accept the step, decrease lambda
                q = q_new
                error = new_error
                error_norm = new_error_norm
                current_lambda /= self.lambda_multiplier
            else:
                # No improvement: reject the step, increase lambda
                current_lambda *= self.lambda_multiplier
                
        return q
