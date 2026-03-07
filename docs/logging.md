# Logging System

## Overview

Basic logging system to track investigation progress and debug issues.

## Configuration

Location: `backend/utils/logger.py`

Features:
- Console output with timestamps (HH:MM:SS format)
- File logging with full timestamps (YYYY-MM-DD HH:MM:SS format)
- Automatic log file creation: `backend/logs/investigation_YYYYMMDD_HHMMSS.log`
- Component-based logging (investigator, packager, gemini)

## Usage

```python
from utils.logger import get_logger

logger = get_logger("component_name")

logger.info("Key event or metric")
logger.warning("Potential issue")
logger.error("Error with details")
```

## What's Logged

### Investigator (`investigator`)
- Cycle start with entity and input counts
- Each phase start (Phase 1-5)
- Hypothesis generation/scoring results
- Elimination results (evidence-based + score-based counts)
- Forward simulation generation
- Evidence requests
- Compression results
- Token usage per phase
- Cycle completion summary

### Evidence Packager (`packager`)
- Evidence gathering start
- Corpus loading results (structural + empirical counts)
- Evidence limiting (30 observation max)
- Gemini tagging API call
- Tagging results

### Gemini Client (`gemini`)
- API call attempts (1/3, 2/3, 3/3)
- API success with token counts (input, output, reasoning)
- API failures with error messages
- Fallback warnings

## Log Levels

- **INFO**: Normal operation events (most common)
- **WARNING**: Potential issues (e.g., empty tagging results, fallback usage)
- **ERROR**: Failures (e.g., API errors, retries)

## Log Files

Location: `backend/logs/`

- Automatically created per investigation run
- Timestamped filenames: `investigation_20260307_184302.log`
- Ignored by git (in .gitignore)

## Example Output

### Console
```
18:43:02 | INFO    | Starting logging test
18:43:02 | INFO    | Loaded 25 structural observations
```

### File
```
2026-03-07 18:43:02 | INFO    | test | Starting logging test
2026-03-07 18:43:02 | INFO    | test | Loaded 25 structural observations
```

## Disabling File Logging

If you only want console output:

```python
from utils.logger import setup_logger

logger = setup_logger("component_name", log_to_file=False)
```
