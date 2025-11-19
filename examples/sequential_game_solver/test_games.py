"""
Test game specifications for sequential game solver evaluation.
Contains various canonical games from game theory.
"""

# Centipede Game (simplified 4-round version)
CENTIPEDE_GAME = {
    "num_players": 2,
    "name": "Centipede Game",
    "tree": {
        "id": "round1",
        "player": 0,
        "actions": {
            "take": {"payoffs": [1, 0]},
            "pass": {
                "id": "round2",
                "player": 1,
                "actions": {
                    "take": {"payoffs": [0, 2]},
                    "pass": {
                        "id": "round3",
                        "player": 0,
                        "actions": {
                            "take": {"payoffs": [3, 1]},
                            "pass": {
                                "id": "round4",
                                "player": 1,
                                "actions": {
                                    "take": {"payoffs": [2, 4]},
                                    "pass": {"payoffs": [5, 5]}
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "expected_solution": {
        "equilibrium_payoffs": [1, 0],
        "first_action": "take"
    }
}

# Entry Deterrence Game (Selten)
ENTRY_DETERRENCE_GAME = {
    "num_players": 2,
    "name": "Entry Deterrence",
    "tree": {
        "id": "root",
        "player": 0,  # Entrant
        "actions": {
            "stay_out": {"payoffs": [1, 2]},
            "enter": {
                "id": "incumbent_choice",
                "player": 1,  # Incumbent
                "actions": {
                    "fight": {"payoffs": [-1, -1]},
                    "accommodate": {"payoffs": [2, 1]}
                }
            }
        }
    },
    "expected_solution": {
        "equilibrium_payoffs": [2, 1],
        "first_action": "enter"
    }
}

# Stackelberg Duopoly (simplified discrete quantities)
STACKELBERG_GAME = {
    "num_players": 2,
    "name": "Stackelberg Duopoly",
    "tree": {
        "id": "leader",
        "player": 0,  # Leader firm
        "actions": {
            "low_quantity": {
                "id": "follower_low",
                "player": 1,  # Follower firm
                "actions": {
                    "low": {"payoffs": [4, 4]},
                    "high": {"payoffs": [3, 5]}
                }
            },
            "high_quantity": {
                "id": "follower_high",
                "player": 1,
                "actions": {
                    "low": {"payoffs": [5, 3]},
                    "high": {"payoffs": [2, 2]}
                }
            }
        }
    },
    "expected_solution": {
        "equilibrium_payoffs": [5, 3],
        "first_action": "high_quantity"
    }
}

# Ultimatum Game
ULTIMATUM_GAME = {
    "num_players": 2,
    "name": "Ultimatum Game",
    "tree": {
        "id": "proposer",
        "player": 0,
        "actions": {
            "offer_9-1": {
                "id": "responder_9-1",
                "player": 1,
                "actions": {
                    "accept": {"payoffs": [9, 1]},
                    "reject": {"payoffs": [0, 0]}
                }
            },
            "offer_7-3": {
                "id": "responder_7-3",
                "player": 1,
                "actions": {
                    "accept": {"payoffs": [7, 3]},
                    "reject": {"payoffs": [0, 0]}
                }
            },
            "offer_5-5": {
                "id": "responder_5-5",
                "player": 1,
                "actions": {
                    "accept": {"payoffs": [5, 5]},
                    "reject": {"payoffs": [0, 0]}
                }
            }
        }
    },
    "expected_solution": {
        "equilibrium_payoffs": [9, 1],
        "first_action": "offer_9-1"
    }
}

# Three-player coalition game
THREE_PLAYER_GAME = {
    "num_players": 3,
    "name": "Three-Player Coalition",
    "tree": {
        "id": "player1",
        "player": 0,
        "actions": {
            "propose_12": {
                "id": "player2_choice1",
                "player": 1,
                "actions": {
                    "accept": {
                        "id": "player3_choice1",
                        "player": 2,
                        "actions": {
                            "accept": {"payoffs": [5, 3, 2]},
                            "reject": {"payoffs": [0, 0, 0]}
                        }
                    },
                    "reject": {"payoffs": [0, 0, 0]}
                }
            },
            "propose_13": {
                "id": "player2_choice2",
                "player": 1,
                "actions": {
                    "accept": {"payoffs": [0, 0, 0]},
                    "reject": {
                        "id": "player3_choice2",
                        "player": 2,
                        "actions": {
                            "accept": {"payoffs": [6, 0, 4]},
                            "reject": {"payoffs": [0, 0, 0]}
                        }
                    }
                }
            }
        }
    },
    "expected_solution": {
        "equilibrium_payoffs": [6, 0, 4],
        "first_action": "propose_13"
    }
}

# Deep game tree (tests algorithm efficiency)
def generate_deep_game(depth: int = 10):
    """Generate a deep binary game tree for performance testing."""

    def build_level(level: int, max_depth: int):
        if level == max_depth:
            # Terminal nodes alternate payoffs
            return {"payoffs": [level % 3, (level + 1) % 3]}

        return {
            "id": f"level_{level}",
            "player": level % 2,
            "actions": {
                "left": build_level(level + 1, max_depth),
                "right": build_level(level + 1, max_depth)
            }
        }

    return {
        "num_players": 2,
        "name": f"Deep Game (depth={depth})",
        "tree": build_level(0, depth)
    }


# Complex branching game (tests algorithm with many actions)
WIDE_GAME = {
    "num_players": 2,
    "name": "Wide Branching Game",
    "tree": {
        "id": "root",
        "player": 0,
        "actions": {
            f"action_{i}": {
                "id": f"response_{i}",
                "player": 1,
                "actions": {
                    "accept": {"payoffs": [i, 10 - i]},
                    "reject": {"payoffs": [0, 0]}
                }
            }
            for i in range(11)  # 11 different offers
        }
    },
    "expected_solution": {
        "equilibrium_payoffs": [10, 0],
        "first_action": "action_10"
    }
}

# All test games
ALL_GAMES = [
    CENTIPEDE_GAME,
    ENTRY_DETERRENCE_GAME,
    STACKELBERG_GAME,
    ULTIMATUM_GAME,
    THREE_PLAYER_GAME,
    WIDE_GAME,
]

# Performance test games
PERFORMANCE_GAMES = [
    generate_deep_game(5),
    generate_deep_game(10),
    generate_deep_game(15),
]
