"""
Sequential Game Solver using Backward Induction
Finds Subgame Perfect Nash Equilibrium for extensive-form games.

This program will be evolved by OpenEvolve to improve:
- Algorithm efficiency
- Handling of complex game trees
- Edge case handling
- Performance optimization
"""

import json
from typing import Dict, List, Any, Tuple, Optional


class GameNode:
    """Represents a node in the game tree."""

    def __init__(self, node_id: str, player: Optional[int],
                 actions: Optional[Dict[str, Any]],
                 payoffs: Optional[List[float]] = None):
        self.node_id = node_id
        self.player = player  # None for terminal nodes
        self.actions = actions or {}  # Dict of action_name -> child_node
        self.payoffs = payoffs  # Terminal node payoffs
        self.best_action = None
        self.expected_payoffs = None


def parse_game_tree(game_spec: Dict[str, Any]) -> Tuple[GameNode, int]:
    """Parse game specification into GameNode tree structure."""

    def build_node(node_spec: Dict[str, Any]) -> GameNode:
        if "payoffs" in node_spec:
            # Terminal node
            return GameNode(
                node_id=node_spec.get("id", "terminal"),
                player=None,
                actions=None,
                payoffs=node_spec["payoffs"]
            )
        else:
            # Decision node
            actions = {}
            for action_name, child_spec in node_spec.get("actions", {}).items():
                actions[action_name] = build_node(child_spec)

            return GameNode(
                node_id=node_spec.get("id", "node"),
                player=node_spec["player"],
                actions=actions
            )

    root = build_node(game_spec["tree"])
    num_players = game_spec.get("num_players", 2)
    return root, num_players


# EVOLVE-BLOCK-START
def backward_induction(node: GameNode, num_players: int) -> List[float]:
    """
    Solve game tree using backward induction.

    This algorithm can be evolved to improve:
    - Efficiency for large trees
    - Handling of ties in payoffs
    - Memory usage
    - Numerical stability

    Args:
        node: Current game tree node
        num_players: Number of players in the game

    Returns:
        Expected payoffs at this node for each player
    """
    # Base case: terminal node
    if node.payoffs is not None:
        node.expected_payoffs = node.payoffs.copy()
        return node.expected_payoffs

    # Recursive case: decision node
    # Evaluate all possible actions
    action_payoffs = {}
    for action_name, child_node in node.actions.items():
        payoffs = backward_induction(child_node, num_players)
        action_payoffs[action_name] = payoffs

    # Current player chooses action that maximizes their payoff
    current_player = node.player
    best_action = None
    best_payoff = float('-inf')

    for action_name, payoffs in action_payoffs.items():
        player_payoff = payoffs[current_player]
        if player_payoff > best_payoff:
            best_payoff = player_payoff
            best_action = action_name

    # Store the optimal action and resulting payoffs
    node.best_action = best_action
    node.expected_payoffs = action_payoffs[best_action]

    return node.expected_payoffs
# EVOLVE-BLOCK-END


def solve_game(game_spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point: solve a sequential game.

    Args:
        game_spec: Game specification with tree structure and metadata

    Returns:
        Solution including equilibrium path and payoffs
    """
    root, num_players = parse_game_tree(game_spec)

    # Solve using backward induction
    equilibrium_payoffs = backward_induction(root, num_players)

    # Extract equilibrium path
    equilibrium_path = []
    current = root
    while current.best_action is not None:
        equilibrium_path.append({
            "node": current.node_id,
            "player": current.player,
            "action": current.best_action
        })
        current = current.actions[current.best_action]

    return {
        "equilibrium_payoffs": equilibrium_payoffs,
        "equilibrium_path": equilibrium_path,
        "solution_type": "Subgame Perfect Nash Equilibrium"
    }


# Example usage for testing
if __name__ == "__main__":
    # Simple Ultimatum Game: Player 0 proposes split, Player 1 accepts/rejects
    ultimatum_game = {
        "num_players": 2,
        "tree": {
            "id": "root",
            "player": 0,
            "actions": {
                "offer_9-1": {
                    "id": "respond_9-1",
                    "player": 1,
                    "actions": {
                        "accept": {"payoffs": [9, 1]},
                        "reject": {"payoffs": [0, 0]}
                    }
                },
                "offer_5-5": {
                    "id": "respond_5-5",
                    "player": 1,
                    "actions": {
                        "accept": {"payoffs": [5, 5]},
                        "reject": {"payoffs": [0, 0]}
                    }
                },
                "offer_1-9": {
                    "id": "respond_1-9",
                    "player": 1,
                    "actions": {
                        "accept": {"payoffs": [1, 9]},
                        "reject": {"payoffs": [0, 0]}
                    }
                }
            }
        }
    }

    solution = solve_game(ultimatum_game)
    print(json.dumps(solution, indent=2))
