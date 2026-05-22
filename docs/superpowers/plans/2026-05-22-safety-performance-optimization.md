# Safety and Performance Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-subagent-driven-development (recommended) or superpowers-executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Add safer execution controls, clearer confirmation UI, shell alias hardening, reduced rerun side effects, documentation, cache robustness, and targeted performance improvements while preserving the existing Python package architecture.

**Architecture:** Introduce a focused `thefuck.safety` module for risk scoring and rerun policy, extend `CorrectedCommand` with rule metadata, keep final execution controlled through `ui.select_command()`, and harden shell aliases without changing the stdout-to-shell execution contract. Cache and executable lookup improvements remain localized in `thefuck/utils.py`.

**Tech Stack:** Python 2.7+/3.5+ compatible code style, pytest test suite, existing shell integration templates.

---

### Task 1: Command risk metadata and UI confirmation

**Files:**
- Create: `thefuck/safety.py`
- Modify: `thefuck/types.py`
- Modify: `thefuck/ui.py`
- Modify: `thefuck/logs.py`
- Test: `tests/test_safety.py`
- Test: `tests/test_ui.py`
- Test: `tests/test_types.py`

- [x] Add tests for safe, side-effect, and dangerous command metadata.
- [x] Verify tests fail because metadata/risk helpers do not exist.
- [x] Implement risk scoring, rule name propagation, visible rule/side-effect/risk hints, high-risk second confirmation, and side-effect confirmation when global confirmation is disabled.
- [x] Verify focused tests pass.

### Task 2: Side effect exception protection

**Files:**
- Modify: `thefuck/types.py`
- Modify: `thefuck/entrypoints/fix_command.py`
- Test: `tests/test_types.py`
- Test: `tests/entrypoints/test_fix_command.py`

- [x] Add tests proving side effect failures abort command output and fix flow exits non-zero.
- [x] Verify tests fail with current unprotected side effect behavior.
- [x] Wrap side effects, log exceptions, return failure, and have `fix_command()` exit non-zero on failed run.
- [x] Verify focused tests pass.

### Task 3: Shell alias quoting and alias-name validation

**Files:**
- Modify: `thefuck/entrypoints/alias.py`
- Modify: `thefuck/shells/bash.py`
- Modify: `thefuck/shells/zsh.py`
- Modify: `thefuck/shells/fish.py`
- Modify: `thefuck/shells/generic.py`
- Modify: `thefuck/shells/tcsh.py`
- Modify: `thefuck/shells/powershell.py`
- Test: `tests/entrypoints/test_alias.py`
- Test: `tests/shells/test_bash.py`
- Test: `tests/shells/test_zsh.py`
- Test: `tests/shells/test_fish.py`

- [x] Add tests for invalid alias rejection and safer generated shell snippets.
- [x] Verify tests fail on current templates.
- [x] Validate alias names, quote `$@`/`TF_CMD`/history mutations where supported, and reduce unquoted eval surfaces.
- [x] Verify focused tests pass.

### Task 4: Reduce rerun side effects

**Files:**
- Modify: `thefuck/const.py`
- Modify: `thefuck/conf.py`
- Modify: `thefuck/output_readers/rerun.py`
- Modify: `README.md`
- Test: `tests/test_conf.py`
- Test: `tests/output_readers/test_rerun.py`

- [x] Add tests for skipping unsafe reruns by default and allowing opt-in reruns.
- [x] Verify tests fail on current unconditional rerun.
- [x] Add `rerun_safe_only` setting/env parser and use `thefuck.safety` to skip dangerous previous commands before `Popen`.
- [x] Verify focused tests pass.

### Task 5: Cache and executable lookup performance

**Files:**
- Modify: `thefuck/utils.py`
- Test: `tests/test_utils.py`

- [x] Add tests for versioned cache keys, locked access, path-aware excluded prefix checks, and executable de-duplication.
- [x] Verify tests fail against current cache/key/path behavior where applicable.
- [x] Add cache versioning/RLock, robust cache deletion, path-aware prefix matching, and de-duplication while preserving order.
- [x] Verify focused tests pass.

### Task 6: Documentation and final verification

**Files:**
- Modify: `README.md`
- Modify: docs plan file

- [x] Document high-risk confirmation, side-effect confirmation, rerun safety, `--yeah` caveat, and shell alias hardening.
- [x] Run focused pytest suite and syntax checks.
- [x] Run broader available pytest subset when dependencies are installed.
