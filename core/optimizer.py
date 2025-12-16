"""
Anukaran AI - Bayesian Optimizer
================================
Optimization engine using scikit-optimize.
Pure Python - No Streamlit imports.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Callable, List, Dict, Optional, Tuple
import warnings

warnings.filterwarnings('ignore')


@dataclass
class OptimizationResult:
    """Container for optimization results"""
    best_params: Dict[str, float]
    best_value: float
    all_trials: List[Dict]
    convergence: List[float]
    best_so_far: List[float]
    variable_names: List[str]
    success: bool = True
    message: str = ""


@dataclass
class OptimizationConfig:
    """Configuration for optimization run"""
    variable_names: List[str]
    bounds: List[Tuple[float, float]]
    n_iterations: int = 25
    n_initial_points: int = 5
    random_state: int = 42
    maximize: bool = True
    
    def validate(self) -> Tuple[bool, str]:
        """Validate configuration"""
        if len(self.variable_names) != len(self.bounds):
            return False, "Variable names and bounds must have same length"
        if self.n_iterations < 5:
            return False, "Need at least 5 iterations"
        if self.n_initial_points >= self.n_iterations:
            return False, "Initial points must be less than total iterations"
        return True, "OK"


class BayesianOptimizer:
    """
    Bayesian Optimization using Gaussian Process surrogate model.
    
    Uses Expected Improvement (EI) acquisition function to balance
    exploration vs exploitation.
    """
    
    def __init__(self, config: OptimizationConfig):
        """
        Initialize optimizer.
        
        Args:
            config: OptimizationConfig with variable names, bounds, etc.
        """
        self.config = config
        self.history: List[Dict] = []
        self.best_value = float('-inf') if config.maximize else float('inf')
        self.best_params = None
        self.convergence = []
        self.best_so_far = []
        
    def optimize(
        self,
        objective_fn: Callable[[Dict[str, float]], float],
        callback: Optional[Callable[[int, Dict, float], None]] = None
    ) -> OptimizationResult:
        """
        Run Bayesian optimization.
        
        Args:
            objective_fn: Function that takes dict of params, returns objective value
            callback: Optional function called after each iteration
                      callback(iteration, params_dict, objective_value)
        
        Returns:
            OptimizationResult with best parameters and history
        """
        try:
            from skopt import gp_minimize
            from skopt.space import Real
            use_skopt = True
        except ImportError:
            use_skopt = False
        
        if use_skopt:
            return self._optimize_with_skopt(objective_fn, callback)
        else:
            return self._optimize_simple(objective_fn, callback)
    
    def _optimize_with_skopt(
        self,
        objective_fn: Callable,
        callback: Optional[Callable]
    ) -> OptimizationResult:
        """Optimization using scikit-optimize"""
        from skopt import gp_minimize
        from skopt.space import Real
        
        # Build search space
        space = [
            Real(low, high, name=name)
            for name, (low, high) in zip(self.config.variable_names, self.config.bounds)
        ]
        
        iteration_count = [0]  # Mutable counter for closure
        
        def wrapped_objective(params_list):
            """Convert list to dict and evaluate"""
            params_dict = {
                name: val 
                for name, val in zip(self.config.variable_names, params_list)
            }
            
            # Evaluate objective
            value = objective_fn(params_dict)
            
            # Store in history
            self.history.append({
                'params': params_dict.copy(),
                'value': value
            })
            self.convergence.append(value)
            
            # Update best
            if self.config.maximize:
                if value > self.best_value:
                    self.best_value = value
                    self.best_params = params_dict.copy()
            else:
                if value < self.best_value:
                    self.best_value = value
                    self.best_params = params_dict.copy()
            
            self.best_so_far.append(self.best_value)
            
            # Callback for progress updates
            iteration_count[0] += 1
            if callback:
                callback(iteration_count[0], params_dict, value)
            
            # Return negative for maximization (skopt minimizes)
            return -value if self.config.maximize else value
        
        # Run optimization
        result = gp_minimize(
            wrapped_objective,
            space,
            n_calls=self.config.n_iterations,
            n_initial_points=self.config.n_initial_points,
            random_state=self.config.random_state,
            acq_func='EI',  # Expected Improvement
            verbose=False
        )
        
        return OptimizationResult(
            best_params=self.best_params,
            best_value=self.best_value,
            all_trials=self.history,
            convergence=self.convergence,
            best_so_far=self.best_so_far,
            variable_names=self.config.variable_names,
            success=True,
            message=f"Optimization completed: {len(self.history)} trials"
        )
    
    def _optimize_simple(
        self,
        objective_fn: Callable,
        callback: Optional[Callable]
    ) -> OptimizationResult:
        """Simple random search fallback if skopt not available"""
        
        np.random.seed(self.config.random_state)
        
        for i in range(self.config.n_iterations):
            # Generate random parameters within bounds
            params_dict = {}
            for name, (low, high) in zip(self.config.variable_names, self.config.bounds):
                params_dict[name] = np.random.uniform(low, high)
            
            # Evaluate
            value = objective_fn(params_dict)
            
            # Store
            self.history.append({
                'params': params_dict.copy(),
                'value': value
            })
            self.convergence.append(value)
            
            # Update best
            if self.config.maximize:
                if value > self.best_value:
                    self.best_value = value
                    self.best_params = params_dict.copy()
            else:
                if value < self.best_value:
                    self.best_value = value
                    self.best_params = params_dict.copy()
            
            self.best_so_far.append(self.best_value)
            
            if callback:
                callback(i + 1, params_dict, value)
        
        return OptimizationResult(
            best_params=self.best_params,
            best_value=self.best_value,
            all_trials=self.history,
            convergence=self.convergence,
            best_so_far=self.best_so_far,
            variable_names=self.config.variable_names,
            success=True,
            message="Optimization completed (random search fallback)"
        )


class SensitivityAnalyzer:
    """
    Sensitivity analysis using variance-based methods.
    Identifies which parameters have the most impact on the objective.
    """
    
    def __init__(self, variable_names: List[str], bounds: List[Tuple[float, float]]):
        self.variable_names = variable_names
        self.bounds = bounds
    
    def analyze(
        self,
        objective_fn: Callable[[Dict[str, float]], float],
        n_samples: int = 50,
        callback: Optional[Callable] = None
    ) -> Dict[str, float]:
        """
        Run sensitivity analysis.
        
        Args:
            objective_fn: Objective function
            n_samples: Number of samples per parameter
            callback: Progress callback
        
        Returns:
            Dictionary of parameter_name -> importance_score (0-1)
        """
        
        # Generate base point (middle of bounds)
        base_params = {
            name: (low + high) / 2
            for name, (low, high) in zip(self.variable_names, self.bounds)
        }
        
        importance_scores = {}
        total_iterations = len(self.variable_names) * n_samples
        current_iter = 0
        
        for var_idx, (var_name, (low, high)) in enumerate(zip(self.variable_names, self.bounds)):
            values = []
            
            # Sweep this parameter while holding others at base
            test_values = np.linspace(low, high, n_samples)
            
            for test_val in test_values:
                params = base_params.copy()
                params[var_name] = test_val
                
                result = objective_fn(params)
                values.append(result)
                
                current_iter += 1
                if callback:
                    callback(current_iter, total_iterations, var_name, test_val, result)
            
            # Calculate variance for this parameter
            importance_scores[var_name] = np.std(values)
        
        # Normalize to sum to 1
        total = sum(importance_scores.values())
        if total > 0:
            importance_scores = {k: v/total for k, v in importance_scores.items()}
        
        return importance_scores


def create_objective_function(reactor_class, base_config: dict, variable_names: List[str], target: str):
    """
    Factory function to create objective function for optimizer.
    
    Args:
        reactor_class: MethaneDecompositionReactor class
        base_config: Base configuration dictionary
        variable_names: List of parameters to optimize
        target: Output variable to optimize (e.g., 'V_dot_H2_Nm3_h')
    
    Returns:
        Callable that takes param dict and returns objective value
    """
    
    def objective(params: Dict[str, float]) -> float:
        # Start with base config
        config_dict = base_config.copy()
        
        # Update with optimization parameters (handle unit conversions)
        for name, value in params.items():
            if name == 'inlet_temperature':
                config_dict['inlet_temperature'] = value + 273.15  # °C to K
            elif name == 'flow_rate':
                config_dict['flow_rate'] = value / 60 / 1e6  # mL/min to m³/s
            elif name == 'particle_diameter':
                config_dict['particle_diameter'] = value * 1e-6  # μm to m
            elif name == 'bed_height':
                config_dict['bed_height'] = value / 100  # cm to m
            elif name == 'catalyst_mass':
                config_dict['catalyst_mass'] = value / 1000  # g to kg
            elif name == 'inlet_pressure':
                config_dict['inlet_pressure'] = value * 1e5  # bar to Pa
            else:
                config_dict[name] = value
        
        try:
            # Import here to avoid circular imports
            from reactor_model import ReactorConfig, MethaneDecompositionReactor
            
            # Create reactor config
            reactor_config = ReactorConfig(**config_dict)
            
            # Run simulation
            reactor = MethaneDecompositionReactor(reactor_config, isothermal=True)
            results = reactor.solve()
            
            # Get target value
            if target == 'X_CH4':
                return float(results['X_CH4'][-1] * 100)  # Convert to percentage
            elif target == 'V_dot_H2_Nm3_h':
                return float(results['V_dot_H2_Nm3_h'][-1])
            elif target == 'pressure_drop':
                return float((config_dict['inlet_pressure'] - results['P'][-1]) / 1000)  # kPa
            elif target == 'inlet_temperature':
                return float(params.get('inlet_temperature', 900))
            else:
                return float(results.get(target, [0])[-1])
                
        except Exception as e:
            # Return bad value on error
            return 0.0
    
    return objective


def get_base_config_from_session(session_state) -> dict:
    """
    Extract base configuration from Streamlit session state.
    
    Args:
        session_state: Streamlit session state object
    
    Returns:
        Dictionary with reactor configuration
    """
    return {
        'diameter': session_state.get('d_reac', 5.0) / 100,
        'bed_height': session_state.get('h_bed', 20.0) / 100,
        'particle_diameter': session_state.get('d_part', 500.0) * 1e-6,
        'catalyst_density': session_state.get('rho_cat', 2000.0),
        'particle_porosity': session_state.get('eps_part', 0.5),
        'tortuosity': session_state.get('tau', 3.0),
        'bed_porosity': session_state.get('eps_bed', 0.4),
        'catalyst_mass': session_state.get('mass_cat', 50.0) / 1000,
        'inlet_temperature': session_state.get('t_in', 900.0) + 273.15,
        'inlet_pressure': session_state.get('p_in', 1.0) * 1e5,
        'flow_rate': session_state.get('flow', 100.0) / 60 / 1e6,
        'y_CH4_in': session_state.get('y_ch4', 0.2),
        'y_H2_in': session_state.get('y_h2', 0.0),
        'y_N2_in': session_state.get('y_n2', 0.8),
        'pre_exponential': session_state.get('pre_exp', 1e6),
        'activation_energy': session_state.get('act_e', 100.0) * 1000,
        'beta': session_state.get('beta', 0.0),
        'heat_of_reaction': session_state.get('dh', 74.87) * 1e6,
    }