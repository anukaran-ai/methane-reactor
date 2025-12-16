import numpy as np
from scipy.integrate import solve_ivp
from dataclasses import dataclass

# --- PHYSICAL CONSTANTS ---
R_GAS = 8.314
MW_CH4 = 16.04e-3
MW_H2 = 2.016e-3
MW_C = 12.01e-3
MW_N2 = 28.01e-3

# --- HELPER FUNCTIONS ---
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

def heat_capacity_mix(T, y_CH4, y_H2, y_N2):
    Cp_CH4 = 35.69 + 0.0275 * T
    Cp_H2 = 28.84 + 0.00192 * T
    Cp_N2 = 29.12 + 0.00293 * T
    return y_CH4 * Cp_CH4 + y_H2 * Cp_H2 + y_N2 * Cp_N2

def arrhenius_rate_constant(T, A, Ea, beta):
    return A * T ** beta * np.exp(-Ea / (R_GAS * T))

def effectiveness_factor(phi):
    if phi < 0.1: return 1.0
    elif phi > 100: return 3.0 / phi
    else: return (3.0 / phi) * (1.0 / np.tanh(phi) - 1.0 / phi)

def ergun_pressure_drop(u, rho, mu, d_p, eps):
    term1 = 150 * mu * (1 - eps)**2 / (d_p**2 * eps**3) * u
    term2 = 1.75 * rho * (1 - eps) / (d_p * eps**3) * u**2
    return term1 + term2

# --- CONFIG CLASS ---
@dataclass
class ReactorConfig:
    diameter: float; bed_height: float; particle_diameter: float; catalyst_density: float
    particle_porosity: float; tortuosity: float; bed_porosity: float; catalyst_mass: float
    inlet_temperature: float; inlet_pressure: float; flow_rate: float
    y_CH4_in: float; y_H2_in: float; y_N2_in: float
    pre_exponential: float; activation_energy: float; beta: float; heat_of_reaction: float
    
    @property
    def cross_section_area(self) -> float:
        return np.pi * (self.diameter / 2) ** 2

# --- SOLVER CLASS ---
class MethaneDecompositionReactor:
    def __init__(self, config: ReactorConfig, isothermal: bool = True):
        self.cfg = config
        self.isothermal = isothermal
        
        C_total_in = config.inlet_pressure / (R_GAS * config.inlet_temperature) / 1000
        self.F_total_in = config.flow_rate * C_total_in
        self.F_CH4_in = config.y_CH4_in * self.F_total_in
        self.F_H2_in = config.y_H2_in * self.F_total_in
        self.F_N2_in = config.y_N2_in * self.F_total_in
    
    def _ode_system(self, z, y):
        F_CH4, F_H2, T, P = y
        cfg = self.cfg
        
        # Stability Clamps
        F_CH4 = max(F_CH4, 1e-30); F_H2 = max(F_H2, 0.0); T = max(T, 300.0); P = max(P, 1000.0)
        
        F_total = F_CH4 + F_H2 + self.F_N2_in
        y_CH4 = F_CH4 / F_total; y_H2 = F_H2 / F_total; y_N2 = self.F_N2_in / F_total
        
        rho = gas_density(T, P, y_CH4, y_H2, y_N2)
        mu = gas_viscosity(T, y_CH4, y_H2, y_N2)
        Q = F_total * 1000 * R_GAS * T / P
        u = Q / cfg.cross_section_area
        C_CH4 = F_CH4 / Q
        D_mol = diffusivity_CH4(T, P)
        D_eff = D_mol * cfg.particle_porosity / cfg.tortuosity
        k = arrhenius_rate_constant(T, cfg.pre_exponential, cfg.activation_energy, cfg.beta)
        phi = (cfg.particle_diameter / 6) * np.sqrt(k / D_eff) if D_eff > 0 else 0
        eta = effectiveness_factor(phi)
        r_bed = k * eta * C_CH4 * (1 - cfg.bed_porosity)
        A = cfg.cross_section_area
        
        dF_CH4_dz = -1.0 * r_bed * A
        dF_H2_dz = +2.0 * r_bed * A
        
        if self.isothermal: dT_dz = 0.0
        else:
            Cp_mix = heat_capacity_mix(T, y_CH4, y_H2, y_N2)
            F_total_mol = F_total * 1000
            Q_rxn = -cfg.heat_of_reaction * r_bed * A * 1000
            dT_dz = Q_rxn / (F_total_mol * Cp_mix + 1e-10)
            
        dP_dz = -ergun_pressure_drop(u, rho, mu, cfg.particle_diameter, cfg.bed_porosity)
        return np.array([dF_CH4_dz, dF_H2_dz, dT_dz, dP_dz])
        
    def solve(self, n_points=200):
        y0 = np.array([self.F_CH4_in, self.F_H2_in, self.cfg.inlet_temperature, self.cfg.inlet_pressure])
        solution = solve_ivp(
            self._ode_system, (0, self.cfg.bed_height), y0, 
            method='RK45', t_eval=np.linspace(0, self.cfg.bed_height, n_points),
            rtol=1e-8, atol=1e-12
        )
        z = solution.t
        F_CH4 = np.maximum(solution.y[0], 0); F_H2 = np.maximum(solution.y[1], 0)
        T = solution.y[2]; P = solution.y[3]
        F_total = F_CH4 + F_H2 + self.F_N2_in
        F_C = self.F_CH4_in - F_CH4
        
        return {
            'z': z, 'F_CH4': F_CH4, 'F_H2': F_H2, 'T': T, 'P': P,
            'y_CH4': F_CH4/F_total, 'y_H2': F_H2/F_total, 'y_N2': self.F_N2_in/F_total,
            'X_CH4': np.clip((self.F_CH4_in - F_CH4) / self.F_CH4_in, 0, 1),
            'm_dot_C_kg_s': F_C * MW_C * 1000, 'm_dot_H2_kg_s': F_H2 * MW_H2 * 1000,
            'V_dot_H2_Nm3_h': F_H2 * 1000 * R_GAS * 273.15 / 101325 * 3600
        }