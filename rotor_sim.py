# rotor_sim.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np


Array = np.ndarray


def qmul(a: Array, b: Array) -> Array:
    """Broadcasting quaternion multiplication.

    Quaternion order: [w, x, y, z].
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)

    if a.shape[-1] != 4 or b.shape[-1] != 4:
        raise ValueError(
            "Quaternion inputs must have final dimension 4."
        )

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
    """Return the quaternion conjugate."""
    q = np.asarray(q, dtype=float)
    result = q.copy()
    result[..., 1:] *= -1.0
    return result


def qnormalize(
    q: Array,
    epsilon: float = 1e-12,
) -> Array:
    """Normalize one quaternion or an array of quaternions."""
    q = np.asarray(q, dtype=float)
    norm = np.linalg.norm(q, axis=-1, keepdims=True)

    if np.any(norm < epsilon):
        raise ValueError(
            "Cannot normalize a zero or near-zero quaternion."
        )

    return q / norm


def qexp_pure(
    theta: float,
    axis: Array,
) -> Array:
    """Create a quaternion from an angle and a 3-D rotation axis."""
    axis = np.asarray(axis, dtype=float)

    if axis.shape != (3,):
        raise ValueError("axis must have shape (3,).")

    axis_norm = np.linalg.norm(axis)

    if axis_norm < 1e-12:
        raise ValueError("axis must be nonzero.")

    unit_axis = axis / axis_norm
    half_theta = theta / 2.0

    return np.concatenate(
        (
            [np.cos(half_theta)],
            np.sin(half_theta) * unit_axis,
        )
    )


def rotate_vector(
    q: Array,
    vector: Array,
) -> Array:
    """Rotate a 3-D vector using a unit quaternion."""
    q = qnormalize(q)
    vector = np.asarray(vector, dtype=float)

    if vector.shape != (3,):
        raise ValueError("vector must have shape (3,).")

    pure_vector = np.concatenate(([0.0], vector))

    rotated = qmul(
        qmul(q, pure_vector),
        qconj(q),
    )

    return rotated[1:]


def anchor_angle(
    lam: float,
    alpha: float = 1.0,
) -> float:
    """Example anchor map: S(lambda)=2*pi*frac(alpha*lambda)."""
    return 2.0 * np.pi * ((alpha * lam) % 1.0)


def seed_anchor(
    lam: float,
    axis: Sequence[float] = (0.0, 0.0, 1.0),
    alpha: float = 1.0,
) -> Array:
    """Create a normalized rotor seed at a spectral anchor."""
    return qexp_pure(
        anchor_angle(lam, alpha),
        np.asarray(axis, dtype=float),
    )


def mer_field(
    q: Array,
    resistance: Array,
    kappa: Sequence[float] = (1.0, 1.0, 1.0),
    spacing: Sequence[float] = (1.0, 1.0, 1.0),
    curvature: Optional[Array] = None,
) -> Array:
    """
    Calculate the example rotor MER field:

        M = k1 * |grad(Phi)|^2
            + k2 / R
            + k3 * H

    q shape:
        (..., 4)

    resistance shape:
        spatial dimensions only

    curvature:
        optional spatial curvature field H
    """
    q = np.asarray(q, dtype=float)
    resistance = np.asarray(resistance, dtype=float)

    if q.shape[-1] != 4:
        raise ValueError(
            "q must have final dimension 4."
        )

    if q.shape[:-1] != resistance.shape:
        raise ValueError(
            "q spatial shape must match resistance shape."
        )

    if len(kappa) != 3:
        raise ValueError(
            "kappa must contain exactly three values."
        )

    if len(spacing) != len(resistance.shape):
        raise ValueError(
            "spacing must match the number of spatial dimensions."
        )

    gradient_norm_sq = np.zeros_like(
        resistance,
        dtype=float,
    )

    for component in range(4):
        gradients = np.gradient(
            q[..., component],
            *spacing,
            edge_order=1,
        )

        for gradient in gradients:
            gradient_norm_sq += gradient ** 2

    safe_resistance = np.maximum(
        resistance,
        1e-8,
    )

    if curvature is None:
        curvature_field = np.zeros_like(resistance)
    else:
        curvature_field = np.asarray(
            curvature,
            dtype=float,
        )

        if curvature_field.shape != resistance.shape:
            raise ValueError(
                "curvature must match resistance shape."
            )

    return (
        float(kappa[0]) * gradient_norm_sq
        + float(kappa[1]) / safe_resistance
        + float(kappa[2]) * curvature_field
    )


@dataclass(frozen=True)
class RotorConfig:
    """Numerical configuration for rotor evolution."""

    gamma: float = 0.05
    dt: float = 0.01


def rotor_derivative(
    q: Array,
    omega: Array,
    qeq: Optional[Array] = None,
    gamma: float | Array = 0.0,
) -> Array:
    """
    Compute:

        dq/dt = 1/2 * q * Omega - gamma * (q - qeq)
    """
    q = np.asarray(q, dtype=float)
    omega = np.asarray(omega, dtype=float)

    if q.shape[-1] != 4:
        raise ValueError(
            "q must have final dimension 4."
        )

    if omega.shape != q.shape[:-1] + (3,):
        raise ValueError(
            "omega must have shape q.shape[:-1] + (3,)."
        )

    pure_omega = np.concatenate(
        (
            np.zeros(omega.shape[:-1] + (1,)),
            omega,
        ),
        axis=-1,
    )

    equilibrium = (
        q
        if qeq is None
        else np.asarray(qeq, dtype=float)
    )

    if equilibrium.shape != q.shape:
        raise ValueError(
            "qeq must have the same shape as q."
        )

    damping = np.asarray(gamma, dtype=float)

    return (
        0.5 * qmul(q, pure_omega)
        - damping[..., None] * (q - equilibrium)
    )


def evolve_rotor(
    q: Array,
    omega: Array,
    qeq: Optional[Array] = None,
    gamma: float | Array = 0.0,
    config: Optional[RotorConfig] = None,
) -> Array:
    """
    Advance the rotor field by one normalized Euler step.

    This is explicit Euler with normalization, not midpoint integration.
    """
    if config is None:
        config = RotorConfig()

    derivative = rotor_derivative(
        q=q,
        omega=omega,
        qeq=qeq,
        gamma=gamma,
    )

    next_q = np.asarray(q, dtype=float)
    next_q = next_q + config.dt * derivative

    return qnormalize(next_q)


def demo() -> None:
    """Run the basic anchor and rotation smoke test."""
    q = seed_anchor(0.37)
    rotated_z = rotate_vector(
        q,
        np.array([0.0, 0.0, 1.0]),
    )

    print("anchor angle:", anchor_angle(0.37))
    print("anchor quaternion:", q)
    print("rotated z:", rotated_z)


if __name__ == "__main__":
    demo()