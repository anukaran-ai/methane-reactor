"""
Anukaran AI - Optimization Problem Templates
=============================================
Pre-defined optimization scenarios for methane decomposition reactor.
"""

OPTIMIZATION_TEMPLATES = {
    
    "max_h2": {
        "name": "🔥 Maximize H2 Production",
        "description": "Find operating conditions that produce maximum hydrogen yield",
        "use_case": "Research, feasibility studies, scale-up analysis",
        "objective": {
            "target": "V_dot_H2_Nm3_h",
            "direction": "maximize",
            "display_name": "H2 Production",
            "unit": "Nm³/h"
        },
        "variables": [
            {
                "key": "inlet_temperature",
                "label": "Temperature",
                "unit": "°C",
                "min": 700,
                "max": 1100,
                "default_optimize": True
            },
            {
                "key": "flow_rate",
                "label": "Flow Rate",
                "unit": "mL/min",
                "min": 50,
                "max": 500,
                "default_optimize": True
            },
            {
                "key": "particle_diameter",
                "label": "Particle Size",
                "unit": "μm",
                "min": 50,
                "max": 2000,
                "default_optimize": True
            },
        ],
        "constraints": [
            {
                "key": "pressure_drop",
                "label": "Max Pressure Drop",
                "type": "<=",
                "default_value": 50,
                "unit": "kPa"
            }
        ],
        "suggested_iterations": 25,
        "ai_hint": "High temperature increases reaction rate exponentially. Focus on 850-1000°C range first."
    },
    
    "max_conversion": {
        "name": "⚡ Maximize Conversion",
        "description": "Achieve highest CH4 to H2 conversion percentage",
        "use_case": "Catalyst evaluation, academic research, efficiency studies",
        "objective": {
            "target": "X_CH4",
            "direction": "maximize",
            "display_name": "CH4 Conversion",
            "unit": "%"
        },
        "variables": [
            {
                "key": "inlet_temperature",
                "label": "Temperature",
                "unit": "°C",
                "min": 600,
                "max": 1000,
                "default_optimize": True
            },
            {
                "key": "bed_height",
                "label": "Bed Height",
                "unit": "cm",
                "min": 5,
                "max": 100,
                "default_optimize": True
            },
            {
                "key": "flow_rate",
                "label": "Flow Rate",
                "unit": "mL/min",
                "min": 20,
                "max": 300,
                "default_optimize": True
            },
        ],
        "constraints": [
            {
                "key": "pressure_drop",
                "label": "Max Pressure Drop",
                "type": "<=",
                "default_value": 30,
                "unit": "kPa"
            }
        ],
        "suggested_iterations": 20,
        "ai_hint": "Longer residence time (low flow, tall bed) improves conversion. Watch pressure drop."
    },
    
    "min_energy": {
        "name": "💰 Minimize Energy Cost",
        "description": "Find lowest operating temperature that meets production target",
        "use_case": "Industrial optimization, cost reduction, energy efficiency",
        "objective": {
            "target": "inlet_temperature",
            "direction": "minimize",
            "display_name": "Operating Temperature",
            "unit": "°C"
        },
        "variables": [
            {
                "key": "inlet_temperature",
                "label": "Temperature",
                "unit": "°C",
                "min": 500,
                "max": 1000,
                "default_optimize": True
            },
            {
                "key": "bed_height",
                "label": "Bed Height",
                "unit": "cm",
                "min": 10,
                "max": 100,
                "default_optimize": True
            },
            {
                "key": "catalyst_mass",
                "label": "Catalyst Mass",
                "unit": "g",
                "min": 20,
                "max": 500,
                "default_optimize": True
            },
        ],
        "constraints": [
            {
                "key": "X_CH4",
                "label": "Min Conversion",
                "type": ">=",
                "default_value": 80,
                "unit": "%"
            },
            {
                "key": "V_dot_H2_Nm3_h",
                "label": "Min H2 Production",
                "type": ">=",
                "default_value": 0.0005,
                "unit": "Nm³/h"
            }
        ],
        "suggested_iterations": 30,
        "ai_hint": "Trade-off between temperature and catalyst amount. More catalyst allows lower temperature."
    },
    
    "sensitivity": {
        "name": "🎓 Sensitivity Analysis",
        "description": "Understand which parameters have the biggest impact on performance",
        "use_case": "Learning, parameter screening, experiment planning",
        "objective": {
            "target": "V_dot_H2_Nm3_h",
            "direction": "analyze",
            "display_name": "H2 Production",
            "unit": "Nm³/h"
        },
        "variables": [
            {
                "key": "inlet_temperature",
                "label": "Temperature",
                "unit": "°C",
                "min": 700,
                "max": 1000,
                "default_optimize": True
            },
            {
                "key": "flow_rate",
                "label": "Flow Rate",
                "unit": "mL/min",
                "min": 50,
                "max": 300,
                "default_optimize": True
            },
            {
                "key": "particle_diameter",
                "label": "Particle Size",
                "unit": "μm",
                "min": 100,
                "max": 1000,
                "default_optimize": True
            },
            {
                "key": "bed_height",
                "label": "Bed Height",
                "unit": "cm",
                "min": 10,
                "max": 50,
                "default_optimize": True
            },
        ],
        "constraints": [],
        "suggested_iterations": 40,
        "ai_hint": "This will run multiple simulations to rank parameter importance using variance-based sensitivity."
    },
}


def get_template(template_key: str) -> dict:
    """Get optimization template by key"""
    return OPTIMIZATION_TEMPLATES.get(template_key, OPTIMIZATION_TEMPLATES["max_h2"])


def get_template_names() -> dict:
    """Get dictionary of template key -> display name"""
    return {key: val["name"] for key, val in OPTIMIZATION_TEMPLATES.items()}


def get_variable_bounds(template_key: str) -> list:
    """Extract variable bounds as list of tuples for optimizer"""
    template = get_template(template_key)
    bounds = []
    for var in template["variables"]:
        if var.get("default_optimize", True):
            bounds.append((var["min"], var["max"]))
    return bounds


def get_variable_names(template_key: str) -> list:
    """Extract variable keys for optimizer"""
    template = get_template(template_key)
    return [var["key"] for var in template["variables"] if var.get("default_optimize", True)]