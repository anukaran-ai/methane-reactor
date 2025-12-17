# 🔬 Anukaran AI - Reactor Solver Documentation

## Methane Decomposition Packed Bed Reactor Model

**Reaction:** CH₄(g) → C(s) + 2H₂(g)

This document explains the mathematical model and numerical methods used in the Anukaran AI reactor simulator.

---

## 📋 Table of Contents

1. [Model Overview](#1-model-overview)
2. [Governing Equations](#2-governing-equations)
3. [Reaction Kinetics](#3-reaction-kinetics)
4. [Transport Properties](#4-transport-properties)
5. [Mass Transfer & Effectiveness Factor](#5-mass-transfer--effectiveness-factor)
6. [Pressure Drop](#6-pressure-drop)
7. [Numerical Solution](#7-numerical-solution)
8. [Unit Conversions](#8-unit-conversions)
9. [Solver Flow Diagram](#9-solver-flow-diagram)

---

## 1. Model Overview

### 1.1 Reactor Type
- **Configuration:** Cylindrical packed bed reactor
- **Flow:** Plug flow (1D axial)
- **Catalyst:** Spherical particles (Ni-based)
- **Operation:** Isothermal or Non-isothermal

### 1.2 Assumptions
- Steady-state operation
- Plug flow (no radial gradients)
- Ideal gas behavior
- First-order reaction in CH₄
- Uniform catalyst particle size
- No axial dispersion

### 1.3 Model Inputs

| Parameter | Symbol | Unit | Typical Range |
|-----------|--------|------|---------------|
| Reactor diameter | D | m | 0.01 - 1.0 |
| Bed height | L | m | 0.05 - 2.0 |
| Particle diameter | dₚ | m | 10⁻⁶ - 10⁻³ |
| Bed porosity | ε | - | 0.3 - 0.5 |
| Inlet temperature | T₀ | K | 773 - 1373 |
| Inlet pressure | P₀ | Pa | 10⁵ - 10⁶ |
| Flow rate | Q | m³/s | 10⁻⁸ - 10⁻⁴ |
| CH₄ mole fraction | y_CH₄ | - | 0.1 - 1.0 |

### 1.4 Model Outputs

| Output | Symbol | Unit |
|--------|--------|------|
| CH₄ conversion | X_CH₄ | % |
| H₂ production rate | V̇_H₂ | Nm³/h |
| Temperature profile | T(z) | K |
| Pressure profile | P(z) | Pa |
| Species mole fractions | yᵢ(z) | - |

---

## 2. Governing Equations

### 2.1 Species Molar Balance

For a packed bed reactor with plug flow, the molar balance for species *i* is:

$$\frac{dF_i}{dz} = \nu_i \cdot r_{bed} \cdot A_c$$

Where:
- $F_i$ = Molar flow rate of species *i* [kmol/s]
- $z$ = Axial position [m]
- $\nu_i$ = Stoichiometric coefficient
- $r_{bed}$ = Reaction rate per unit bed volume [kmol/(m³·s)]
- $A_c$ = Cross-sectional area [m²]

### 2.2 Stoichiometric Coefficients

For CH₄ → C + 2H₂:

| Species | νᵢ |
|---------|-----|
| CH₄ | -1 |
| C | +1 |
| H₂ | +2 |

### 2.3 Species Balance Equations

**Methane:**
$$\frac{dF_{CH_4}}{dz} = -r_{bed} \cdot A_c$$

**Hydrogen:**
$$\frac{dF_{H_2}}{dz} = +2 \cdot r_{bed} \cdot A_c$$

**Nitrogen (inert):**
$$\frac{dF_{N_2}}{dz} = 0$$

### 2.4 Energy Balance

For non-isothermal operation:

$$\frac{dT}{dz} = \frac{-\Delta H_{rxn} \cdot r_{bed} \cdot A_c}{\sum F_i \cdot C_{p,i}}$$

Where:
- $\Delta H_{rxn}$ = Heat of reaction [J/kmol] (positive = endothermic)
- $C_{p,i}$ = Molar heat capacity [J/(mol·K)]

For **isothermal** operation:
$$\frac{dT}{dz} = 0$$

### 2.5 Pressure Drop (Momentum Balance)

$$\frac{dP}{dz} = -f(u, \rho, \mu, d_p, \varepsilon)$$

See [Section 6](#6-pressure-drop) for the Ergun equation.

---

## 3. Reaction Kinetics

### 3.1 Arrhenius Rate Law

The intrinsic reaction rate constant follows the Arrhenius equation:

$$k(T) = A \cdot T^\beta \cdot \exp\left(-\frac{E_a}{R \cdot T}\right)$$

Where:
- $A$ = Pre-exponential factor [1/s]
- $\beta$ = Temperature exponent [-]
- $E_a$ = Activation energy [J/mol]
- $R$ = Universal gas constant = 8.314 J/(mol·K)
- $T$ = Temperature [K]

### 3.2 Typical Kinetic Parameters

| Parameter | Symbol | Typical Value | Range |
|-----------|--------|---------------|-------|
| Pre-exponential | A | 10⁶ 1/s | 10³ - 10¹⁰ |
| Activation energy | Eₐ | 100 kJ/mol | 60 - 150 |
| Temperature exponent | β | 0 | -1 to 1 |
| Heat of reaction | ΔH | +74.87 kJ/mol | (endothermic) |

### 3.3 Reaction Rate Expression

First-order rate in CH₄ concentration:

$$r_{intrinsic} = k(T) \cdot C_{CH_4}$$

Where $C_{CH_4}$ is the molar concentration [kmol/m³]:

$$C_{CH_4} = \frac{F_{CH_4}}{Q} = \frac{F_{CH_4} \cdot P}{F_{total} \cdot R \cdot T}$$

### 3.4 Bed Reaction Rate

Accounting for effectiveness factor and bed porosity:

$$r_{bed} = k(T) \cdot \eta \cdot C_{CH_4} \cdot (1 - \varepsilon)$$

Where:
- $\eta$ = Effectiveness factor (internal diffusion limitation)
- $\varepsilon$ = Bed porosity (void fraction)

---

## 4. Transport Properties

### 4.1 Gas Mixture Density

Using ideal gas law:

$$\rho = \frac{P \cdot M_{mix}}{R \cdot T}$$

Where the mixture molecular weight is:

$$M_{mix} = \sum y_i \cdot M_i = y_{CH_4} \cdot M_{CH_4} + y_{H_2} \cdot M_{H_2} + y_{N_2} \cdot M_{N_2}$$

| Species | Molecular Weight (kg/mol) |
|---------|---------------------------|
| CH₄ | 0.01604 |
| H₂ | 0.002016 |
| C | 0.01201 |
| N₂ | 0.02801 |

### 4.2 Gas Viscosity

Temperature-dependent viscosity for each species:

$$\mu_{CH_4} = 1.02 \times 10^{-5} \cdot \left(\frac{T}{300}\right)^{0.87}$$

$$\mu_{H_2} = 8.76 \times 10^{-6} \cdot \left(\frac{T}{300}\right)^{0.68}$$

$$\mu_{N_2} = 1.78 \times 10^{-5} \cdot \left(\frac{T}{300}\right)^{0.67}$$

Mixture viscosity (linear mixing rule):

$$\mu_{mix} = \sum y_i \cdot \mu_i$$

### 4.3 Molecular Diffusivity

CH₄ diffusivity in the gas mixture (Fuller correlation simplified):

$$D_{CH_4} = 1.87 \times 10^{-5} \cdot \left(\frac{T}{300}\right)^{1.75} \cdot \frac{101325}{P}$$

Units: [m²/s]

### 4.4 Effective Diffusivity

Inside porous catalyst particles:

$$D_{eff} = \frac{D_{mol} \cdot \varepsilon_p}{\tau}$$

Where:
- $\varepsilon_p$ = Particle porosity (typically 0.3 - 0.6)
- $\tau$ = Tortuosity factor (typically 2 - 4)

### 4.5 Heat Capacity

Molar heat capacity [J/(mol·K)] as function of temperature:

$$C_{p,CH_4} = 35.69 + 0.0275 \cdot T$$

$$C_{p,H_2} = 28.84 + 0.00192 \cdot T$$

$$C_{p,N_2} = 29.12 + 0.00293 \cdot T$$

Mixture heat capacity:

$$C_{p,mix} = \sum y_i \cdot C_{p,i}$$

---

## 5. Mass Transfer & Effectiveness Factor

### 5.1 Thiele Modulus

The Thiele modulus represents the ratio of reaction rate to diffusion rate:

$$\phi = \frac{d_p}{6} \cdot \sqrt{\frac{k}{D_{eff}}}$$

Where:
- $d_p$ = Particle diameter [m]
- $k$ = Rate constant [1/s]
- $D_{eff}$ = Effective diffusivity [m²/s]

The factor $d_p/6$ is the characteristic length for a sphere ($V_p/A_p = d_p/6$).

### 5.2 Effectiveness Factor

For a first-order reaction in a spherical catalyst particle:

$$\eta = \frac{3}{\phi} \cdot \left(\frac{1}{\tanh(\phi)} - \frac{1}{\phi}\right)$$

**Limiting cases:**

| Condition | φ | η | Regime |
|-----------|---|---|--------|
| Small particles, slow reaction | φ < 0.1 | η ≈ 1.0 | Kinetic control |
| Large particles, fast reaction | φ > 100 | η ≈ 3/φ | Diffusion control |
| Intermediate | 0.1 < φ < 100 | Use formula | Mixed control |

### 5.3 Physical Interpretation
```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   η = 1.0 (Kinetic Control)                                │
│   • Reaction is slow compared to diffusion                 │
│   • Entire catalyst particle is utilized                   │
│   • Small particles, low temperature                       │
│                                                             │
│   η < 1.0 (Diffusion Limitation)                           │
│   • Reaction is fast compared to diffusion                 │
│   • Only outer shell of particle reacts                    │
│   • Large particles, high temperature                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Pressure Drop

### 6.1 Ergun Equation

Pressure drop in a packed bed:

$$-\frac{dP}{dz} = \frac{150 \mu (1-\varepsilon)^2}{d_p^2 \varepsilon^3} u + \frac{1.75 \rho (1-\varepsilon)}{d_p \varepsilon^3} u^2$$

Where:
- First term = Viscous losses (laminar, Blake-Kozeny)
- Second term = Inertial losses (turbulent, Burke-Plummer)

### 6.2 Variables

| Symbol | Description | Unit |
|--------|-------------|------|
| P | Pressure | Pa |
| z | Axial position | m |
| μ | Gas viscosity | Pa·s |
| ρ | Gas density | kg/m³ |
| ε | Bed porosity | - |
| dₚ | Particle diameter | m |
| u | Superficial velocity | m/s |

### 6.3 Superficial Velocity

$$u = \frac{Q}{A_c} = \frac{F_{total} \cdot R \cdot T}{P \cdot A_c}$$

Where:
- $Q$ = Volumetric flow rate [m³/s]
- $A_c$ = Cross-sectional area = $\pi D^2 / 4$ [m²]

### 6.4 Pressure Drop Considerations

| Factor | Effect on ΔP |
|--------|--------------|
| ↓ Particle size | ↑↑ Pressure drop (∝ 1/dₚ²) |
| ↑ Flow rate | ↑ Pressure drop |
| ↓ Bed porosity | ↑ Pressure drop |
| ↑ Bed height | ↑ Pressure drop |
| ↑ Temperature | ↓ Density, ↑ Viscosity (mixed effect) |

---

## 7. Numerical Solution

### 7.1 System of ODEs

The complete model consists of 4 coupled ordinary differential equations:

$$\frac{d}{dz}\begin{bmatrix} F_{CH_4} \\ F_{H_2} \\ T \\ P \end{bmatrix} = \begin{bmatrix} -r_{bed} \cdot A_c \\ +2 \cdot r_{bed} \cdot A_c \\ \frac{-\Delta H_{rxn} \cdot r_{bed} \cdot A_c}{\sum F_i C_{p,i}} \\ -\left(\frac{150\mu(1-\varepsilon)^2}{d_p^2 \varepsilon^3}u + \frac{1.75\rho(1-\varepsilon)}{d_p \varepsilon^3}u^2\right) \end{bmatrix}$$

### 7.2 Initial Conditions (z = 0)

$$\begin{bmatrix} F_{CH_4}(0) \\ F_{H_2}(0) \\ T(0) \\ P(0) \end{bmatrix} = \begin{bmatrix} F_{CH_4,in} \\ F_{H_2,in} \\ T_{in} \\ P_{in} \end{bmatrix}$$

### 7.3 Solver Method

**Algorithm:** Runge-Kutta 4th/5th order (RK45)

**Implementation:** `scipy.integrate.solve_ivp`
```python
solution = solve_ivp(
    ode_system,           # Function defining dy/dz
    (0, L),               # Integration span [0, bed_height]
    y0,                   # Initial conditions
    method='RK45',        # Runge-Kutta 4(5)
    t_eval=z_points,      # Output points
    rtol=1e-8,            # Relative tolerance
    atol=1e-12            # Absolute tolerance
)
```

### 7.4 Numerical Stability

**Stability clamps** prevent numerical issues:
```python
F_CH4 = max(F_CH4, 1e-30)  # Prevent division by zero
F_H2 = max(F_H2, 0.0)       # Non-negative flow
T = max(T, 300.0)           # Minimum temperature
P = max(P, 1000.0)          # Minimum pressure
```

### 7.5 Solution Flow
```
┌─────────────────────────────────────────────────────────────┐
│                    SOLVER ALGORITHM                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  START                                                      │
│    │                                                        │
│    ▼                                                        │
│  ┌─────────────────────────────────────┐                   │
│  │ 1. SET INITIAL CONDITIONS           │                   │
│  │    F_CH4(0), F_H2(0), T(0), P(0)   │                   │
│  └─────────────────────────────────────┘                   │
│    │                                                        │
│    ▼                                                        │
│  ┌─────────────────────────────────────┐                   │
│  │ 2. FOR each z step:                 │◄──────┐           │
│  │    a. Calculate properties          │       │           │
│  │       - ρ, μ, D_eff, C_p           │       │           │
│  │    b. Calculate rate constant       │       │           │
│  │       - k = A·T^β·exp(-Ea/RT)      │       │           │
│  │    c. Calculate Thiele modulus      │       │           │
│  │       - φ = (dp/6)·√(k/D_eff)      │       │           │
│  │    d. Calculate effectiveness       │       │           │
│  │       - η = f(φ)                    │       │           │
│  │    e. Calculate reaction rate       │       │           │
│  │       - r_bed = k·η·C_CH4·(1-ε)    │       │           │
│  │    f. Calculate derivatives         │       │           │
│  │       - dF/dz, dT/dz, dP/dz        │       │           │
│  │    g. RK45 step                     │       │           │
│  └─────────────────────────────────────┘       │           │
│    │                                           │           │
│    ▼                                           │           │
│  ┌─────────────────────────────────────┐       │           │
│  │ 3. z < L ?                          │───YES─┘           │
│  └─────────────────────────────────────┘                   │
│    │ NO                                                     │
│    ▼                                                        │
│  ┌─────────────────────────────────────┐                   │
│  │ 4. CALCULATE OUTPUTS                │                   │
│  │    - Conversion X = (F_in-F_out)/F_in                   │
│  │    - H2 yield, Carbon production    │                   │
│  │    - Profiles: T(z), P(z), y_i(z)  │                   │
│  └─────────────────────────────────────┘                   │
│    │                                                        │
│    ▼                                                        │
│  END                                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. Unit Conversions

### 8.1 Input Conversions (User → Solver)

| User Input | User Unit | Solver Unit | Conversion |
|------------|-----------|-------------|------------|
| Temperature | °C | K | T_K = T_C + 273.15 |
| Pressure | bar | Pa | P_Pa = P_bar × 10⁵ |
| Flow rate | mL/min | m³/s | Q = Q_mL / 60 / 10⁶ |
| Particle diameter | μm | m | d = d_μm × 10⁻⁶ |
| Bed height | cm | m | L = L_cm / 100 |
| Reactor diameter | cm | m | D = D_cm / 100 |
| Catalyst mass | g | kg | m = m_g / 1000 |
| Activation energy | kJ/mol | J/mol | Ea = Ea_kJ × 1000 |
| Heat of reaction | kJ/mol | J/kmol | ΔH = ΔH_kJ × 10⁶ |

### 8.2 Output Conversions (Solver → User)

| Solver Output | Solver Unit | User Unit | Conversion |
|---------------|-------------|-----------|------------|
| H₂ flow rate | kmol/s | Nm³/h | V̇ = F × 22.414 × 3600 |
| Mass flow | kmol/s | kg/h | ṁ = F × M × 3600 |
| Temperature | K | °C | T_C = T_K - 273.15 |
| Pressure | Pa | bar | P_bar = P_Pa / 10⁵ |

### 8.3 Standard Conditions

For Nm³ (Normal cubic meters):
- Temperature: 273.15 K (0°C)
- Pressure: 101325 Pa (1 atm)

$$V_{Nm^3/h} = F_{kmol/s} \times \frac{R \times 273.15}{101325} \times 3600$$

---

## 9. Solver Flow Diagram

### 9.1 Complete Data Flow
```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │  Geometry   │    │  Catalyst   │    │ Conditions  │             │
│  │  D, L       │    │  dp, ε, ρ   │    │  T, P, Q    │             │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘             │
└─────────┼──────────────────┼──────────────────┼─────────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      UNIT CONVERSION                                │
│         cm→m, μm→m, °C→K, bar→Pa, mL/min→m³/s                      │
└─────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      ReactorConfig                                  │
│                   (dataclass container)                             │
└─────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│               MethaneDecompositionReactor                           │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ __init__():                                                    │ │
│  │   • Calculate inlet molar flows F_CH4, F_H2, F_N2             │ │
│  │   • C_total = P / (R·T)                                       │ │
│  │   • F_i = y_i · Q · C_total                                   │ │
│  └───────────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ _ode_system(z, y):                                            │ │
│  │   • Extract state: F_CH4, F_H2, T, P                          │ │
│  │   • Calculate: ρ, μ, u, C_CH4                                 │ │
│  │   • Calculate: D_eff, k(T), φ, η                              │ │
│  │   • Calculate: r_bed                                          │ │
│  │   • Return: dF_CH4/dz, dF_H2/dz, dT/dz, dP/dz                │ │
│  └───────────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ solve():                                                       │ │
│  │   • Call scipy.integrate.solve_ivp                            │ │
│  │   • Post-process results                                      │ │
│  │   • Return dictionary with all outputs                        │ │
│  └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        RESULTS                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │  Profiles   │  │   Metrics   │  │    Plots    │                 │
│  │ z, T, P, y  │  │ X, V̇_H2, ΔP │  │  Charts     │                 │
│  └─────────────┘  └─────────────┘  └─────────────┘                 │
└─────────────────────────────────────────────────────────────────────┘
```

### 9.2 Calculation Sequence at Each z Step
```
┌─────────────────────────────────────────────────────────────────────┐
│                  CALCULATION SEQUENCE                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  INPUT STATE: [F_CH4, F_H2, T, P]                                  │
│       │                                                             │
│       ▼                                                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ STEP 1: Mole Fractions                                      │   │
│  │   F_total = F_CH4 + F_H2 + F_N2                            │   │
│  │   y_i = F_i / F_total                                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│       │                                                             │
│       ▼                                                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ STEP 2: Transport Properties                                │   │
│  │   ρ = P·M_mix / (R·T)                                       │   │
│  │   μ = Σ(y_i · μ_i)                                          │   │
│  │   D_eff = D_mol · ε_p / τ                                   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│       │                                                             │
│       ▼                                                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ STEP 3: Velocity & Concentration                            │   │
│  │   Q = F_total · R · T / P                                   │   │
│  │   u = Q / A_c                                               │   │
│  │   C_CH4 = F_CH4 / Q                                         │   │
│  └─────────────────────────────────────────────────────────────┘   │
│       │                                                             │
│       ▼                                                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ STEP 4: Kinetics                                            │   │
│  │   k = A · T^β · exp(-Ea/RT)                                 │   │
│  │   φ = (dp/6) · √(k/D_eff)                                   │   │
│  │   η = (3/φ) · [coth(φ) - 1/φ]                               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│       │                                                             │
│       ▼                                                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ STEP 5: Reaction Rate                                       │   │
│  │   r_bed = k · η · C_CH4 · (1 - ε)                           │   │
│  └─────────────────────────────────────────────────────────────┘   │
│       │                                                             │
│       ▼                                                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ STEP 6: Derivatives                                         │   │
│  │   dF_CH4/dz = -r_bed · A_c                                  │   │
│  │   dF_H2/dz  = +2·r_bed · A_c                                │   │
│  │   dT/dz     = -ΔH·r_bed·A_c / (Σ F_i·Cp_i)  [non-iso]     │   │
│  │   dP/dz     = -Ergun(u, ρ, μ, dp, ε)                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│       │                                                             │
│       ▼                                                             │
│  OUTPUT: [dF_CH4/dz, dF_H2/dz, dT/dz, dP/dz]                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📚 References

1. Fogler, H.S. "Elements of Chemical Reaction Engineering" 5th Ed.
2. Levenspiel, O. "Chemical Reaction Engineering" 3rd Ed.
3. Bird, Stewart, Lightfoot. "Transport Phenomena" 2nd Ed.
4. Ergun, S. "Fluid Flow Through Packed Columns" Chem. Eng. Prog. 48(2), 1952

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024 | Initial documentation |

---

*Documentation by Anukaran AI*
