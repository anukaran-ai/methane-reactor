"""
Anukaran AI - Plotting Utilities
================================
Shared plotting functions for optimization results.
Pure Python/Matplotlib - No Streamlit imports.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Optional


def create_convergence_plot(convergence_history: List[float], best_history: List[float] = None):
    """
    Create optimization convergence plot.
    
    Args:
        convergence_history: List of objective values at each iteration
        best_history: List of best-so-far values (optional)
    
    Returns:
        matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    
    iterations = range(1, len(convergence_history) + 1)
    
    # Plot all evaluations
    ax.scatter(iterations, convergence_history, alpha=0.5, s=30, c='blue', label='Each Trial')
    
    # Plot best-so-far line
    if best_history is None:
        best_history = []
        current_best = float('-inf')
        for val in convergence_history:
            current_best = max(current_best, val)
            best_history.append(current_best)
    
    ax.plot(iterations, best_history, 'r-', linewidth=2, label='Best So Far')
    
    ax.set_xlabel('Iteration', fontsize=11)
    ax.set_ylabel('Objective Value', fontsize=11)
    ax.set_title('Optimization Convergence', fontsize=12, fontweight='bold')
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def create_parameter_importance_plot(importance_scores: Dict[str, float]):
    """
    Create horizontal bar chart of parameter importance.
    
    Args:
        importance_scores: Dict of parameter_name -> importance_score
    
    Returns:
        matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    
    # Sort by importance
    sorted_params = sorted(importance_scores.items(), key=lambda x: x[1], reverse=True)
    names = [p[0] for p in sorted_params]
    scores = [p[1] for p in sorted_params]
    
    # Color gradient based on importance
    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(scores)))[::-1]
    
    bars = ax.barh(names, scores, color=colors, edgecolor='black', linewidth=0.5)
    
    # Add value labels
    for bar, score in zip(bars, scores):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                f'{score:.1%}', va='center', fontsize=10)
    
    ax.set_xlabel('Relative Importance', fontsize=11)
    ax.set_title('Parameter Sensitivity Analysis', fontsize=12, fontweight='bold')
    ax.set_xlim(0, max(scores) * 1.2)
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    return fig


def create_optimization_history_plot(trials: List[Dict], objective_name: str = "Objective"):
    """
    Create detailed optimization history plot with parameters.
    
    Args:
        trials: List of trial dictionaries with 'params' and 'value' keys
        objective_name: Name of objective for labeling
    
    Returns:
        matplotlib Figure
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    
    # Left plot: Objective over iterations
    iterations = range(1, len(trials) + 1)
    values = [t['value'] for t in trials]
    
    # Calculate best-so-far
    best_so_far = []
    current_best = float('-inf')
    for val in values:
        current_best = max(current_best, val)
        best_so_far.append(current_best)
    
    axes[0].scatter(iterations, values, alpha=0.6, s=40, c='steelblue', label='Trials')
    axes[0].plot(iterations, best_so_far, 'r-', linewidth=2, label='Best')
    axes[0].set_xlabel('Iteration')
    axes[0].set_ylabel(objective_name)
    axes[0].set_title('Optimization Progress')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Right plot: Best value highlight
    best_idx = np.argmax(values)
    best_trial = trials[best_idx]
    
    param_names = list(best_trial['params'].keys())
    param_values = list(best_trial['params'].values())
    
    # Normalize for visualization
    colors = ['#2ecc71' if i == best_idx else '#3498db' for i in range(len(values))]
    
    axes[1].bar(param_names, param_values, color='#3498db', edgecolor='black')
    axes[1].set_ylabel('Parameter Value')
    axes[1].set_title(f'Best Parameters (Trial #{best_idx + 1})')
    axes[1].tick_params(axis='x', rotation=45)
    axes[1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    return fig


def create_contour_plot(
    x_values: np.ndarray,
    y_values: np.ndarray,
    z_values: np.ndarray,
    x_label: str,
    y_label: str,
    z_label: str,
    best_point: tuple = None
):
    """
    Create 2D contour plot for parameter exploration.
    
    Args:
        x_values, y_values: 1D arrays of parameter values
        z_values: 2D array of objective values
        x_label, y_label, z_label: Axis labels
        best_point: Optional (x, y) tuple to mark optimal point
    
    Returns:
        matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    
    X, Y = np.meshgrid(x_values, y_values)
    
    contour = ax.contourf(X, Y, z_values, levels=20, cmap='viridis')
    ax.contour(X, Y, z_values, levels=10, colors='white', linewidths=0.5, alpha=0.5)
    
    cbar = plt.colorbar(contour, ax=ax, label=z_label)
    
    if best_point:
        ax.scatter(best_point[0], best_point[1], c='red', s=200, marker='*',
                   edgecolors='white', linewidths=2, label='Optimum', zorder=5)
        ax.legend()
    
    ax.set_xlabel(x_label, fontsize=11)
    ax.set_ylabel(y_label, fontsize=11)
    ax.set_title(f'{z_label} Response Surface', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    return fig


def create_trials_table_data(trials: List[Dict], variable_names: List[str]) -> List[Dict]:
    """
    Format trials data for display in a table.
    
    Args:
        trials: List of trial dictionaries
        variable_names: List of parameter names
    
    Returns:
        List of formatted dictionaries for table display
    """
    table_data = []
    
    best_value = max(t['value'] for t in trials) if trials else 0
    
    for i, trial in enumerate(trials):
        row = {
            '#': i + 1,
            'Objective': f"{trial['value']:.6f}",
            'Best?': '⭐' if trial['value'] == best_value else ''
        }
        
        # Add parameters
        for var_name in variable_names:
            if var_name in trial['params']:
                row[var_name] = f"{trial['params'][var_name]:.2f}"
        
        table_data.append(row)
    
    return table_data


def create_summary_stats(trials: List[Dict]) -> Dict:
    """
    Calculate summary statistics from optimization trials.
    
    Args:
        trials: List of trial dictionaries
    
    Returns:
        Dictionary of summary statistics
    """
    if not trials:
        return {}
    
    values = [t['value'] for t in trials]
    
    best_idx = np.argmax(values)
    best_trial = trials[best_idx]
    
    return {
        'total_trials': len(trials),
        'best_value': max(values),
        'worst_value': min(values),
        'mean_value': np.mean(values),
        'std_value': np.std(values),
        'best_trial_number': best_idx + 1,
        'best_params': best_trial['params'],
        'improvement': ((max(values) - values[0]) / abs(values[0]) * 100) if values[0] != 0 else 0
    }