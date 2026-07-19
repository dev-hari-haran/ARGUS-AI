import numpy as np
import pytest
from src.kinematics.forward_kinematics import ForwardKinematics
from src.kinematics.workspace import Workspace

def test_forward_kinematics_origin():
    fk = ForwardKinematics()
    l1, l2 = np.array([1.0]), np.array([1.0])
    x, y = fk.compute(np.array([0.0]), np.array([0.0]), l1, l2)
    assert np.isclose(x[0], 2.0)
    assert np.isclose(y[0], 0.0)

def test_forward_kinematics_bent():
    fk = ForwardKinematics()
    l1, l2 = np.array([1.0]), np.array([1.0])
    x, y = fk.compute(np.array([0.0]), np.array([np.pi/2]), l1, l2)
    assert np.isclose(x[0], 1.0)
    assert np.isclose(y[0], 1.0)

def test_workspace_boundaries():
    ws = Workspace()
    l1, l2 = np.array([1.0]), np.array([1.0])
    min_r, max_r = ws.get_boundaries(l1, l2)
    assert min_r[0] == 0.0
    assert max_r[0] == 2.0
    
def test_is_in_workspace():
    ws = Workspace()
    l1, l2 = np.array([1.0]), np.array([1.0])
    assert ws.is_in_workspace(np.array([1.0]), np.array([1.0]), l1, l2)[0]
    assert not ws.is_in_workspace(np.array([3.0]), np.array([0.0]), l1, l2)[0]
