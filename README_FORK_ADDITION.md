# Fork Addition for README.md

Insert this section after the "Why OpenEvolve?" section in README.md to document your Skills Pipeline extension.

---

## 🎨 Skills Pipeline Extension (This Fork)

> **Note**: This fork includes experimental features for creating reusable Claude Skills from evolved solutions. These are not part of the upstream project.

This fork adds a complete pipeline for turning OpenEvolve solutions into reusable skills:

### What's Added

**📦 Claude Skills System** (`.claude/skills/`)
- **add-information-sets.md** - Adds imperfect information support to game theory apps
- **implement-common-knowledge.md** - Knowledge hierarchy tracking
- **visualize-information-sets.md** - Auto-generates visual representations

**🔬 Example: seq Repository Improvements** (`examples/seq_improvements/`)
- Complete evolution setup for adding features to external projects
- Demonstrates applying OpenEvolve to real-world codebases
- End-to-end workflow from analysis to production code

**📚 Documentation**
- **OPENEVOLVE_SKILLS_PIPELINE.md** - Complete pipeline architecture
- **COMPLETE_DEMONSTRATION.md** - Working example with seq repository
- **Developer Skills** - How to apply evolved solutions to production

### Pipeline Workflow

```
1. Identify issues in target project (e.g., seq repository)
   ↓
2. Create OpenEvolve setup (initial_program + evaluator + config)
   ↓
3. Run evolution (LLM-powered search with MAP-Elites)
   ↓
4. Package successful solutions as Claude Skills
   ↓
5. Apply skills to production code in target project
   ↓
6. Commit working changes (demonstrated with seq)
```

### Example Application

**Target**: [seq](https://github.com/Jacck/seq) - Sequential game theory web app

**Issue**: Couldn't model imperfect information games (Selten games, common knowledge)

**Solution**: Evolved information sets support (6/6 tests passing, 1.00 fitness)

**Result**:
- ✅ Applied to production code (+250 lines)
- ✅ New features working in seq repository
- ✅ Packaged as reusable skills for other projects

### Files Structure

```
.claude/skills/              # Reusable Claude Skills
  ├── add-information-sets.md
  ├── implement-common-knowledge.md
  └── visualize-information-sets.md

examples/seq_improvements/   # Cross-project evolution example
  └── information_sets/
      ├── initial_program.js
      ├── evaluator.py
      └── config.yaml

OPENEVOLVE_SKILLS_PIPELINE.md   # Complete documentation
COMPLETE_DEMONSTRATION.md        # Working example
```

### Difference from Upstream

**Upstream OpenEvolve**: Evolves code for optimization/discovery within a project

**This Fork**: Adds ability to:
- Create reusable skills from evolved solutions
- Apply skills across multiple projects
- Package patterns for Claude to reuse
- Document complete workflows

### Usage

See the complete demonstration:
```bash
# View the pipeline documentation
cat OPENEVOLVE_SKILLS_PIPELINE.md

# See working example with seq repository
cat COMPLETE_DEMONSTRATION.md

# Explore the skills
ls .claude/skills/
```

### Status

🧪 **Experimental** - Personal workflow extension, not intended for upstream merge

📖 **Documented** - Complete guides and working examples included

✅ **Working** - Demonstrated with actual commits to seq repository

### Future

These experimental features may be:
- Refined and proposed for upstream contribution
- Kept as separate fork functionality
- Evolved into standalone tools

---

**Upstream**: [algorithmicsuperintelligence/openevolve](https://github.com/algorithmicsuperintelligence/openevolve)

**This Fork**: Adds Claude Skills Pipeline for cross-project evolution

---
