# implement-common-knowledge

**Description:** Add common knowledge hierarchy tracking to game theory applications to model "I know that you know that I know..." scenarios.

**Category:** Game Theory / Advanced Features

**Requires:** `add-information-sets` skill (prerequisite)

---

## Overview

Common knowledge is fundamental in game theory for modeling:
- **Mutual knowledge**: "I know X and you know X"
- **Higher-order knowledge**: "I know that you know that I know X"
- **Common knowledge**: Everyone knows X, everyone knows everyone knows X, ad infinitum
- **Rationality assumptions**: Players are rational, know others are rational, etc.

## Problem

Standard game solvers don't track knowledge hierarchies:

```javascript
// ❌ No knowledge tracking
const game = {
  "node1": { player: "P1", actions: {...} }
};
// What does P1 know at this node?
// What does P1 know about P2's knowledge?
// This information is implicit and untracked!
```

## Solution: Knowledge State Tracking

### Core Data Structure

```javascript
const knowledgeState = {
  nodeId: "n1",
  activePlayer: "P1",

  // Level 0: What actually happened
  history: ["P1:Left", "P2:Up"],

  // Level 1: What each player knows
  knowledge: {
    "P1": {
      possibleHistories: [["P1:Left", "P2:Up"], ["P1:Left", "P2:Down"]],
      informationSet: "IS_P1_1"
    },
    "P2": {
      possibleHistories: [["P1:Left", "P2:Up"]],
      informationSet: "IS_P2_1"
    }
  },

  // Level 2: What P1 knows about what P2 knows
  secondOrderKnowledge: {
    "P1_about_P2": {
      // P1's belief about P2's possible histories
      believedPossibleHistories: [["P1:Left", "P2:Up"]]
    },
    "P2_about_P1": {
      believedPossibleHistories: [["P1:Left", "P2:Up"], ["P1:Left", "P2:Down"]]
    }
  },

  // Common knowledge: Facts known by all, known to be known by all, etc.
  commonKnowledge: {
    gameStructure: true,  // Everyone knows the game tree
    rationality: true,    // Everyone knows everyone is rational
    payoffs: true,        // Everyone knows all payoffs
    publicHistory: ["P1:Left"]  // Publicly observed moves
  }
};
```

### Implementation Functions

```javascript
/**
 * Initialize knowledge state at game start
 */
function initializeKnowledgeState(gameTree, rootId) {
    return {
        currentNode: rootId,
        history: [],
        playerKnowledge: {},
        commonKnowledge: {
            gameStructure: gameTree,
            rationality: true,
            payoffs: extractAllPayoffs(gameTree)
        },
        knowledgeDepth: 3  // Track up to 3 levels of "I know that you know..."
    };
}

/**
 * Update knowledge after a move
 */
function updateKnowledge(knowledgeState, move, observability) {
    const newState = JSON.parse(JSON.stringify(knowledgeState));

    // Add to actual history
    newState.history.push(move);

    // Determine who observed this move
    for (const player of getAllPlayers(newState)) {
        if (observability[player]) {
            // Player observed the move - update their knowledge
            if (!newState.playerKnowledge[player]) {
                newState.playerKnowledge[player] = {
                    observedHistory: [],
                    possibleStates: []
                };
            }
            newState.playerKnowledge[player].observedHistory.push(move);
        } else {
            // Player didn't observe - their possible states branch
            updatePossibleStates(newState, player, move);
        }
    }

    // Update common knowledge (if move was public)
    if (isPublic(observability)) {
        newState.commonKnowledge.publicHistory = newState.commonKnowledge.publicHistory || [];
        newState.commonKnowledge.publicHistory.push(move);
    }

    return newState;
}

/**
 * Check if fact is common knowledge
 */
function isCommonKnowledge(knowledgeState, fact, depth = Infinity) {
    // Fact is common knowledge if:
    // 1. All players know it
    // 2. All players know that all players know it
    // 3. ... (iterate to specified depth)

    let currentDepth = 0;
    let knownByAll = true;

    while (currentDepth < depth && knownByAll) {
        for (const player of getAllPlayers(knowledgeState)) {
            if (!playerKnows(knowledgeState, player, fact, currentDepth)) {
                knownByAll = false;
                break;
            }
        }
        currentDepth++;
    }

    return knownByAll;
}

/**
 * Get what player knows about another player's knowledge
 */
function getBeliefAboutBelief(knowledgeState, observer, target, fact) {
    // What does 'observer' believe that 'target' believes about 'fact'?

    const observerKnowledge = knowledgeState.playerKnowledge[observer];
    if (!observerKnowledge) return null;

    // For each possible state from observer's perspective
    const beliefs = [];
    for (const possibleState of observerKnowledge.possibleStates) {
        // In that possible state, what would target believe?
        const targetBeliefInState = playerKnows(possibleState, target, fact);
        beliefs.push(targetBeliefInState);
    }

    return beliefs;
}

/**
 * Compute equilibrium with common knowledge constraints
 */
function solveWithCommonKnowledge(gameTree, rootId, commonKnowledgeAssumptions) {
    // Initialize knowledge tracking
    let knowledgeState = initializeKnowledgeState(gameTree, rootId);

    // Apply common knowledge assumptions
    for (const assumption of commonKnowledgeAssumptions) {
        knowledgeState.commonKnowledge[assumption.key] = assumption.value;
    }

    // Solve recursively, maintaining knowledge consistency
    function solveNode(nodeId, currentKnowledge) {
        const node = gameTree[nodeId];

        if (node.payoffs) {
            return { payoffs: node.payoffs, knowledge: currentKnowledge };
        }

        const player = node.player;
        const infoSet = node.informationSet || `IS_${nodeId}`;

        // What does the player know at this point?
        const playerKnowledge = getCurrentPlayerKnowledge(currentKnowledge, player, infoSet);

        // Compute best response given their knowledge
        let bestAction = null;
        let bestValue = -Infinity;

        for (const [action, nextNode] of Object.entries(node.actions)) {
            // Update knowledge after this action
            const observability = getActionObservability(gameTree, action);
            const newKnowledge = updateKnowledge(currentKnowledge,
                { player, action, node: nodeId },
                observability
            );

            const result = solveNode(nextNode, newKnowledge);
            const value = result.payoffs[getPlayerIndex(player)];

            if (value > bestValue) {
                bestValue = value;
                bestAction = action;
            }
        }

        return {
            action: bestAction,
            payoffs: bestValue,
            knowledge: currentKnowledge
        };
    }

    return solveNode(rootId, knowledgeState);
}

// Helper functions
function getAllPlayers(knowledgeState) {
    return Object.keys(knowledgeState.playerKnowledge);
}

function isPublic(observability) {
    return Object.values(observability).every(v => v === true);
}

function playerKnows(knowledgeState, player, fact, depth = 0) {
    // Simplified: check if fact is consistent with player's knowledge
    const playerKnowledge = knowledgeState.playerKnowledge[player];
    if (!playerKnowledge) return false;

    // Implementation depends on fact type
    return checkFactConsistency(playerKnowledge, fact);
}

function checkFactConsistency(knowledge, fact) {
    // Check if fact is true in all possible states the player considers possible
    return knowledge.possibleStates.every(state => evaluateFact(state, fact));
}

function evaluateFact(state, fact) {
    // Evaluate if fact is true in given state
    // This is domain-specific
    return true;  // Placeholder
}

function updatePossibleStates(newState, player, move) {
    // Player didn't observe move - multiple states are now possible
    if (!newState.playerKnowledge[player]) {
        newState.playerKnowledge[player] = { possibleStates: [] };
    }
    // Add branching logic here
}

function getCurrentPlayerKnowledge(knowledge, player, infoSet) {
    return knowledge.playerKnowledge[player] || { possibleStates: [] };
}

function getActionObservability(gameTree, action) {
    // Determine which players observe this action
    // Default: all players observe (can be overridden in game tree)
    return { "P1": true, "P2": true };
}

function getPlayerIndex(player) {
    return player === "P1" || player.includes("1") ? 0 : 1;
}

function extractAllPayoffs(gameTree) {
    const payoffs = {};
    for (const [nodeId, node] of Object.entries(gameTree)) {
        if (node.payoffs) {
            payoffs[nodeId] = node.payoffs;
        }
    }
    return payoffs;
}
```

## Example: Selten Game with Common Knowledge

```javascript
// Selten's Entry Deterrence with incomplete information
const seltenGame = {
    "entry": {
        id: "entry",
        player: "Entrant",
        actions: {
            "Enter": "nature",  // Nature determines incumbent type
            "StayOut": "stayOut"
        }
    },
    "nature": {
        id: "nature",
        player: "Nature",
        type: "chance",
        actions: {
            "Strong": "incumbent_strong",  // P(Strong) = 0.3
            "Weak": "incumbent_weak"       // P(Weak) = 0.7
        },
        probabilities: { "Strong": 0.3, "Weak": 0.7 },
        observability: {
            "Entrant": false,  // Entrant doesn't see type!
            "Incumbent": true   // Incumbent knows own type
        }
    },
    "incumbent_strong": {
        id: "incumbent_strong",
        player: "Incumbent",
        informationSet: "Incumbent_AfterEntry",  // Entrant doesn't know which node
        actions: { "Fight": "fight_s", "Accommodate": "acc_s" }
    },
    "incumbent_weak": {
        id: "incumbent_weak",
        player: "Incumbent",
        informationSet: "Incumbent_AfterEntry",  // Same info set!
        actions: { "Fight": "fight_w", "Accommodate": "acc_w" }
    },
    // ... terminal nodes
};

// Common knowledge in this game:
const commonKnowledge = [
    { key: "gameStructure", value: seltenGame },
    { key: "rationality", value: true },
    { key: "priorProbabilities", value: { "Strong": 0.3, "Weak": 0.7 } }
];

// NOT common knowledge:
// - Incumbent's actual type (only known to incumbent)
// - Entrant's entry decision before it happens

// Solve with common knowledge tracking
const solution = solveWithCommonKnowledge(seltenGame, "entry", commonKnowledge);

// Analyze knowledge states
console.log("At incumbent_strong node:");
console.log("  Incumbent knows: Own type is Strong");
console.log("  Entrant knows: Entry occurred, but not incumbent type");
console.log("  Common knowledge: Game structure, priors, rationality");
console.log("  Entrant's belief: P(Strong | entered) = 0.3");
```

## Visualization of Knowledge

```javascript
function visualizeKnowledgeHierarchy(knowledgeState, depth = 3) {
    const hierarchy = [];

    // Level 0: Actual state
    hierarchy.push({
        level: 0,
        description: "Actual History",
        content: knowledgeState.history
    });

    // Level 1: What each player knows
    hierarchy.push({
        level: 1,
        description: "Individual Knowledge",
        content: Object.entries(knowledgeState.playerKnowledge).map(([player, knowledge]) => ({
            player,
            knows: knowledge.observedHistory,
            possibleStates: knowledge.possibleStates.length
        }))
    });

    // Level 2+: Higher order beliefs
    for (let d = 2; d <= depth; d++) {
        const higherOrder = computeHigherOrderBeliefs(knowledgeState, d);
        hierarchy.push({
            level: d,
            description: `Level ${d} Knowledge`,
            content: higherOrder
        });
    }

    return hierarchy;
}

// Render in HTML
function renderKnowledgeHierarchy(hierarchy) {
    return `
        <div class="knowledge-visualization">
            ${hierarchy.map(level => `
                <div class="knowledge-level" data-level="${level.level}">
                    <h4>Level ${level.level}: ${level.description}</h4>
                    <div class="knowledge-content">
                        ${JSON.stringify(level.content, null, 2)}
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}
```

## Integration with Information Sets

This skill builds on `add-information-sets`:

```javascript
// Combine information sets with common knowledge
function enhanceWithCommonKnowledge(gameTreeWithInfoSets) {
    const enhanced = addInformationSets(gameTreeWithInfoSets);

    // For each information set, compute what is/isn't common knowledge
    for (const [setId, setData] of Object.entries(enhanced._informationSets)) {
        setData.commonKnowledge = {
            // What all players in this info set know
            sharedKnowledge: computeSharedKnowledge(setData.nodes),
            // What is NOT common (distinguishes nodes in set)
            privateInformation: computePrivateInformation(setData.nodes)
        };
    }

    return enhanced;
}
```

## Benefits

✅ **Models Selten Games** - Handle incomplete information properly
✅ **Tracks Beliefs** - Know what each player knows at each point
✅ **Enables Signaling** - Model reputation, threats, and signals
✅ **Foundation for Advanced Equilibria** - Sequential, Perfect Bayesian, etc.
✅ **Explicit Reasoning** - Make knowledge assumptions visible

## Related Skills

- **Prerequisite**: `add-information-sets`
- **Next Steps**: `add-chance-nodes`, `upgrade-to-pbe`
- **Visualization**: `visualize-beliefs`, `visualize-knowledge-tree`

---

## Metadata

```yaml
complexity: High
requires: add-information-sets
domain: Game Theory / Epistemology
use_cases:
  - Selten's Entry Deterrence
  - Signaling games
  - Reputation models
  - Incomplete information games
```
