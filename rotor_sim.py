from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np


Array = np.ndarray


def qmul(a: Array, b: Array) -> Array:
    """Broadcasting quaternion multiplication, order [w, x, y, z]."""
    w1, x1, y1, z1 = np.moveaxis(a, -1, 0)
    w2, x2, y2, z2 = np.moveaxis(b, -1, 0)

    return np.stack(
        (
            w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
            w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
            w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
        ),
        axis=-1,
    )


def qconj(q: Array) -> Array:
    """Quaternion conjugate."""
    result = q.copy()
    result[..., 1:] *= -1.0
    return result


def qnormalize(q: Array, epsilon: float = 1e-12) -> Array:
    """Normalize one quaternion or an array of quaternions."""
    norm = np.linalg.norm(q, axis=-1, keepdims=True)
    if np.any(norm < epsilon):
        raise ValueError("Cannot normalize a zero or near-zero quaternion.")
    return q / norm


def qexp_pure(theta: float, axis: Array) -> Array:
    """Exponential of a pure quaternion theta * axis."""
    axis = np.asarray(axis, dtype=float)
    axis_norm = np.linalg.norm(axis)

    if axis.shape != (3,):
        raise ValueError("axis must have shape (3,).")
    if axis_norm < 1e-12:
        raise ValueError("axis must be nonzero.")

    unit_axis = axis / axis_norm
    half_theta = theta / 2.0
    return np.concatenate(
        ([np.cos(half_theta)], np.sin(half_theta) * unit_axis)
    )


def rotate_vector(q: Array, vector: Array) -> Array:
    """Rotate a 3-D vector with a unit quaternion."""
    vector = np.asarray(vector, dtype=float)
    if vector.shape != (3,):
        raise ValueError("vector must have shape (3,).")

    pure_vector = np.concatenate(([0.0], vector))
    return qmul(qmul(q, pure_vector), qconj(q))[1:]


def anchor_angle(lam: float, alpha: float = 1.0) -> float:
    """Example anchor map S(lambda) = 2*pi*frac(alpha*lambda)."""
    return 2.0 * np.pi * ((alpha * lam) % 1.0)


def seed_anchor(
    lam: float,
    axis: Sequence[float] = (0.0, 0.0, 1.0),
    alpha: float = 1.0,
) -> Array:
    return qexp_pure(anchor_angle(lam, alpha), np.asarray(axis))


def mer_field(
    q: Array,
    resistance: Array,
    kappa: Sequence[float] = (1.0, 1.0, 1.0),
    spacing: Sequence[float] = (1.0, 1.0, 1.0),
) -> Array:
    """Example M = k1|grad(Phi)|^2 + k2/R + k3*H.

    q shape: (..., 4), with the spatial dimensions before the quaternion axis.
    resistance shape: spatial dimensions only.
    Curvature H is a zero placeholder until supplied.
    """
    q = np.asarray(q, dtype=float)
    resistance = np.asarray(resistance, dtype=float)

    if q.shape[-1] != 4:
        raise ValueError("q must have final dimension 4.")
    if q.shape[:-1] != resistance.shape:
        raise ValueError("q spatial shape must match resistance shape.")

    grad_norm_sq = np.zeros_like(resistance, dtype=float)

    for component in range(4):
        gradients = np.gradient(
            q[..., component],
            *spacing,
            edge_order=1,
        )
        for gradient in gradients:
            grad_norm_sq += gradient**2

    safe_resistance = np.maximum(resistance, 1e-8)
    curvature = np.zeros_like(resistance)

    return (
        float(kappa[0]) * grad_norm_sq
        + float(kappa[1]) / safe_resistance
        + float(kappa[2]) * curvature
    )


@dataclass(frozen=True)
class RotorConfig:
    gamma: float = 0.05
    dt: float = 0.01


def rotor_derivative(
    q: Array,
    omega: Array,
    qeq: Optional[Array] = None,
    gamma: float | Array = 0.0,
) -> Array:
    """Compute dq/dt = 1/2 q*Omega - gamma(q-qeq)."""
    q = np.asarray(q, dtype=float)
    omega = np.asarray(omega, dtype=float)

    if q.shape[-1] != 4:
        raise ValueError("q must have final dimension 4.")
    if omega.shape != q.shape[:-1] + (3,):
        raise ValueError("omega must have shape q.shape[:-1] + (3,).")

    pure_omega = np.concatenate(
        (np.zeros(omega.shape[:-1] + (1,)), omega),
        axis=-1,
    )

    equilibrium = q if qeq is None else np.asarray(qeq, dtype=float)
    if equilibrium.shape != q.shape:
        raise ValueError("qeq must have the same shape as q.")

    return 0.5 * qmul(q, pure_omega) - np.asarray(gamma)[..., None] * (
        q - equilibrium
    )


def evolve_rotor(
    q: Array,
    omega: Array,
    qeq: Optional[Array] = None,
    gamma: float | Array = 0.0,
    config: RotorConfig | None = None,
) -> Array:
    """One normalized explicit Euler step.

    Despite the original comment, this is Euler, not midpoint.
    """
    config = config or RotorConfig()
    derivative = rotor_derivative(q, omega, qeq, gamma)
    next_q = np.asarray(q, dtype=float) + config.dt * derivative
    return qnormalize(next_q)


def demo() -> None:
    q = seed_anchor(0.37)
    print("anchor angle:", anchor_angle(0.37))
    print("anchor quaternion:", q)
    print("rotated z:", rotate_vector(q, np.array([0.0, 0.0, 1.0])))

import numpy as np

from rotor_sim import (
    RotorConfig,
    evolve_rotor,
    mer_field,
    qnormalize,
    seed_anchor,
)


def test_field_functions():
    shape = (4, 4, 4)

    q0 = np.zeros(shape + (4,), dtype=float)
    q0[..., 0] = 1.0

    omega = np.zeros(shape + (3,), dtype=float)
    omega[..., 2] = 1.0

    resistance = np.ones(shape, dtype=float)

    q1 = evolve_rotor(
        q0,
        omega,
        config=RotorConfig(dt=0.01),
    )

    mer = mer_field(q1, resistance)

    assert q1.shape == q0.shape
    assert mer.shape == resistance.shape
    assert np.allclose(np.linalg.norm(q1, axis=-1), 1.0, atol=1e-10)

    print("field shape:", q1.shape)
    print("MER shape:", mer.shape)
    print("quaternion norm:", np.min(np.linalg.norm(q1, axis=-1)))
    print("MER range:", float(mer.min()), float(mer.max()))
    print("Field test passed.")




if __name__ == "__main__":
    demo()