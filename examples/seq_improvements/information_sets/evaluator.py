"""
Evaluator for Information Sets Implementation

This evaluator tests the evolved JavaScript code for information sets support.
It uses a cascade evaluation pattern:
- Stage 1: Syntax validation and basic structure
- Stage 2: Functional correctness on simple games
- Stage 3: Advanced scenarios and edge cases
"""

import subprocess
import json
import tempfile
import os
from typing import Dict, Any, Tuple


def evaluate(program_str: str) -> Tuple[float, Dict[str, Any]]:
    """
    Evaluate the information sets implementation.

    Args:
        program_str: The JavaScript code to evaluate

    Returns:
        Tuple of (fitness_score, artifacts_dict)
    """
    artifacts = {
        "stage": 0,
        "tests_passed": 0,
        "tests_failed": 0,
        "errors": [],
        "test_results": []
    }

    # Stage 1: Syntax validation
    artifacts["stage"] = 1
    if not validate_syntax(program_str, artifacts):
        return 0.0, artifacts

    # Stage 2: Basic functionality
    artifacts["stage"] = 2
    basic_score = test_basic_functionality(program_str, artifacts)
    if basic_score < 0.5:  # Must pass at least 50% of basic tests
        return basic_score * 0.3, artifacts

    # Stage 3: Advanced scenarios
    artifacts["stage"] = 3
    advanced_score = test_advanced_scenarios(program_str, artifacts)

    # Calculate final fitness
    # 30% basic, 70% advanced
    final_score = (basic_score * 0.3) + (advanced_score * 0.7)

    return final_score, artifacts


def validate_syntax(program_str: str, artifacts: Dict[str, Any]) -> bool:
    """Stage 1: Check if JavaScript is syntactically valid."""
    try:
        # Check for required functions
        required_functions = [
            'addInformationSets',
            'groupNodesIntoInformationSet',
            'solveWithInformationSets'
        ]

        for func in required_functions:
            if func not in program_str:
                artifacts["errors"].append(f"Missing required function: {func}")
                return False

        # Try to parse with Node.js
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(program_str)
            temp_file = f.name

        try:
            result = subprocess.run(
                ['node', '--check', temp_file],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                artifacts["errors"].append(f"Syntax error: {result.stderr}")
                return False
        finally:
            os.unlink(temp_file)

        return True

    except Exception as e:
        artifacts["errors"].append(f"Validation error: {str(e)}")
        return False


def test_basic_functionality(program_str: str, artifacts: Dict[str, Any]) -> float:
    """Stage 2: Test basic information sets functionality."""
    tests_passed = 0
    total_tests = 3

    # Test 1: Can create information sets for a simple game
    test_name = "Create information sets"
    if run_js_test(program_str, TEST_CREATE_INFO_SETS, artifacts, test_name):
        tests_passed += 1

    # Test 2: Can group nodes into information sets
    test_name = "Group nodes manually"
    if run_js_test(program_str, TEST_GROUP_NODES, artifacts, test_name):
        tests_passed += 1

    # Test 3: Can solve simple game with information sets
    test_name = "Solve with information sets"
    if run_js_test(program_str, TEST_SOLVE_SIMPLE, artifacts, test_name):
        tests_passed += 1

    artifacts["tests_passed"] = tests_passed
    artifacts["tests_failed"] = total_tests - tests_passed

    return tests_passed / total_tests


def test_advanced_scenarios(program_str: str, artifacts: Dict[str, Any]) -> float:
    """Stage 3: Test advanced scenarios."""
    tests_passed = artifacts["tests_passed"]
    total_tests = 6

    # Test 4: Simultaneous move game
    test_name = "Simultaneous moves"
    if run_js_test(program_str, TEST_SIMULTANEOUS_MOVES, artifacts, test_name):
        tests_passed += 1

    # Test 5: Validation - reject invalid information sets
    test_name = "Validation - different players"
    if run_js_test(program_str, TEST_VALIDATION_PLAYERS, artifacts, test_name):
        tests_passed += 1

    # Test 6: Complex game with multiple information sets
    test_name = "Multiple information sets"
    if run_js_test(program_str, TEST_MULTIPLE_INFO_SETS, artifacts, test_name):
        tests_passed += 1

    artifacts["tests_passed"] = tests_passed
    artifacts["tests_failed"] = total_tests - tests_passed

    return tests_passed / total_tests


def run_js_test(program_str: str, test_code: str, artifacts: Dict[str, Any], test_name: str) -> bool:
    """Execute a JavaScript test and return success/failure."""
    try:
        # Combine program and test code
        full_code = program_str + "\n\n" + test_code

        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(full_code)
            temp_file = f.name

        try:
            result = subprocess.run(
                ['node', temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )

            success = result.returncode == 0

            artifacts["test_results"].append({
                "name": test_name,
                "passed": success,
                "stdout": result.stdout[:500],  # Limit output size
                "stderr": result.stderr[:500] if result.stderr else ""
            })

            return success

        finally:
            os.unlink(temp_file)

    except subprocess.TimeoutExpired:
        artifacts["test_results"].append({
            "name": test_name,
            "passed": False,
            "error": "Test timed out"
        })
        return False
    except Exception as e:
        artifacts["test_results"].append({
            "name": test_name,
            "passed": False,
            "error": str(e)
        })
        return False


# ========================================
# TEST CASES
# ========================================

TEST_CREATE_INFO_SETS = """
// Test: Create information sets for a simple game
const simpleGame = {
    "root": {
        id: "root",
        player: "P1",
        actions: {
            "Left": "terminal1",
            "Right": "terminal2"
        }
    },
    "terminal1": { id: "terminal1", payoffs: [3, 1] },
    "terminal2": { id: "terminal2", payoffs: [1, 3] }
};

try {
    const enhanced = addInformationSets(simpleGame);

    // Check that information sets were added
    if (!enhanced._informationSets) {
        throw new Error("No _informationSets metadata added");
    }

    // Check that root has an information set
    if (!enhanced.root.informationSet) {
        throw new Error("Root node missing informationSet");
    }

    console.log("✓ Information sets created successfully");
    process.exit(0);
} catch (error) {
    console.error("✗ Test failed:", error.message);
    process.exit(1);
}
"""

TEST_GROUP_NODES = """
// Test: Group nodes into information sets manually
const game = {
    "n1": { id: "n1", player: "P1", actions: { "A": "n2", "B": "n3" } },
    "n2": { id: "n2", player: "P2", actions: { "X": "t1", "Y": "t2" } },
    "n3": { id: "n3", player: "P2", actions: { "X": "t3", "Y": "t4" } },
    "t1": { id: "t1", payoffs: [1, 2] },
    "t2": { id: "t2", payoffs: [3, 4] },
    "t3": { id: "t3", payoffs: [5, 6] },
    "t4": { id: "t4", payoffs: [7, 8] }
};

try {
    // Group n2 and n3 into same information set (P2 can't distinguish)
    const enhanced = groupNodesIntoInformationSet(game, ["n2", "n3"], "P2_InfoSet");

    if (enhanced.n2.informationSet !== "P2_InfoSet") {
        throw new Error("n2 not in correct information set");
    }

    if (enhanced.n3.informationSet !== "P2_InfoSet") {
        throw new Error("n3 not in correct information set");
    }

    console.log("✓ Nodes grouped successfully");
    process.exit(0);
} catch (error) {
    console.error("✗ Test failed:", error.message);
    process.exit(1);
}
"""

TEST_SOLVE_SIMPLE = """
// Test: Solve a simple game with information sets
const game = {
    "root": {
        id: "root",
        player: "P1",
        actions: {
            "Left": "terminal1",
            "Right": "terminal2"
        }
    },
    "terminal1": { id: "terminal1", payoffs: [3, 1] },
    "terminal2": { id: "terminal2", payoffs: [1, 3] }
};

try {
    const solution = solveWithInformationSets(game, "root");

    // Check solution structure
    if (!solution.strategies) {
        throw new Error("Missing strategies in solution");
    }

    if (!solution.equilibriumPath) {
        throw new Error("Missing equilibrium path");
    }

    if (!solution.terminalPayoffs) {
        throw new Error("Missing terminal payoffs");
    }

    console.log("✓ Game solved successfully");
    console.log("  Strategies:", JSON.stringify(solution.strategies));
    process.exit(0);
} catch (error) {
    console.error("✗ Test failed:", error.message);
    process.exit(1);
}
"""

TEST_SIMULTANEOUS_MOVES = """
// Test: Game with simultaneous moves (matching pennies)
const simultaneousGame = {
    "root": { id: "root", player: "Nature", actions: { "Start": "p1_choice" } },
    "p1_choice": { id: "p1_choice", player: "P1", actions: { "Heads": "p2_h", "Tails": "p2_t" } },
    "p2_h": { id: "p2_h", player: "P2", informationSet: "P2_simultaneous", actions: { "Heads": "th_h", "Tails": "th_t" } },
    "p2_t": { id: "p2_t", player: "P2", informationSet: "P2_simultaneous", actions: { "Heads": "tt_h", "Tails": "tt_t" } },
    "th_h": { id: "th_h", payoffs: [1, -1] },
    "th_t": { id: "th_t", payoffs: [-1, 1] },
    "tt_h": { id: "tt_h", payoffs: [-1, 1] },
    "tt_t": { id: "tt_t", payoffs: [1, -1] }
};

try {
    const solution = solveWithInformationSets(simultaneousGame, "root");

    // P2's nodes should be in same information set
    if (!solution.beliefs || !solution.beliefs.P2_simultaneous) {
        console.log("  Warning: No beliefs tracked for P2_simultaneous");
    }

    console.log("✓ Simultaneous move game handled");
    process.exit(0);
} catch (error) {
    console.error("✗ Test failed:", error.message);
    process.exit(1);
}
"""

TEST_VALIDATION_PLAYERS = """
// Test: Should reject information sets with different players
const invalidGame = {
    "n1": { id: "n1", player: "P1", actions: { "A": "t1" } },
    "n2": { id: "n2", player: "P2", actions: { "B": "t2" } },
    "t1": { id: "t1", payoffs: [1, 2] },
    "t2": { id: "t2", payoffs: [3, 4] }
};

try {
    // This should throw an error
    groupNodesIntoInformationSet(invalidGame, ["n1", "n2"], "Invalid");

    console.error("✗ Should have rejected different players in same info set");
    process.exit(1);
} catch (error) {
    if (error.message.includes("same player")) {
        console.log("✓ Correctly rejected invalid information set");
        process.exit(0);
    } else {
        console.error("✗ Wrong error message:", error.message);
        process.exit(1);
    }
}
"""

TEST_MULTIPLE_INFO_SETS = """
// Test: Complex game with multiple information sets
const complexGame = {
    "root": { id: "root", player: "P1", actions: { "A": "n2", "B": "n3" } },
    "n2": { id: "n2", player: "P2", informationSet: "IS_P2", actions: { "X": "n4", "Y": "n5" } },
    "n3": { id: "n3", player: "P2", informationSet: "IS_P2", actions: { "X": "n6", "Y": "n7" } },
    "n4": { id: "n4", player: "P1", informationSet: "IS_P1", actions: { "C": "t1", "D": "t2" } },
    "n5": { id: "n5", player: "P1", informationSet: "IS_P1", actions: { "C": "t3", "D": "t4" } },
    "n6": { id: "n6", player: "P1", actions: { "C": "t5", "D": "t6" } },
    "n7": { id: "n7", player: "P1", actions: { "C": "t7", "D": "t8" } },
    "t1": { id: "t1", payoffs: [3, 3] },
    "t2": { id: "t2", payoffs: [1, 5] },
    "t3": { id: "t3", payoffs: [5, 1] },
    "t4": { id: "t4", payoffs: [2, 2] },
    "t5": { id: "t5", payoffs: [4, 4] },
    "t6": { id: "t6", payoffs: [0, 6] },
    "t7": { id: "t7", payoffs: [6, 0] },
    "t8": { id: "t8", payoffs: [1, 1] }
};

try {
    const enhanced = addInformationSets(complexGame);
    const solution = solveWithInformationSets(complexGame, "root");

    // Should have multiple information sets
    if (!enhanced._informationSets || Object.keys(enhanced._informationSets).length < 3) {
        throw new Error("Should have at least 3 information sets");
    }

    console.log("✓ Complex game with multiple information sets solved");
    console.log("  Information sets:", Object.keys(enhanced._informationSets).length);
    process.exit(0);
} catch (error) {
    console.error("✗ Test failed:", error.message);
    process.exit(1);
}
"""


if __name__ == "__main__":
    # Test the evaluator itself
    print("Testing evaluator...")

    # Read the initial program
    with open("initial_program.js", "r") as f:
        program = f.read()

    score, artifacts = evaluate(program)
    print(f"\nFitness Score: {score:.2f}")
    print(f"Stage: {artifacts['stage']}")
    print(f"Tests Passed: {artifacts['tests_passed']}")
    print(f"Tests Failed: {artifacts['tests_failed']}")

    if artifacts.get("errors"):
        print("\nErrors:")
        for error in artifacts["errors"]:
            print(f"  - {error}")

    print("\nTest Results:")
    for test in artifacts.get("test_results", []):
        status = "✓" if test["passed"] else "✗"
        print(f"  {status} {test['name']}")
        if not test["passed"] and test.get("error"):
            print(f"    Error: {test['error']}")
