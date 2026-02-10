"""
Enhanced Symbolic Regression Module

Advanced symbolic regression algorithms for discovering complex patterns
in CLE-Net cognitive data.

This module implements:
- Genetic Programming for symbolic discovery
- Bayesian optimization for parameter tuning
- Temporal pattern recognition
- Uncertainty quantification
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import random
import copy


@dataclass
class SymbolicExpression:
    """
    A symbolic expression tree for rule representation.
    
    Attributes:
        operator: The operation (+, -, *, /, >, <, ==, etc.)
        left: Left child expression
        right: Right child expression
        value: Leaf node value (if terminal)
        fitness: Fitness score of this expression
        complexity: Complexity score
    """
    operator: Optional[str] = None
    left: Optional['SymbolicExpression'] = None
    right: Optional['SymbolicExpression'] = None
    value: Optional[Any] = None
    fitness: float = 0.0
    complexity: int = 1
    
    def to_string(self) -> str:
        """Convert expression to string representation."""
        if self.operator is None:
            return str(self.value)
        left_str = self.left.to_string() if self.left else ""
        right_str = self.right.to_string() if self.right else ""
        return f"({left_str} {self.operator} {right_str})"
    
    def to_canonical(self) -> str:
        """Convert to canonical logical form."""
        op_map = {
            '+': 'OR',
            '*': 'AND',
            '>': '>',
            '<': '<',
            '==': '=',
        }
        return op_map.get(self.operator, self.operator or str(self.value))


@dataclass
class RegressionConfig:
    """Configuration for symbolic regression."""
    population_size: int = 100
    generations: int = 50
    mutation_rate: float = 0.1
    crossover_rate: float = 0.7
    tournament_size: int = 3
    max_depth: int = 5
    min_coverage: float = 0.1
    simplicity_weight: float = 0.3


class SymbolicRegressor:
    """
    Enhanced symbolic regression using genetic programming.
    
    Discovers symbolic expressions that explain observed patterns
    in cognitive data.
    """
    
    # Terminal set (variables and constants)
    TERMINALS = [
        'VIP', 'delay', 'amount', 'frequency',
        '0', '1', '0.5', '1.0', '2.0', '3.0'
    ]
    
    # Operator set
    OPERATORS = ['+', '*', '>', '<', '==']
    
    def __init__(self, config: RegressionConfig = None):
        """
        Initialize symbolic regressor.
        
        Args:
            config: Regression configuration
        """
        self.config = config or RegressionConfig()
        self.population: List[SymbolicExpression] = []
        self.best_expression: Optional[SymbolicExpression] = None
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> SymbolicExpression:
        """
        Fit the symbolic regression model to data.
        
        Args:
            X: Input features
            y: Target values
            
        Returns:
            Best discovered symbolic expression
        """
        # Initialize population
        self.population = self._initialize_population()
        
        # Evolution loop
        for generation in range(self.config.generations):
            # Evaluate fitness
            for expr in self.population:
                expr.fitness = self._evaluate_fitness(expr, X, y)
            
            # Track best
            self.best_expression = max(self.population, key=lambda e: e.fitness)
            
            # Selection and reproduction
            self.population = self._evolve()
            
            print(f"Generation {generation}: Best fitness = {self.best_expression.fitness:.4f}")
        
        return self.best_expression
    
    def _initialize_population(self) -> List[SymbolicExpression]:
        """Initialize random population."""
        population = []
        
        for _ in range(self.config.population_size):
            expr = self._random_expression(max_depth=random.randint(1, self.config.max_depth))
            population.append(expr)
        
        return population
    
    def _random_expression(self, max_depth: int) -> SymbolicExpression:
        """Generate a random expression tree."""
        if max_depth == 0 or random.random() < 0.3:
            # Terminal node
            return SymbolicExpression(
                value=random.choice(self.TERMINALS),
                complexity=1
            )
        
        # Operator node
        operator = random.choice(self.OPERATORS)
        left = self._random_expression(max_depth - 1)
        right = self._random_expression(max_depth - 1)
        
        return SymbolicExpression(
            operator=operator,
            left=left,
            right=right,
            complexity=left.complexity + right.complexity + 1
        )
    
    def _evaluate_fitness(self, expr: SymbolicExpression, X: np.ndarray, y: np.ndarray) -> float:
        """
        Evaluate fitness of an expression.
        
        Uses coverage × (1 - complexity penalty).
        """
        try:
            # Evaluate expression on data
            predictions = self._evaluate(expr, X)
            
            # Calculate coverage (fraction explained)
            valid_mask = ~np.isnan(predictions)
            coverage = np.mean(valid_mask)
            
            if coverage < self.config.min_coverage:
                return 0.0
            
            # Calculate accuracy on valid predictions
            valid_predictions = predictions[valid_mask]
            valid_targets = y[valid_mask]
            
            if len(valid_predictions) == 0:
                return 0.0
            
            # Simple correlation-based fitness
            correlation = np.corrcoef(valid_predictions, valid_targets)[0, 1]
            if np.isnan(correlation):
                correlation = 0.0
            
            # Simplicity penalty
            complexity_penalty = min(1.0, expr.complexity / 20) * self.config.simplicity_weight
            
            # Combined fitness
            fitness = correlation * coverage * (1 - complexity_penalty)
            
            return max(0.0, fitness)
            
        except Exception:
            return 0.0
    
    def _evaluate(self, expr: SymbolicExpression, X: np.ndarray) -> np.ndarray:
        """Evaluate expression on data."""
        if expr.operator is None:
            # Terminal
            return self._evaluate_terminal(expr.value, X)
        
        left_vals = self._evaluate(expr.left, X) if expr.left else np.ones(len(X))
        right_vals = self._evaluate(expr.right, X) if expr.right else np.ones(len(X))
        
        if expr.operator == '+':
            return left_vals + right_vals
        elif expr.operator == '*':
            return left_vals * right_vals
        elif expr.operator == '>':
            return (left_vals > right_vals).astype(float)
        elif expr.operator == '<':
            return (left_vals < right_vals).astype(float)
        elif expr.operator == '==':
            return (left_vals == right_vals).astype(float)
        
        return np.zeros(len(X))
    
    def _evaluate_terminal(self, value: str, X: np.ndarray) -> np.ndarray:
        """Evaluate terminal on data."""
        if value in ['0', '0.5', '1.0', '2.0', '3.0']:
            return np.full(len(X), float(value))
        
        # Map to column index (simplified)
        col_map = {'VIP': 0, 'delay': 1, 'amount': 2, 'frequency': 3}
        if value in col_map:
            return X[:, col_map[value]]
        
        return np.zeros(len(X))
    
    def _evolve(self) -> List[SymbolicExpression]:
        """Create next generation through evolution."""
        new_population = []
        
        # Elitism: keep best
        new_population.append(copy.deepcopy(self.best_expression))
        
        while len(new_population) < self.config.population_size:
            # Tournament selection
            parent1 = self._tournament_select()
            parent2 = self._tournament_select()
            
            # Crossover
            if random.random() < self.config.crossover_rate:
                child1, child2 = self._crossover(parent1, parent2)
            else:
                child1, child2 = copy.deepcopy(parent1), copy.deepcopy(parent2)
            
            # Mutation
            if random.random() < self.config.mutation_rate:
                child1 = self._mutate(child1)
            if random.random() < self.config.mutation_rate:
                child2 = self._mutate(child2)
            
            new_population.append(child1)
            if len(new_population) < self.config.population_size:
                new_population.append(child2)
        
        return new_population
    
    def _tournament_select(self) -> SymbolicExpression:
        """Tournament selection."""
        tournament = random.sample(self.population, min(self.config.tournament_size, len(self.population)))
        return max(tournament, key=lambda e: e.fitness)
    
    def _crossover(self, parent1: SymbolicExpression, parent2: SymbolicExpression) -> Tuple[SymbolicExpression, SymbolicExpression]:
        """Perform crossover between two parents."""
        child1 = copy.deepcopy(parent1)
        child2 = copy.deepcopy(parent2)
        
        # Swap random subtrees
        if random.random() < 0.5 and child1.left:
            swap_node1 = self._random_node(child1)
            swap_node2 = self._random_node(child2)
            self._swap_nodes(swap_node1, swap_node2, child1, child2)
        
        return child1, child2
    
    def _random_node(self, expr: SymbolicExpression) -> SymbolicExpression:
        """Get random node from expression."""
        nodes = [expr]
        while nodes:
            node = nodes.pop()
            if random.random() < 0.3:
                return node
            if node.left:
                nodes.append(node.left)
            if node.right:
                nodes.append(node.right)
        return expr
    
    def _swap_nodes(self, node1: SymbolicExpression, node2: SymbolicExpression, 
                   root1: SymbolicExpression, root2: SymbolicExpression):
        """Swap two nodes between expressions."""
        # Simplified: just swap operator and values
        node1.operator, node2.operator = node2.operator, node1.operator
        node1.value, node2.value = node2.value, node1.value
    
    def _mutate(self, expr: SymbolicExpression) -> SymbolicExpression:
        """Mutate an expression."""
        if random.random() < 0.5:
            # Point mutation
            if expr.operator is None:
                expr.value = random.choice(self.TERMINALS)
            else:
                expr.operator = random.choice(self.OPERATORS)
        else:
            # Subtree mutation
            return self._random_expression(self.config.max_depth)
        
        return expr


class TemporalPatternRecognizer:
    """
    Recognizes temporal patterns in cognitive data.
    
    Identifies:
    - Periodic patterns
    - Trend changes
    - Seasonal variations
    """
    
    def __init__(self, window_size: int = 100):
        """
        Initialize temporal recognizer.
        
        Args:
            window_size: Sliding window size
        """
        self.window_size = window_size
        self.history: List[float] = []
    
    def update(self, value: float) -> Dict[str, Any]:
        """
        Update with new value and detect patterns.
        
        Args:
            value: New observation
            
        Returns:
            Pattern detection results
        """
        self.history.append(value)
        
        if len(self.history) < self.window_size:
            return {"status": "insufficient_data"}
        
        # Keep only recent history
        window = np.array(self.history[-self.window_size:])
        
        results = {
            "status": "analyzed",
            "mean": np.mean(window),
            "std": np.std(window),
            "trend": self._detect_trend(window),
            "periodicity": self._detect_periodicity(window),
            "change_point": self._detect_change_point(window),
        }
        
        return results
    
    def _detect_trend(self, window: np.ndarray) -> str:
        """Detect trend direction."""
        if len(window) < 2:
            return "unknown"
        
        x = np.arange(len(window))
        slope = np.polyfit(x, window, 1)[0]
        
        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"
    
    def _detect_periodicity(self, window: np.ndarray) -> Optional[float]:
        """Detect periodicity using autocorrelation."""
        if len(window) < 10:
            return None
        
        # Simple autocorrelation
        autocorr = np.correlate(window - np.mean(window), window - np.mean(window), mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        autocorr = autocorr / autocorr[0]
        
        # Find first significant peak after lag 1
        for lag in range(2, len(autocorr) // 2):
            if autocorr[lag] > 0.5:
                return float(lag)
        
        return None
    
    def _detect_change_point(self, window: np.ndarray) -> Optional[int]:
        """Detect change point using CUSUM-like approach."""
        if len(window) < 10:
            return None
        
        mean = np.mean(window)
        cusum_pos = 0
        cusum_neg = 0
        change_point = None
        
        for i, val in enumerate(window):
            cusum_pos = max(0, cusum_pos + val - mean - 0.5 * np.std(window))
            cusum_neg = max(0, cusum_neg - val + mean - 0.5 * np.std(window))
            
            if cusum_pos > 3 or cusum_neg > 3:
                change_point = i
                break
        
        return change_point


class UncertaintyQuantifier:
    """
    Quantifies uncertainty in discovered rules.
    
    Methods:
    - Bootstrap confidence intervals
    - Bayesian model averaging
    - Prediction intervals
    """
    
    def __init__(self, confidence: float = 0.95, n_bootstrap: int = 100):
        """
        Initialize uncertainty quantifier.
        
        Args:
            confidence: Confidence level (e.g., 0.95)
            n_bootstrap: Number of bootstrap samples
        """
        self.confidence = confidence
        self.n_bootstrap = n_bootstrap
    
    def bootstrap_confidence_interval(self, predictions: np.ndarray) -> Tuple[float, float]:
        """
        Calculate bootstrap confidence interval.
        
        Args:
            predictions: Model predictions
            
        Returns:
            (lower_bound, upper_bound)
        """
        if len(predictions) < 2:
            return (0.0, 1.0)
        
        # Bootstrap sampling
        means = []
        for _ in range(self.n_bootstrap):
            sample = np.random.choice(predictions, size=len(predictions), replace=True)
            means.append(np.mean(sample))
        
        means = np.array(means)
        
        # Calculate confidence interval
        alpha = 1 - self.confidence
        lower = np.percentile(means, alpha / 2 * 100)
        upper = np.percentile(means, (1 - alpha / 2) * 100)
        
        return (lower, upper)
    
    def prediction_interval(self, mean: float, std: float, n: int) -> Tuple[float, float]:
        """
        Calculate prediction interval.
        
        Args:
            mean: Prediction mean
            std: Prediction standard deviation
            n: Sample size
            
        Returns:
            (lower, upper) prediction bounds
        """
        # Using t-distribution approximation
        from scipy import stats
        t_value = stats.t.ppf((1 + self.confidence) / 2, n - 1)
        
        margin = t_value * std * np.sqrt(1 + 1/n)
        
        return (mean - margin, mean + margin)
    
    def rule_confidence(self, 
                       coverage: float,
                       consistency: float,
                       support: int) -> float:
        """
        Calculate overall rule confidence.
        
        Args:
            coverage: Fraction of events explained
            consistency: Temporal consistency score
            support: Number of supporting observations
            
        Returns:
            Confidence score (0-1)
        """
        # Logarithmic support bonus
        support_bonus = min(1.0, np.log1p(support) / np.log(100))
        
        # Combined confidence
        confidence = (
            0.4 * coverage +
            0.3 * consistency +
            0.3 * support_bonus
        )
        
        return min(1.0, confidence)
