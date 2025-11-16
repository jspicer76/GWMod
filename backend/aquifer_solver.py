import numpy as np
from math import exp, log
from dataclasses import dataclass

def estimate_aquifer_properties(wells):
    """
    Placeholder:
    Compute T, K, S from pumping & observation wells.
    Final version: incorporate Theis / Neuman / Cooper-Jacob.
    """

    T = 5000       # ft²/day (placeholder)
    K = 100        # ft/day (placeholder)
    S = 0.2        # specific yield for unconfined

    return {
        "Transmissivity T": T,
        "Hydraulic Conductivity K": K,
        "Storativity/Specific Yield S": S,
        "Method": "Jacob (placeholder)"
    }
# ==============================
#  DATA STRUCTURES
# ==============================

@dataclass
class PumpingWell:
    x: float
    y: float
    Q: float  # pumping rate (ft³/day or gpm converted)


@dataclass
class ObservationPoint:
    x: float
    y: float
    t: np.ndarray     # seconds or days
    s: np.ndarray     # drawdown (ft)


# ==============================
#  UTILITY: WELL DISTANCE
# ==============================

def distance(well, obs):
    return np.sqrt((well.x - obs.x)**2 + (well.y - obs.y)**2)


# ==============================
#  THEIS WELL FUNCTION (W(u))
# ==============================

def W_theis(u):
    """Exact Theis well function using exponential integral."""
    # For small u, use the asymptotic log expansion.
    if u < 1e-5:
        return -0.57721566 - np.log(u) + u - u**2/4
    # Otherwise use exponential integral approximation
    summation = 0
    term = u
    for n in range(1, 50):
        summation += term / (n * np.math.factorial(n))
        term *= u
    return -0.57721 - np.log(u) + summation


# ==============================
#  THEIS SOLUTION (T, S)
# ==============================

def theis_drawdown(r, t, Q, T, S):
    u = (r**2 * S) / (4 * T * t)
    return (Q / (4 * np.pi * T)) * np.array([W_theis(ui) for ui in u])


# ==============================
#  NEUMAN UNCONFINED (DELAYED YIELD)
# ==============================

def neuman_drawdown(r, t, Q, T, Sy, Kz_over_Kr=0.1):
    """
    Simplified Neuman solution for unconfined aquifers.
    Includes delayed yield via Sy.
    Vertical anisotropy Kz/Kr is adjustable.
    """
    # Effective storativity
    S_eff = Sy * (1 + Kz_over_Kr)

    u = (r**2 * S_eff) / (4 * T * t)
    # Add delayed yield exponential term
    delayed_term = Sy * (1 - np.exp(-t / (S_eff * 50)))  # softened approximation
    return (Q / (4 * np.pi * T)) * np.array([W_theis(ui) for ui in u]) + delayed_term


# ==============================
#  LEAST SQUARES FITTING ENGINE
# ==============================

def fit_theis(well, obs):
    r = distance(well, obs)

    t = obs.t
    s = obs.s

    # Initial guesses
    T0 = 3000
    S0 = 1e-4

    params = np.array([T0, S0])

    for _ in range(30):
        T, S = params
        model = theis_drawdown(r, t, well.Q, T, S)

        # Jacobian
        dT = (theis_drawdown(r, t, well.Q, T * 1.001, S) - model) / (0.001 * T)
        dS = (theis_drawdown(r, t, well.Q, T, S * 1.001) - model) / (0.001 * S)
        J = np.vstack([dT, dS]).T

        # Least squares update
        residual = s - model
        update = np.linalg.lstsq(J, residual, rcond=None)[0]
        params += update

        if np.linalg.norm(update) < 1e-6:
            break

    T, S = params
    return T, S


def fit_neuman(well, obs):
    r = distance(well, obs)

    t = obs.t
    s = obs.s

    # Initial guesses
    T0 = 3000
    Sy0 = 0.15
    Aniso0 = 0.1

    params = np.array([T0, Sy0, Aniso0])

    for _ in range(40):
        T, Sy, A = params
        model = neuman_drawdown(r, t, well.Q, T, Sy, A)

        dT = (neuman_drawdown(r, t, well.Q, T * 1.001, Sy, A) - model) / (0.001 * T)
        dSy = (neuman_drawdown(r, t, well.Q, T, Sy * 1.001, A) - model) / (0.001 * Sy)
        dA = (neuman_drawdown(r, t, well.Q, T, Sy, A * 1.001) - model) / (0.001 * A)

        J = np.vstack([dT, dSy, dA]).T
        residual = s - model

        update = np.linalg.lstsq(J, residual, rcond=None)[0]
        params += update

        if np.linalg.norm(update) < 1e-6:
            break

    T, Sy, A = params
    return T, Sy, A


# ==============================
#  MAIN ENTRY POINT FOR GUI
# ==============================

def estimate_aquifer_properties(pumping_well, observation_wells):
    """
    pumping_well  : PumpingWell(x,y,Q)
    observation_wells: list of ObservationPoint
    """

    results = {}

    for i, obs in enumerate(observation_wells):
        try:
            T, S = fit_theis(pumping_well, obs)
            results[f"Obs Well {i+1} — Theis"] = {
                "T (ft²/day)": T,
                "S (dimensionless)": S
            }
        except:
            results[f"Obs Well {i+1} — Theis"] = "Solver failed"

        try:
            T, Sy, A = fit_neuman(pumping_well, obs)
            K = T / obs.t[0] if obs.t[0] > 0 else np.nan
            results[f"Obs Well {i+1} — Neuman"] = {
                "T (ft²/day)": T,
                "Sy": Sy,
                "Vertical/Horizontal K ratio": A
            }
        except:
            results[f"Obs Well {i+1} — Neuman"] = "Solver failed"

    return results