# Sequential Game Solver Evolution

This example demonstrates using OpenEvolve to improve a backward induction solver for sequential (extensive-form) games. The solver finds **Subgame Perfect Nash Equilibrium** (SPNE) for games with perfect information.

## Overview

Sequential games are turn-based games where players move one at a time with complete knowledge of previous actions. Examples include:
- Centipede Game
- Entry Deterrence
- Stackelberg Duopoly
- Ultimatum Game

The backward induction algorithm solves these by working backwards from terminal nodes, determining the optimal action at each decision point.

## Background: The Original Solver

This example is inspired by the sequential game solver from [github.com/Jacck/seq](https://github.com/Jacck/seq), which implements backward induction for finding SPNE in JavaScript. Our goal is to use OpenEvolve to improve the Python implementation in terms of:

1. **Accuracy**: Correctly solving all game types
2. **Performance**: Faster execution on deep game trees
3. **Robustness**: Better error handling and edge cases

## Files

- `initial_program.py`: Initial backward induction implementation with EVOLVE markers
- `evaluator.py`: Cascade evaluator testing correctness, performance, and robustness
- `test_games.py`: Collection of canonical games for testing
- `config.yaml`: Evolution configuration optimized for algorithm improvement
- `README.md`: This file

## Game Representation

Games are represented as nested dictionaries:

```python
game = {
    "num_players": 2,
    "tree": {
        "id": "root",
        "player": 0,  # Current player (0-indexed)
        "actions": {
            "action_name": {
                # Child node (another decision or terminal)
                "id": "child",
                "player": 1,
                "actions": {...}
            },
            "other_action": {
                # Terminal node
                "payoffs": [5, 3]  # Payoffs for each player
            }
        }
    }
}
```

## Setup

### 1. Install OpenEvolve

```bash
cd /path/to/openevolve
pip install -e ".[dev]"
```

### 2. Set up API Key

OpenEvolve uses OpenAI-compatible APIs. Set your API key:

```bash
# For OpenAI
export OPENAI_API_KEY="your-key-here"

# For Google Gemini (default in config)
export OPENAI_API_KEY="your-gemini-key"
```

### 3. Verify Setup

Test the initial program:

```bash
cd examples/sequential_game_solver
python initial_program.py
```

Test the evaluator:

```bash
python evaluator.py initial_program.py
```

You should see output like:
```json
{
  "score": 75.5,
  "features": [0.83, 0.72, 1.0],
  "stage": 3,
  "accuracy": 0.83,
  "avg_solve_time": 0.0023,
  "games_tested": 6,
  "games_correct": 5
}
```

## Running Evolution

### Basic Evolution Run

```bash
cd /path/to/openevolve

python openevolve-run.py \
  examples/sequential_game_solver/initial_program.py \
  examples/sequential_game_solver/evaluator.py \
  --config examples/sequential_game_solver/config.yaml \
  --iterations 50
```

### Understanding the Output

Evolution creates an output directory with:

```
openevolve_output/
├── checkpoints/           # Periodic snapshots
│   ├── checkpoint_5/
│   ├── checkpoint_10/
│   └── ...
├── logs/                  # Execution logs
├── artifacts/             # Program outputs (if enabled)
└── best_program.py        # Best solution found
```

### Resume from Checkpoint

If evolution is interrupted, resume from the last checkpoint:

```bash
python openevolve-run.py \
  examples/sequential_game_solver/initial_program.py \
  examples/sequential_game_solver/evaluator.py \
  --config examples/sequential_game_solver/config.yaml \
  --checkpoint examples/sequential_game_solver/openevolve_output/checkpoints/checkpoint_25/ \
  --iterations 50
```

## Evaluation Metrics

The evaluator uses a cascade approach with three stages:

### Stage 1: Quick Validation
- Syntax checking
- Function imports
- **Threshold**: Program must compile and define `solve_game`

### Stage 2: Basic Correctness
- Tests on Centipede and Entry Deterrence games
- **Threshold**: Must solve at least 50% correctly

### Stage 3: Comprehensive Evaluation
- All canonical games (6 games)
- Performance testing (3 deep trees)
- Robustness testing (edge cases)

**Final Score** (0-100):
- 60% Accuracy (correctness on all games)
- 20% Performance (speed on deep trees)
- 20% Robustness (error handling)

**Features for MAP-Elites** (for diversity):
1. **Accuracy** (0-1): Fraction of games solved correctly
2. **Speed** (0-1): Inverse of average solve time
3. **Robustness** (0-1): Ability to handle edge cases

## Visualization

Visualize the evolution tree to see how programs evolved:

```bash
python scripts/visualizer.py \
  --path examples/sequential_game_solver/openevolve_output/checkpoints/checkpoint_50/
```

This shows:
- Evolution history tree
- Score progression
- Feature map distribution
- Island populations

## Customization

### Adding New Games

Edit `test_games.py` to add new test games:

```python
MY_GAME = {
    "num_players": 2,
    "name": "My Custom Game",
    "tree": {
        # Define your game tree
    },
    "expected_solution": {
        "equilibrium_payoffs": [5, 5],
        "first_action": "cooperate"
    }
}

ALL_GAMES.append(MY_GAME)
```

### Tuning Evolution

Modify `config.yaml`:

- `max_iterations`: How many evolution cycles
- `temperature`: Higher = more creative mutations
- `num_islands`: More islands = more diversity
- `migration_interval`: How often islands share solutions
- `feature_dimensions`: What aspects to diversify

### Modifying the Algorithm

The EVOLVE-BLOCK in `initial_program.py` (lines 47-84) is the focus of evolution. The LLM will propose improvements to:

- Algorithm efficiency
- Tie-breaking strategies
- Memory management
- Numerical precision

## Expected Results

After 50 iterations, you should see:

- **Accuracy**: 90%+ on canonical games
- **Performance**: 2-5x faster on deep trees
- **Robustness**: Better edge case handling

The evolved program might include optimizations like:

- Memoization for repeated subgames
- Alpha-beta pruning-like optimizations
- Better tie-breaking logic
- Iterative vs recursive approaches

## Troubleshooting

### API Rate Limits

If you hit rate limits, adjust in `config.yaml`:

```yaml
llm:
  timeout: 120
  retries: 5
  retry_delay: 10
```

### Out of Memory

For large populations:

```yaml
database:
  population_size: 200  # Reduce from 500
  num_islands: 2        # Reduce from 3
```

### Slow Evaluation

Reduce parallel evaluations or timeout:

```yaml
evaluator:
  parallel_evaluations: 2
  timeout: 30
```

## Game Theory Background

### Backward Induction

Starting from terminal nodes:
1. Identify all terminal payoffs
2. Move to parent nodes
3. Each player chooses action maximizing their payoff
4. Propagate chosen payoffs backward
5. Continue until reaching root

### Subgame Perfect Nash Equilibrium

A strategy profile is SPNE if it represents optimal play in every subgame, even off the equilibrium path. This eliminates non-credible threats.

### Example: Entry Deterrence

```
Entrant: [Stay Out] → (1, 2)
         [Enter] → Incumbent: [Fight] → (-1, -1)
                             [Accommodate] → (2, 1)
```

**Backward induction**:
- At incumbent's node: Accommodate (1 > -1)
- At entrant's node: Enter (2 > 1)
- **SPNE**: (Enter, Accommodate) → (2, 1)

The threat to "Fight" is not credible since the incumbent prefers to Accommodate.

## Related Examples

- `examples/function_minimization/`: Optimize continuous functions
- `examples/symbolic_regression/`: Discover mathematical formulas
- `examples/rust_adaptive_sort/`: Evolve sorting algorithms

## References

1. [github.com/Jacck/seq](https://github.com/Jacck/seq) - Original JavaScript solver
2. Selten, R. (1965) - Spieltheoretische Behandlung eines Oligopolmodells
3. Rosenthal, R. (1981) - Games of Perfect Information (Centipede Game)
4. von Stackelberg, H. (1934) - Market Structure and Equilibrium

## Contributing

To improve this example:

1. Add more complex game types (simultaneous moves, imperfect information)
2. Implement alternative solution concepts (Nash, Bayesian)
3. Add visualization of game trees
4. Create interactive solver interface

## License

This example is part of OpenEvolve and follows the same license.
