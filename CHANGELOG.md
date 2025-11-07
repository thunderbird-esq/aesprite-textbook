# Changelog

All notable changes to the Klutz Workbook Project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed - Code Review and Configuration Issues

#### Architecture & Configuration Improvements (HIGH PRIORITY)
1. **AssetValidator Configuration Refactoring**: Refactored `asset_validator.py` to load configuration from `config/master_config.yaml` instead of hardcoded values, establishing a single source of truth for canvas size, color limits, spine boundaries, rotation limits, and safe zones. Maintains backward compatibility with fallback defaults.

2. **Line Length Standardization**: Standardized all line length configurations to 100 characters across project linting and formatting tools (`.pre-commit-config.yaml`, flake8, pylint, and documentation), eliminating conflicting configurations.

3. **Script Path Corrections**: Updated documentation references in README.md, docs/README.md, and planning documents to reflect actual root-level project structure instead of non-existent `scripts/` directory (4 command examples corrected).

4. **Non-Printable Characters Removed**: Replaced 22 instances of control characters (0x13, 0x17) with proper Unicode characters (✓ U+2713 and ✗ U+2717) across 6 Python files (prompt_generator.py, gemini_integration.py, klutz_compositor.py, nano_banana_integration.py, post_processor.py, quality_assurance.py) for clean cross-platform terminal output.

#### Configuration Consistency Fixes (MEDIUM PRIORITY)
5. **UTF-8 Encoding Issue**: Resolved UTF-8 encoding issue with degree symbol in Gemini integration for proper character handling.

6. **Missing Config Fields**: Added critical missing configuration fields to `config/master_config.yaml` required for AssetValidator refactoring:
   - `technical.spine_width: 462`
   - New `layout` section with `safe_zones` (left, right, top, bottom boundaries)
   - All values maintain backward compatibility with original hardcoded defaults

### Breaking Changes
None - All fixes maintain backward compatibility.

### Migration Guide
No migration needed. All changes are backward compatible:
- AssetValidator configuration loading includes fallback to hardcoded defaults
- Configuration field additions use existing default values
- No API changes or behavioral modifications

### In Progress
- Batch processing optimization
- API rate limiting improvements
- Extended asset library

## [0.1.0] - 2025-11-05

### Added - Documentation Reorganization

#### New Directory Structure
- Created comprehensive `docs/` directory organization
- Added `docs/api/` for API reference documentation
- Added `docs/architecture/` for system design documentation
- Added `docs/curriculum/` for educational content
- Added `docs/design/` for design guidelines
- Added `docs/planning/` for project planning documents
- Added `docs/reviews/` for critical analysis and improvements
- Added `docs/technical/` for implementation details

#### New API Documentation
- `docs/api/api-reference.md` - Complete API reference for all classes and methods
- `docs/api/configuration-guide.md` - YAML schema and configuration documentation
- `docs/api/usage-examples.md` - Code examples for common tasks

#### New Architecture Documentation
- `docs/architecture/system-overview.md` - High-level system architecture
- `docs/architecture/data-flow.md` - Detailed data flow through pipeline
- `docs/architecture/directory-structure.md` - Project organization guide

#### New Documentation Index
- `docs/README.md` - Comprehensive documentation index with navigation
- Updated root `README.md` with links to organized documentation

#### File Organization
- Moved planning documents to `docs/planning/`
- Moved technical implementation chapters to `docs/technical/`
- Moved design documents to `docs/design/`
- Moved criticism and improvement guides to `docs/reviews/`
- Moved curriculum modules to `docs/curriculum/`

#### Project Documentation
- `CHANGELOG.md` - Version history and changes (this file)
- `CONTRIBUTING.md` - Contribution guidelines and standards

### Changed
- Reorganized all markdown files from root into categorized docs/ subdirectories
- Updated README.md with navigation to organized documentation
- Consolidated duplicate files in docs/ root

### Removed
- Deleted empty files (`CLAUDE.md`, `klutz-workbook-project`)
- Removed duplicate files after consolidation
- Cleaned up temporary and merged documentation files from root

### Fixed
- Improved documentation discoverability
- Clarified project structure
- Enhanced navigation between related documents

---

## [0.0.1] - 2025-10-XX (Historical)

### Added - Initial Implementation

#### Core Components
- `klutz_compositor.py` - Main composition engine
- `asset_validator.py` - Period authenticity validation
- `prompt_generator.py` - AI prompt generation
- `post_processor.py` - Print artifact simulation
- `gemini_integration.py` - Gemini API integration
- `nano_banana_integration.py` - nano-banana integration
- `quality_assurance.py` - Quality checks
- `production_monitoring.py` - Metrics and logging
- `performance_optimization.py` - Batch processing
- `deploy_workbook.py` - PDF assembly

#### Features
- Period-accurate (1996) visual styling
- Spiral binding simulation (4:1 pitch)
- Paper texture generation
- CMYK misregistration
- Dot gain simulation
- Hard shadow rendering
- Typography with period fonts
- Color validation (70/20/10 rule)
- Spine dead zone checking
- Layout YAML configuration

#### Assets & Configuration
- Master configuration system (`config/master_config.yaml`)
- Layout YAML schema
- Font files (Chicago, Geneva, Monaco, Tekton)
- Texture generation
- Asset validation rules

#### Documentation (Initial)
- Technical implementation chapters (1-15)
- Design rules and guidelines
- Curriculum modules
- Project planning documents

#### Testing
- Unit test framework
- Integration test suite
- Asset validation tests
- Visual regression testing

---

## Version History

- **0.1.0** (2025-11-05) - Documentation reorganization and cleanup
- **0.0.1** (2025-10-XX) - Initial implementation and core features

---

## Upcoming Releases

### [0.2.0] - Planned
- Enhanced batch processing
- Improved caching system
- Additional font support
- Extended asset library
- Performance optimizations

### [0.3.0] - Planned
- Web interface for layout editing
- Real-time preview
- Collaborative editing features
- Version control integration

### [1.0.0] - Planned
- Complete 20-page workbook
- Full test coverage
- Production-ready pipeline
- Comprehensive documentation
- Publishing toolkit

---

## Notes on Versioning

### Version Number Format: MAJOR.MINOR.PATCH

- **MAJOR** - Incompatible API changes
- **MINOR** - New features, backward compatible
- **PATCH** - Bug fixes, backward compatible

### Release Cadence

- **Patch releases** - As needed for bug fixes
- **Minor releases** - Monthly for new features
- **Major releases** - When API changes require it

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Reporting issues
- Suggesting enhancements
- Submitting pull requests
- Code style requirements
- Testing standards

---

## Links

- **Repository:** [GitHub](https://github.com/yourusername/aesprite-textbook)
- **Documentation:** [docs/](docs/)
- **Issues:** [GitHub Issues](https://github.com/yourusername/aesprite-textbook/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/aesprite-textbook/discussions)

---

*This changelog is maintained by the project team and updated with each release.*
