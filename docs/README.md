# Documentation Index

Welcome to the Klutz Workbook Project documentation! This index organizes all documentation by audience and purpose.

## Quick Navigation

- **[🚀 Getting Started](#getting-started)** - New to the project? Start here
- **[💻 For Developers](#for-developers)** - API, architecture, and implementation
- **[🎨 For Designers](#for-designers)** - Style guides and design rules
- **[📚 For Educators](#for-educators)** - Curriculum and teaching materials
- **[📋 For Project Managers](#for-project-managers)** - Planning and strategy
- **[✅ For Quality Reviewers](#for-quality-reviewers)** - Reviews and improvements

---

## Getting Started

### Essential Reading

1. **[../README.md](../README.md)** - Project overview and quick start
2. **[architecture/system-overview.md](architecture/system-overview.md)** - Understand the system architecture
3. **[api/usage-examples.md](api/usage-examples.md)** - See code examples in action

### First-Time Setup

**Note:** All commands should be run from project root.

```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import yaml; import PIL; print('Ready!')"

# Generate your first spread
python klutz_compositor.py config/layouts/spread_04_05.yaml
```

### Common Tasks

- **Generate a spread:** See [api/usage-examples.md](api/usage-examples.md#example-1-generate-a-single-spread)
- **Validate assets:** See [api/usage-examples.md](api/usage-examples.md#example-4-validate-an-image-asset)
- **Create a layout:** See [api/configuration-guide.md](api/configuration-guide.md#layout-configuration)
- **Batch process:** See [api/usage-examples.md](api/usage-examples.md#example-7-process-entire-workbook)

---

## For Developers

### API & Reference

| Document | Description | Audience |
|----------|-------------|----------|
| [api/api-reference.md](api/api-reference.md) | Complete API for all classes and methods | All developers |
| [api/configuration-guide.md](api/configuration-guide.md) | YAML schema and configuration reference | Layout creators |
| [api/usage-examples.md](api/usage-examples.md) | Code samples for common tasks | Implementers |

### Architecture

| Document | Description | Audience |
|----------|-------------|----------|
| [architecture/system-overview.md](architecture/system-overview.md) | High-level system architecture | System designers |
| [architecture/data-flow.md](architecture/data-flow.md) | Data movement through pipeline | Pipeline developers |
| [architecture/directory-structure.md](architecture/directory-structure.md) | Project organization and file structure | All contributors |

### Implementation Details

| Document | Description |
|----------|-------------|
| [technical/klutz-technical-implementation-1.md](technical/klutz-technical-implementation-1.md) | Compositor implementation |
| [technical/klutz-technical-implementation-2.md](technical/klutz-technical-implementation-2.md) | Asset validator |
| [technical/klutz-technical-implementation-3.md](technical/klutz-technical-implementation-3.md) | Prompt generator |
| [technical/klutz-technical-implementation-4.md](technical/klutz-technical-implementation-4.md) | Post processor |
| [technical/klutz-technical-implementation-5.md](technical/klutz-technical-implementation-5.md) | Gemini integration |
| [technical/klutz-technical-implementation-6.md](technical/klutz-technical-implementation-6.md) | nano-banana integration |
| [technical/klutz-technical-implementation-7.md](technical/klutz-technical-implementation-7.md) | Quality assurance |
| [technical/klutz-technical-implementation-8.md](technical/klutz-technical-implementation-8.md) | Production monitoring |
| [technical/klutz-technical-implementation-9.md](technical/klutz-technical-implementation-9.md) | Performance optimization |
| [technical/klutz-technical-implementation-10.md](technical/klutz-technical-implementation-10.md) | Deployment utilities |
| [technical/klutz-technical-implementation-11.md](technical/klutz-technical-implementation-11.md) | Configuration system |
| [technical/klutz-technical-implementation-12.md](technical/klutz-technical-implementation-12.md) | Typography engine |
| [technical/klutz-technical-implementation-13.md](technical/klutz-technical-implementation-13.md) | Texture generation |
| [technical/klutz-technical-implementation-14.md](technical/klutz-technical-implementation-14.md) | Binding simulation |
| [technical/klutz-technical-implementation-15.md](technical/klutz-technical-implementation-15.md) | Print artifacts |

**Note:** Merged documents (e.g., `klutz-technical-implementation-1and2.md`) combine multiple chapters for easier reading.

**TOC:** [technical/klutz-technical-documentation-toc.md](technical/klutz-technical-documentation-toc.md)

### Development Workflow

```mermaid
graph LR
    A[Create Layout YAML] --> B[Generate Prompts]
    B --> C[Generate Assets]
    C --> D[Validate Assets]
    D --> E[Compose Spread]
    E --> F[Post-Process]
    F --> G[Quality Assurance]
    G --> H[Assemble PDF]
```

See [architecture/data-flow.md](architecture/data-flow.md) for detailed flow diagrams.

---

## For Designers

### Style Guides

| Document | Description | Use When |
|----------|-------------|----------|
| [design/designrules3.md](design/designrules3.md) | Core design constraints and rules | Creating any visual element |
| [design/klutz-press-design.md](design/klutz-press-design.md) | Klutz Press style analysis | Understanding the aesthetic |
| [design/new-stylebook.md](design/new-stylebook.md) | Updated comprehensive style guide | Reference for all design work |
| [design/nickelodeon-goosebumps-design.md](design/nickelodeon-goosebumps-design.md) | 90s aesthetic reference | Period-accurate color and style |

### Key Design Principles

**1. Period Authenticity (1996)**
- No gradients or soft shadows
- Hard-edged graphics only
- MacPaint-style pixel art
- Photographed on film (Kodak Gold 400)

**2. Color Rules (70/20/10)**
- 70% Klutz Primary (Red, Blue, Yellow)
- 20% Nickelodeon Orange (#F57D0D)
- 10% Goosebumps Acid Green (#95C120)

**3. Typography**
- Headlines: Chicago (Macintosh system font)
- Body: Geneva (period-accurate)
- Code: Monaco (monospace)
- Handwriting: Tekton (casual)

**4. Layout Constraints**
- Spine dead zone: X: 1469-1931
- Safe zones: 150px margin
- Max rotation: ±15° (±5° for text)
- 4:1 pitch spiral binding

See [design/designrules3.md](design/designrules3.md) for complete rules.

### Designer Checklist

Before submitting a layout:

- [ ] All colors within 70/20/10 distribution
- [ ] No elements in spine dead zone
- [ ] Rotation within limits
- [ ] Hard shadows only (no blur)
- [ ] Period-accurate fonts
- [ ] No anachronistic terms in prompts
- [ ] Passes asset validator

---

## For Educators

### Curriculum Modules

| Module | Topics | Duration |
|--------|--------|----------|
| [curriculum/AESPRITE-TIER1-MODULE-1.md](curriculum/AESPRITE-TIER1-MODULE-1.md) | Introduction, Setup, Interface | 2 hours |
| [curriculum/AESPRITE-TIER1-MODULE-2.md](curriculum/AESPRITE-TIER1-MODULE-2.md) | Fundamentals, Tools, Layers | 3 hours |
| [curriculum/AESPRITE-TIER1-MODULE-3.md](curriculum/AESPRITE-TIER1-MODULE-3.md) | Advanced Techniques, Animation | 4 hours |
| [curriculum/AESPRITE-TIER1-MODULE-4.md](curriculum/AESPRITE-TIER1-MODULE-4.md) | Applications, Projects, Export | 3 hours |

### Additional Resources

- [curriculum/AESPRITE-TIER1-MODULE1-EXPANDED.md](curriculum/AESPRITE-TIER1-MODULE1-EXPANDED.md) - Expanded Module 1 content
- [curriculum/AESPRITE-TIER1-ADDITIONAL-RESOURCES.md](curriculum/AESPRITE-TIER1-ADDITIONAL-RESOURCES.md) - Extra learning materials

### Teaching Philosophy

The curriculum follows Klutz Press's hands-on philosophy:
- Learn by doing
- Clear step-by-step instructions
- Visual examples throughout
- Fun, engaging tone
- Immediate practical application

### Curriculum PDF

The complete curriculum is also available as a single PDF:
**[../aesprite-curriculum.pdf](../aesprite-curriculum.pdf)**

---

## For Project Managers

### Planning Documents

| Document | Description | Status |
|----------|-------------|--------|
| [planning/gemini-klutz-plan-v2.md](planning/gemini-klutz-plan-v2.md) | Overall project strategy and plan | Active |
| [planning/klutz-workbook-action-plan.md](planning/klutz-workbook-action-plan.md) | Actionable task breakdown | Active |

### Project Phases

**Phase 1: Foundation** (Completed)
- Architecture design
- Core compositor implementation
- Asset validation system

**Phase 2: Generation** (In Progress)
- Prompt generation
- AI integration (Gemini, nano-banana)
- Asset library building

**Phase 3: Production** (Upcoming)
- Batch processing
- Quality assurance automation
- PDF assembly

**Phase 4: Polish** (Planned)
- Performance optimization
- Documentation completion
- Final testing

### Tracking & Metrics

- **Spreads completed:** Track in [../output/spreads/](../output/spreads/)
- **Asset library:** Monitor [../assets/generated/](../assets/generated/)
- **Validation reports:** Review in [../output/validation/](../output/validation/)

---

## For Quality Reviewers

### Review Documents

| Document | Date | Focus |
|----------|------|-------|
| [reviews/criticism-091425.md](reviews/criticism-091425.md) | 2025-09-14 | Detailed critique and analysis |
| [reviews/kimi-improvement-guide.md](reviews/kimi-improvement-guide.md) | Current | Enhancement recommendations |

### Quality Standards

**Period Authenticity**
- No anachronistic visual elements
- Period-accurate hardware and software
- 1996-appropriate terminology

**Visual Quality**
- Hard-edged graphics only
- Correct color distribution
- Proper spine clearance
- Accurate binding simulation

**Technical Quality**
- 300 DPI resolution
- Correct canvas dimensions (3400x2200)
- Proper CMYK artifacts
- Appropriate file sizes

### Review Checklist

Use this checklist when reviewing spreads:

- [ ] **Period Accuracy**
  - [ ] No gradients or soft shadows
  - [ ] No modern UI elements
  - [ ] Period-appropriate fonts
  - [ ] 1996-era photography style

- [ ] **Color Compliance**
  - [ ] 70/20/10 distribution
  - [ ] Nickelodeon orange ≤ 30%
  - [ ] Goosebumps green ≤ 10%

- [ ] **Layout Quality**
  - [ ] No spine intrusion
  - [ ] Safe zone compliance
  - [ ] Proper rotation limits
  - [ ] Binding holes aligned

- [ ] **Print Quality**
  - [ ] CMYK misregistration present
  - [ ] Dot gain applied
  - [ ] Vignette visible
  - [ ] Paper texture evident

See [reviews/kimi-improvement-guide.md](reviews/kimi-improvement-guide.md) for detailed improvement recommendations.

---

## Reading Order Recommendations

### New Contributors

1. [../README.md](../README.md) - Project overview
2. [architecture/system-overview.md](architecture/system-overview.md) - Architecture
3. [api/usage-examples.md](api/usage-examples.md) - Code examples
4. [../CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines

### Implementers

1. [api/api-reference.md](api/api-reference.md) - API documentation
2. [api/configuration-guide.md](api/configuration-guide.md) - Configuration
3. [architecture/data-flow.md](architecture/data-flow.md) - Data flow
4. [technical/](technical/) - Implementation details

### Designers

1. [design/klutz-press-design.md](design/klutz-press-design.md) - Style analysis
2. [design/new-stylebook.md](design/new-stylebook.md) - Style guide
3. [design/designrules3.md](design/designrules3.md) - Design rules
4. [api/configuration-guide.md](api/configuration-guide.md) - Layout YAML

### Reviewers

1. [reviews/criticism-091425.md](reviews/criticism-091425.md) - Current critique
2. [reviews/kimi-improvement-guide.md](reviews/kimi-improvement-guide.md) - Improvements
3. [design/designrules3.md](design/designrules3.md) - Quality standards

---

## Contributing to Documentation

### Adding New Documentation

1. Choose the appropriate category directory
2. Follow the existing document structure
3. Add frontmatter (title, date, status)
4. Update this index (docs/README.md)
5. Update main README.md if applicable
6. Submit pull request

### Documentation Standards

**Frontmatter:**
```markdown
---
title: Document Title
date: YYYY-MM-DD
status: Draft | Active | Deprecated
---
```

**Structure:**
- Use clear heading hierarchy (H1 → H2 → H3)
- Include table of contents for long documents
- Add code examples where relevant
- Link to related documents
- Use consistent formatting

**Style:**
- Write in active voice
- Use clear, concise language
- Define technical terms
- Include examples
- Add diagrams where helpful

### Need Help?

- Check existing documentation for patterns
- Review [../CONTRIBUTING.md](../CONTRIBUTING.md)
- Ask in GitHub Discussions
- Open an issue for clarification

---

## Document Status Legend

- **Active** - Current, maintained documentation
- **Draft** - Work in progress, not yet complete
- **Deprecated** - Outdated, kept for reference
- **Archived** - Historical, no longer relevant

---

## Search Tips

### Finding Information

**By Task:**
- "How do I generate a spread?" → [api/usage-examples.md](api/usage-examples.md)
- "What colors can I use?" → [design/designrules3.md](design/designrules3.md)
- "How does the pipeline work?" → [architecture/data-flow.md](architecture/data-flow.md)
- "What's the YAML schema?" → [api/configuration-guide.md](api/configuration-guide.md)

**By Role:**
- Developer → [api/](api/) and [architecture/](architecture/)
- Designer → [design/](design/)
- Educator → [curriculum/](curriculum/)
- Manager → [planning/](planning/)
- Reviewer → [reviews/](reviews/)

**By Component:**
- Compositor → [technical/klutz-technical-implementation-1.md](technical/klutz-technical-implementation-1.md)
- Validator → [technical/klutz-technical-implementation-2.md](technical/klutz-technical-implementation-2.md)
- Typography → [technical/klutz-technical-implementation-12.md](technical/klutz-technical-implementation-12.md)
- Binding → [technical/klutz-technical-implementation-14.md](technical/klutz-technical-implementation-14.md)

---

## Frequently Accessed

**Quick Links:**
- [API Reference](api/api-reference.md)
- [Configuration Guide](api/configuration-guide.md)
- [System Overview](architecture/system-overview.md)
- [Design Rules](design/designrules3.md)
- [Usage Examples](api/usage-examples.md)

**Project Files:**
- [Main README](../README.md)
- [Contributing Guide](../CONTRIBUTING.md)
- [Changelog](../CHANGELOG.md)
- [Requirements](../requirements.txt)

---

*Last Updated: 2025-11-05*
*Documentation Version: 1.0*
