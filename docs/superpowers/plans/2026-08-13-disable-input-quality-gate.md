# Disable Input Quality Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Disable linguistic input rejection without removing it or changing retrieval.

**Architecture:** A single settings flag controls whether `RootCategoryClassifier` invokes its existing `InputQualityGate`. The active environment disables it; the default remains enabled.

**Tech Stack:** Python 3.12, FastAPI, pytest.

## Global Constraints

- Preserve the API schema validation for empty and overlong input.
- Do not change exact, fuzzy, embedding, fusion, or decision logic.
- Do not change the demo UI.

---

### Task 1: Configurable input quality gate

**Files:**
- Modify: `app/core/config.py`
- Modify: `app/classifier/service.py`
- Modify: `app/main.py`
- Modify: `.env.example`
- Modify: `.env`
- Test: `tests/test_config.py`
- Test: `tests/test_classifier.py`

**Interfaces:**
- Consumes: `DANDAN_INPUT_VALIDATION_ENABLED` boolean environment value.
- Produces: `Settings.input_validation_enabled: bool` and `RootCategoryClassifier(..., input_validation_enabled: bool = True)`.

- [ ] Write tests proving environment parsing and disabled-gate classification.
- [ ] Run focused tests and confirm they fail because the flag is absent.
- [ ] Add the flag, pass it at startup, and guard `require_meaningful`.
- [ ] Set the active environment value to `false`.
- [ ] Run focused and full verification.
- [ ] Restart FastAPI and verify the public UI end to end.
