"""
Evaluator for sequential game solver.
Tests correctness, performance, and robustness of evolved solvers.

Implements cascade evaluation:
- Stage 1: Quick validation (syntax, imports)
- Stage 2: Basic correctness tests
- Stage 3: Comprehensive evaluation (performance, edge cases)
"""

import sys
import time
import traceback
from typing import Dict, Any
import importlib.util

# Import test games
from test_games import (
    ALL_GAMES,
    PERFORMANCE_GAMES,
    CENTIPEDE_GAME,
    ENTRY_DETERRENCE_GAME
)


def evaluate(program_str: str) -> Dict[str, Any]:
    """
    Evaluate a sequential game solver program.

    Returns:
        Dictionary with score, features, and detailed results
    """

    # Stage 1: Quick Validation
    # --------------------------------------------------
    try:
        # Try to compile the program
        compile(program_str, '<program>', 'exec')
    except SyntaxError as e:
        return {
            "score": 0.0,
            "features": [0.0, 0.0, 0.0],
            "error": f"Syntax error: {str(e)}",
            "stage": 1
        }

    # Execute the program and import solve_game function
    try:
        namespace = {}
        exec(program_str, namespace)
        solve_game = namespace.get("solve_game")

        if solve_game is None:
            return {
                "score": 0.0,
                "features": [0.0, 0.0, 0.0],
                "error": "solve_game function not found",
                "stage": 1
            }
    except Exception as e:
        return {
            "score": 0.0,
            "features": [0.0, 0.0, 0.0],
            "error": f"Import error: {str(e)}",
            "stage": 1
        }

    # Stage 2: Basic Correctness Tests
    # --------------------------------------------------
    correctness_score = 0.0
    basic_games = [CENTIPEDE_GAME, ENTRY_DETERRENCE_GAME]

    for game in basic_games:
        try:
            solution = solve_game(game)

            # Check if solution has required fields
            if "equilibrium_payoffs" not in solution:
                continue

            # Check correctness against expected solution
            expected = game.get("expected_solution", {})
            if "equilibrium_payoffs" in expected:
                if solution["equilibrium_payoffs"] == expected["equilibrium_payoffs"]:
                    correctness_score += 1.0

        except Exception:
            # Failed to solve this game
            continue

    # Normalize correctness score
    correctness_score = correctness_score / len(basic_games)

    if correctness_score < 0.5:
        # Failed basic tests
        return {
            "score": correctness_score * 20,  # Max 10 points
            "features": [correctness_score, 0.0, 0.0],
            "stage": 2,
            "correctness": correctness_score
        }

    # Stage 3: Comprehensive Evaluation
    # --------------------------------------------------

    # 3a: Test all canonical games
    all_correct = 0
    all_tested = 0

    for game in ALL_GAMES:
        try:
            solution = solve_game(game)
            all_tested += 1

            expected = game.get("expected_solution", {})
            if "equilibrium_payoffs" in expected:
                if solution["equilibrium_payoffs"] == expected["equilibrium_payoffs"]:
                    all_correct += 1
        except Exception:
            all_tested += 1
            continue

    accuracy = all_correct / all_tested if all_tested > 0 else 0.0

    # 3b: Performance testing
    performance_times = []
    performance_success = 0

    for game in PERFORMANCE_GAMES:
        try:
            start_time = time.time()
            solution = solve_game(game)
            elapsed = time.time() - start_time

            performance_times.append(elapsed)
            if solution.get("equilibrium_payoffs") is not None:
                performance_success += 1
        except Exception:
            performance_times.append(10.0)  # Penalty for failure

    avg_time = sum(performance_times) / len(performance_times)
    # Speed score: faster is better (inverse relationship)
    # Cap at 10 seconds, normalize to 0-1
    speed_score = max(0.0, 1.0 - (avg_time / 10.0))

    performance_ratio = performance_success / len(PERFORMANCE_GAMES)

    # 3c: Robustness - test error handling
    robustness_score = 0.0

    # Test with malformed game (should not crash)
    try:
        bad_game = {"num_players": 2, "tree": {}}
        result = solve_game(bad_game)
        robustness_score += 0.5
    except Exception:
        # It's okay to raise an exception for invalid input
        robustness_score += 0.5

    # Test with single-node game
    try:
        single_node = {
            "num_players": 2,
            "tree": {"payoffs": [5, 5]}
        }
        result = solve_game(single_node)
        if result.get("equilibrium_payoffs") == [5, 5]:
            robustness_score += 0.5
    except Exception:
        pass

    # Calculate final score
    # Weights: accuracy (60%), performance (20%), robustness (20%)
    final_score = (
        accuracy * 60.0 +
        (speed_score * performance_ratio) * 20.0 +
        robustness_score * 20.0
    )

    # Features for MAP-Elites diversity
    # Feature 1: Accuracy (0-1)
    # Feature 2: Speed (0-1, higher is faster)
    # Feature 3: Robustness (0-1)
    features = [
        round(accuracy, 2),
        round(speed_score, 2),
        round(robustness_score, 2)
    ]

    return {
        "score": round(final_score, 2),
        "features": features,
        "stage": 3,
        "accuracy": accuracy,
        "avg_solve_time": round(avg_time, 4),
        "performance_success_rate": performance_ratio,
        "robustness": robustness_score,
        "games_tested": all_tested,
        "games_correct": all_correct
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python evaluator.py <program_file>")
        sys.exit(1)

    program_file = sys.argv[1]

    with open(program_file, 'r') as f:
        program_str = f.read()

    result = evaluate(program_str)

    # Print result as JSON for OpenEvolve
    import json
    print(json.dumps(result, indent=2))
