# visualize-information-sets

**Description:** Auto-generate visual representations of information sets in game trees using SVG or Canvas.

**Category:** Game Theory / Visualization

**Requires:** `add-information-sets` skill

---

## Quick Implementation

Add dotted ovals connecting nodes in the same information set:

```javascript
function visualizeInformationSets(svg, layout, gameTree) {
    if (!gameTree._informationSets) return;

    const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7'];
    let colorIndex = 0;

    for (const [setId, setData] of Object.entries(gameTree._informationSets)) {
        if (setData.nodes.length <= 1) continue;  // Skip single-node sets

        const color = colors[colorIndex % colors.length];
        colorIndex++;

        // Get positions of all nodes in this set
        const positions = setData.nodes.map(nid => layout[nid]);

        // Draw dashed ellipse around the nodes
        const { centerX, centerY, radiusX, radiusY } = computeBoundingEllipse(positions);

        const ellipse = document.createElementNS('http://www.w3.org/2000/svg', 'ellipse');
        ellipse.setAttribute('cx', centerX);
        ellipse.setAttribute('cy', centerY);
        ellipse.setAttribute('rx', radiusX + 40);
        ellipse.setAttribute('ry', radiusY + 40);
        ellipse.setAttribute('fill', 'none');
        ellipse.setAttribute('stroke', color);
        ellipse.setAttribute('stroke-width', '2');
        ellipse.setAttribute('stroke-dasharray', '5,5');
        ellipse.setAttribute('opacity', '0.6');
        svg.appendChild(ellipse);

        // Add label
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', centerX);
        text.setAttribute('y', centerY - radiusY - 50);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('font-size', '11');
        text.setAttribute('font-weight', 'bold');
        text.setAttribute('fill', color);
        text.textContent = `${setData.player} cannot distinguish`;
        svg.appendChild(text);
    }
}

function computeBoundingEllipse(positions) {
    const xs = positions.map(p => p.x);
    const ys = positions.map(p => p.y);

    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);

    return {
        centerX: (minX + maxX) / 2,
        centerY: (minY + maxY) / 2,
        radiusX: (maxX - minX) / 2,
        radiusY: (maxY - minY) / 2
    };
}

// Call after drawing tree:
visualizeInformationSets(svg, layout, gameTree);
```

---

## Metadata

```yaml
complexity: Low
lines_of_code: ~50
visual: true
```
