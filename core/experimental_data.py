
"""
Anukaran AI - Experimental Data Storage
=======================================
Contains experimental data for model validation.
Methane decomposition: CH4 → C + 2H2
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional

# ============================================================================
# EXPERIMENTAL DATA FROM LITERATURE
# ============================================================================

# Time on Stream (TOS) in minutes
TOS_MINUTES = np.array([0, 30, 60, 90, 120, 150, 180, 210])

# Experimental data at different temperatures
# Format: {"temperature_C": {"H2_percent": [...], "CH4_percent": [...]}}

EXPERIMENTAL_DATA = {
    770: {
        "TOS_min": TOS_MINUTES,
        "H2_percent": np.array([11.41, 20.28, 16.1, 14.08, 12.81, 11.82, 11.12, 10.33]),
        "CH4_percent": np.array([24.87, 79.71, 83.89, 85.91, 87.18, 88.17, 88.87, 89.66]),
    },
    800: {
        "TOS_min": TOS_MINUTES,
        "H2_percent": np.array([24.13, 24.5, 20.51, 17.8, 16.74, 15.51, 14.44, 13.43]),
        "CH4_percent": np.array([65.0, 75.49, 79.48, 82.19, 83.25, 84.48, 85.55, 86.56]),
    },
    830: {
        "TOS_min": TOS_MINUTES,
        "H2_percent": np.array([40.69, 31.68, 25.23, 23.9, 22.29, 20.36, 19.8, 18.79]),
        "CH4_percent": np.array([44.64, 68.31, 74.76, 76.09, 77.7, 79.63, 80.19, 81.2]),
    },
}

# ============================================================================
# EXPERIMENTAL CONDITIONS (Estimated/Default if not provided)
# ============================================================================

@dataclass
class ExperimentalConditions:
    """Experimental setup parameters"""
    # Reactor geometry
    reactor_diameter_cm: float = 2.5      # cm
    bed_height_cm: float = 10.0           # cm
    
    # Catalyst properties
    particle_diameter_um: float = 500.0   # μm
    catalyst_density_kg_m3: float = 2000.0
    particle_porosity: float = 0.5
    tortuosity: float = 3.0
    bed_porosity: float = 0.4
    catalyst_mass_g: float = 20.0         # g
    
    # Operating conditions
    inlet_pressure_bar: float = 1.0       # bar
    flow_rate_mL_min: float = 50.0        # mL/min
    
    # Inlet composition
    y_CH4_in: float = 0.5                 # 50% CH4
    y_H2_in: float = 0.0                  # 0% H2
    y_N2_in: float = 0.5                  # 50% N2 (carrier)
    
    # Kinetics (to be fitted)
    pre_exponential: float = 1.0e6        # 1/s
    activation_energy_kJ_mol: float = 100.0  # kJ/mol
    beta: float = 0.0
    heat_of_reaction_kJ_mol: float = 74.87   # kJ/mol (endothermic)


# Default experimental conditions
DEFAULT_CONDITIONS = ExperimentalConditions()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_experimental_data(temperature_C: int) -> Optional[Dict]:
    """
    Get experimental data for a specific temperature.
    
    Args:
        temperature_C: Temperature in Celsius (770, 800, or 830)
    
    Returns:
        Dictionary with TOS_min, H2_percent, CH4_percent arrays
        or None if temperature not available
    """
    return EXPERIMENTAL_DATA.get(temperature_C, None)


def get_available_temperatures() -> List[int]:
    """Get list of temperatures with experimental data"""
    return list(EXPERIMENTAL_DATA.keys())


def get_initial_values(temperature_C: int) -> Optional[Dict]:
    """
    Get initial (TOS=0) experimental values for validation.
    
    Args:
        temperature_C: Temperature in Celsius
    
    Returns:
        Dictionary with H2_percent and CH4_percent at TOS=0
    """
    data = get_experimental_data(temperature_C)
    if data is None:
        return None
    
    return {
        "H2_percent": data["H2_percent"][0],
        "CH4_percent": data["CH4_percent"][0],
    }


def get_all_initial_values() -> Dict[int, Dict]:
    """Get initial values for all temperatures"""
    result = {}
    for temp in get_available_temperatures():
        result[temp] = get_initial_values(temp)
    return result


def interpolate_experimental(temperature_C: int, time_min: float) -> Optional[Dict]:
    """
    Interpolate experimental data at a specific time.
    
    Args:
        temperature_C: Temperature in Celsius
        time_min: Time on stream in minutes
    
    Returns:
        Dictionary with interpolated H2_percent and CH4_percent
    """
    data = get_experimental_data(temperature_C)
    if data is None:
        return None
    
    H2_interp = np.interp(time_min, data["TOS_min"], data["H2_percent"])
    CH4_interp = np.interp(time_min, data["TOS_min"], data["CH4_percent"])
    
    return {
        "H2_percent": H2_interp,
        "CH4_percent": CH4_interp,
    }


def calculate_conversion_from_composition(CH4_in_percent: float, CH4_out_percent: float) -> float:
    """
    Calculate CH4 conversion from inlet and outlet compositions.
    
    Note: This is approximate - actual conversion depends on molar flow changes.
    For dilute systems, this gives reasonable estimate.
    """
    if CH4_in_percent <= 0:
        return 0.0
    
    # Approximate conversion (valid for dilute/constant total moles)
    conversion = (CH4_in_percent - CH4_out_percent) / CH4_in_percent * 100
    return max(0.0, min(100.0, conversion))


def get_experimental_summary() -> str:
    """Get a text summary of experimental data"""
    summary = "=" * 60 + "\n"
    summary += "EXPERIMENTAL DATA SUMMARY\n"
    summary += "=" * 60 + "\n\n"
    
    summary += "Reaction: CH4 → C + 2H2\n"
    summary += f"Time on Stream: {TOS_MINUTES[0]} to {TOS_MINUTES[-1]} minutes\n"
    summary += f"Temperatures: {get_available_temperatures()} °C\n\n"
    
    summary += "-" * 60 + "\n"
    summary += f"{'Temp (°C)':<12}{'H2% (t=0)':<15}{'H2% (t=210)':<15}{'Decay %':<15}\n"
    summary += "-" * 60 + "\n"
    
    for temp in get_available_temperatures():
        data = get_experimental_data(temp)
        H2_initial = data["H2_percent"][0]
        H2_final = data["H2_percent"][-1]
        decay = (H2_initial - H2_final) / H2_initial * 100
        summary += f"{temp:<12}{H2_initial:<15.2f}{H2_final:<15.2f}{decay:<15.1f}\n"
    
    summary += "-" * 60 + "\n"
    
    return summary


# ============================================================================
# DATA VALIDATION
# ============================================================================

def validate_experimental_data() -> bool:
    """Check that experimental data is consistent"""
    for temp, data in EXPERIMENTAL_DATA.items():
        # Check array lengths match
        if len(data["TOS_min"]) != len(data["H2_percent"]):
            print(f"Error: TOS and H2 length mismatch at {temp}°C")
            return False
        if len(data["TOS_min"]) != len(data["CH4_percent"]):
            print(f"Error: TOS and CH4 length mismatch at {temp}°C")
            return False
        
        # Check compositions are reasonable (0-100%)
        if np.any(data["H2_percent"] < 0) or np.any(data["H2_percent"] > 100):
            print(f"Error: H2% out of range at {temp}°C")
            return False
        if np.any(data["CH4_percent"] < 0) or np.any(data["CH4_percent"] > 100):
            print(f"Error: CH4% out of range at {temp}°C")
            return False
    
    return True


# Run validation on import
if not validate_experimental_data():
    raise ValueError("Experimental data validation failed!")


# ============================================================================
# PRINT SUMMARY IF RUN DIRECTLY
# ============================================================================

if __name__ == "__main__":
    print(get_experimental_summary())
    
    print("\nInitial Values (TOS = 0):")
    for temp, values in get_all_initial_values().items():
        print(f"  {temp}°C: H2 = {values['H2_percent']:.2f}%, CH4 = {values['CH4_percent']:.2f}%")
