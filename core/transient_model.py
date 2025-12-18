
"""
Anukaran AI - Transient Reactor Model
=====================================
Unsteady-state packed bed reactor with catalyst deactivation.
Reaction: CH4 → C + 2H2
"""

import numpy as np
from scipy.integrate import solve_ivp
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Callable
import warnings

warnings.filterwarnings('ignore')

# Physical constants
R_GAS = 8.314
MW_CH4 = 16.04e-3
MW_H2 = 2.016e-3
MW_C = 12.01e-3
MW_N2 = 28.01e-3


# ============================================================================
# DEACTIVATION MODELS
# ============================================================================

@dataclass
class DeactivationParams:
    """Parameters for catalyst deactivation"""
    k_d: float = 0.01          # Deactivation rate constant [1/min]
    order: int = 1             # Deactivation order (1 or 2)
    E_d: float = 50000.0       # Deactivation activation energy [J/mol]
    T_ref: float = 1073.15     # Reference temperature [K] (800°C)
    
    def get_kd_at_temperature(self, T: float) -> float:
        """Get temperature-dependent deactivation rate constant"""
        return self.k_d * np.exp(-self.E_d / R_GAS * (1/T - 1/self.T_ref))


class DeactivationModel:
    """
    Catalyst deactivation kinetics.
    
    Models available:
    - 'linear': da/dt = -k_d (constant rate)
    - 'first_order': da/dt = -k_d * a
    - 'second_order': da/dt = -k_d * a^2
    - 'coking': da/dt = -k_d * a * C_CH4
    """
    
    def __init__(self, model_type: str = 'first_order', params: DeactivationParams = None):
        self.model_type = model_type
        self.params = params or DeactivationParams()
    
    def rate(self, activity: float, T: float, C_CH4: float = 0.0) -> float:
        """
        Calculate deactivation rate da/dt.
        
        Args:
            activity: Current catalyst activity (0 to 1)
            T: Temperature [K]
            C_CH4: CH4 concentration [kmol/m³] (for coking model)
        
        Returns:
            da/dt [1/min] (negative value)
        """
        k_d = self.params.get_kd_at_temperature(T)
        
        if self.model_type == 'linear':
            return -k_d
        elif self.model_type == 'first_order':
            return -k_d * activity
        elif self.model_type == 'second_order':
            return -k_d * activity ** 2
        elif self.model_type == 'coking':
            return -k_d * activity * (C_CH4 * 1000)  # Convert to mol/m³
        else:
            return -k_d * activity  # Default to first order


# ============================================================================
# TRANSPORT PROPERTIES (Same as steady-state model)
# ============================================================================

def gas_viscosity(T, y_CH4, y_H2, y_N2):
    mu_CH4 = 1.02e-5 * (T / 300) ** 0.87
    mu_H2 = 8.76e-6 * (T / 300) ** 0.68
    mu_N2 = 1.78e-5 * (T / 300) ** 0.67
    return y_CH4 * mu_CH4 + y_H2 * mu_H2 + y_N2 * mu_N2


def gas_density(T, P, y_CH4, y_H2, y_N2):
    MW_mix = y_CH4 * MW_CH4 + y_H2 * MW_H2 + y_N2 * MW_N2
    return P * MW_mix / (R_GAS * T)


def diffusivity_CH4(T, P):
    return 1.87e-5 * (T / 300) ** 1.75 * (101325 / P)


def arrhenius_rate_constant(T, A, Ea, beta=0):
    return A * T ** beta * np.exp(-Ea / (R_GAS * T))


def effectiveness_factor(phi):
    if phi < 0.1:
        return 1.0
    elif phi > 100:
        return 3.0 / phi
    else:
        return (3.0 / phi) * (1.0 / np.tanh(phi) - 1.0 / phi)


def ergun_pressure_drop(u, rho, mu, d_p, eps):
    term1 = 150 * mu * (1 - eps)**2 / (d_p**2 * eps**3) * u
    term2 = 1.75 * rho * (1 - eps) / (d_p * eps**3) * u**2
    return term1 + term2


# ============================================================================
# TRANSIENT REACTOR CONFIG
# ============================================================================

@dataclass
class TransientReactorConfig:
    """Configuration for transient reactor simulation"""
    # Geometry
    diameter: float              # Reactor diameter [m]
    bed_height: float            # Bed height [m]
    
    # Catalyst
    particle_diameter: float     # Particle diameter [m]
    catalyst_density: float      # Particle density [kg/m³]
    particle_porosity: float     # Intra-particle porosity [-]
    tortuosity: float            # Tortuosity [-]
    bed_porosity: float          # Bed void fraction [-]
    
    # Operating conditions
    temperature: float           # Operating temperature [K]
    inlet_pressure: float        # Inlet pressure [Pa]
    flow_rate: float             # Volumetric flow rate [m³/s]
    
    # Inlet composition
    y_CH4_in: float              # CH4 mole fraction
    y_H2_in: float               # H2 mole fraction
    y_N2_in: float               # N2 mole fraction
    
    # Kinetics
    pre_exponential: float       # Pre-exponential factor [1/s]
    activation_energy: float     # Activation energy [J/mol]
    beta: float = 0.0            # Temperature exponent
    
    @property
    def cross_section_area(self) -> float:
        return np.pi * (self.diameter / 2) ** 2


# ==================================
