# Tests

All test files have been organized in this folder.

## Running Tests

```bash
# From backend directory
cd backend
source ../venv/bin/activate

# Quick validation (recommended)
python tests/test_v2_quick.py

# Full production validation
python tests/validate_production.py

# Specific phase tests
python tests/test_phase1.py
python tests/test_phase2.py
python tests/test_phase3_5phase.py
python tests/test_phase4.py
python tests/test_phase5.py

# Integration tests
python tests/test_integration_345.py
python tests/test_investigator_v2.py

# Component tests
python tests/test_orchestrator.py
python tests/test_packager.py
python tests/test_corpus_loader.py
```

## Test Files

### Core Tests
- `test_v2_quick.py` - Quick 2-cycle validation (recommended for development)
- `validate_production.py` - Full production scenario test
- `test_investigator_v2.py` - Complete 3-cycle test suite

### Phase Tests
- `test_phase1.py` - Data models validation
- `test_phase2.py` - Gemini client + config + utils
- `test_phase3_5phase.py` - 5-phase investigator (legacy)
- `test_phase4.py` - Evidence pipeline
- `test_phase5.py` - Orchestrator
- `test_phase6.py` - LangGraph wiring
- `test_phase7.py` - FastAPI endpoints

### Component Tests
- `test_orchestrator.py` - Orchestrator functions
- `test_packager.py` - Evidence packager
- `test_corpus_loader.py` - Corpus loading
- `test_evidence_search.py` - Evidence search
- `test_batch_tagging.py` - Batch evidence tagging

### Integration Tests
- `test_integration_345.py` - Phases 3-4-5 integration
- `test_modules.py` - Module imports
- `test_logging.py` - Logging configuration

### Feature Tests
- `test_score_elimination.py` - Score-based elimination
- `test_corpus_only.py` - Corpus-only operations

## Notes

- All tests now use `sys.path` to import from parent directory
- Run from `backend/` directory, not from `tests/` directory
- Virtual environment must be activated
- Check logs in `backend/logs/` for detailed output
