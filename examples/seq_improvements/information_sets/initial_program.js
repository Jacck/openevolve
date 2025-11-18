/**
 * Information Sets for Sequential Games
 *
 * This program adds support for information sets to enable modeling
 * imperfect information games with common knowledge.
 *
 * Goal: Allow nodes to be grouped into information sets where players
 * cannot distinguish between nodes in the same set.
 */

// EVOLVE-BLOCK-START
/**
 * Data structure for representing information sets in a game tree.
 *
 * An information set groups together decision nodes that are indistinguishable
 * to the player making the decision. This is essential for modeling:
 * - Simultaneous moves (players don't observe each other's actions)
 * - Imperfect information (players don't know the full history)
 * - Common knowledge games (what players know about what others know)
 *
 * @param {Object} gameTree - The game tree structure
 * @returns {Object} Enhanced game tree with information set support
 */
function addInformationSets(gameTree) {
    // Create a deep copy to avoid mutating the original
    const enhanced = JSON.parse(JSON.stringify(gameTree));

    // Add information set tracking
    const informationSets = {};

    // Iterate through nodes to identify potential information sets
    for (const [nodeId, node] of Object.entries(enhanced)) {
        if (!node.payoffs) { // Decision nodes only
            // Initialize information set if not already assigned
            if (!node.informationSet) {
                // By default, each node is in its own information set
                node.informationSet = `IS_${nodeId}`;
            }

            // Track information sets
            if (!informationSets[node.informationSet]) {
                informationSets[node.informationSet] = {
                    player: node.player,
                    nodes: [],
                    actions: new Set()
                };
            }

            informationSets[node.informationSet].nodes.push(nodeId);

            // Collect all possible actions in this information set
            if (node.actions) {
                Object.keys(node.actions).forEach(action => {
                    informationSets[node.informationSet].actions.add(action);
                });
            }
        }
    }

    // Validate information sets
    for (const [setId, setData] of Object.entries(informationSets)) {
        // All nodes in an information set must have the same player
        const players = new Set(setData.nodes.map(nid => enhanced[nid].player));
        if (players.size > 1) {
            throw new Error(`Information set ${setId} contains nodes with different players`);
        }

        // All nodes in an information set should have the same actions available
        const actionArrays = setData.nodes.map(nid =>
            Object.keys(enhanced[nid].actions || {}).sort()
        );

        const firstActions = JSON.stringify(actionArrays[0]);
        const allSame = actionArrays.every(arr => JSON.stringify(arr) === firstActions);

        if (!allSame) {
            console.warn(`Warning: Information set ${setId} has nodes with different actions`);
        }
    }

    // Add metadata to enhanced tree
    enhanced._informationSets = informationSets;

    return enhanced;
}

/**
 * Group nodes into an information set manually
 *
 * @param {Object} gameTree - The game tree
 * @param {Array<string>} nodeIds - Array of node IDs to group
 * @param {string} setName - Name for the information set
 * @returns {Object} Updated game tree
 */
function groupNodesIntoInformationSet(gameTree, nodeIds, setName) {
    const enhanced = JSON.parse(JSON.stringify(gameTree));

    // Validate that all nodes exist and belong to the same player
    let player = null;
    for (const nodeId of nodeIds) {
        if (!enhanced[nodeId]) {
            throw new Error(`Node ${nodeId} does not exist`);
        }
        if (enhanced[nodeId].payoffs) {
            throw new Error(`Cannot add terminal node ${nodeId} to information set`);
        }
        if (player === null) {
            player = enhanced[nodeId].player;
        } else if (enhanced[nodeId].player !== player) {
            throw new Error(`All nodes in information set must belong to same player`);
        }

        // Assign information set
        enhanced[nodeId].informationSet = setName;
    }

    return enhanced;
}

/**
 * Solve game with information sets using Perfect Bayesian Equilibrium
 * (Simplified version - assumes all nodes in info set have same optimal action)
 *
 * @param {Object} gameTree - Game tree with information sets
 * @param {string} rootId - Root node ID
 * @returns {Object} Solution with strategies and beliefs
 */
function solveWithInformationSets(gameTree, rootId) {
    // First, add information sets if not already present
    const enhanced = gameTree._informationSets ? gameTree : addInformationSets(gameTree);

    const solution = {
        strategies: {},
        beliefs: {},
        values: {},
        equilibriumPath: [],
        terminalPayoffs: null
    };

    // Compute backward induction with belief tracking
    function computeNodeValue(nodeId, beliefState = {}) {
        const node = enhanced[nodeId];

        // Base case: terminal node
        if (node.payoffs) {
            solution.values[nodeId] = node.payoffs;
            return node.payoffs;
        }

        // Get information set
        const infoSet = node.informationSet || `IS_${nodeId}`;

        // Track beliefs at this information set
        if (!solution.beliefs[infoSet]) {
            solution.beliefs[infoSet] = {};
        }

        // For nodes in the same information set, we need to compute expected values
        const infoSetData = enhanced._informationSets[infoSet];
        const nodesInSet = infoSetData ? infoSetData.nodes : [nodeId];

        const player = node.player;
        const playerIndex = getPlayerIndex(player);

        let bestAction = null;
        let bestValue = null;
        let bestPayoffs = null;

        // Evaluate each action
        for (const [action, nextNodeId] of Object.entries(node.actions)) {
            const nextPayoffs = computeNodeValue(nextNodeId, beliefState);

            // Player chooses action that maximizes their expected payoff
            if (bestValue === null || nextPayoffs[playerIndex] > bestValue) {
                bestValue = nextPayoffs[playerIndex];
                bestAction = action;
                bestPayoffs = nextPayoffs;
            }
        }

        // Store strategy for this information set (not just this node)
        solution.strategies[infoSet] = bestAction;
        solution.values[nodeId] = bestPayoffs;

        return bestPayoffs;
    }

    // Helper function to get player index
    function getPlayerIndex(player) {
        if (player.includes('1') || player.toLowerCase().includes('p1') ||
            player.toLowerCase().includes('entrant') ||
            player.toLowerCase().includes('proposer') ||
            player.toLowerCase().includes('leader')) {
            return 0;
        }
        return 1;
    }

    // Compute solution
    const finalPayoffs = computeNodeValue(rootId);
    solution.terminalPayoffs = finalPayoffs;

    // Trace equilibrium path (simplified for info sets)
    function tracePath(nodeId) {
        const node = enhanced[nodeId];

        if (node.payoffs) {
            return [{ nodeId, type: 'terminal', payoffs: node.payoffs }];
        }

        const infoSet = node.informationSet || `IS_${nodeId}`;
        const action = solution.strategies[infoSet];
        const nextNodeId = node.actions[action];

        return [
            { nodeId, player: node.player, action, informationSet: infoSet },
            ...tracePath(nextNodeId)
        ];
    }

    solution.equilibriumPath = tracePath(rootId);

    return solution;
}
// EVOLVE-BLOCK-END

// Export functions for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        addInformationSets,
        groupNodesIntoInformationSet,
        solveWithInformationSets
    };
}
