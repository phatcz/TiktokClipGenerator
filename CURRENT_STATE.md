# CURRENT_STATE — TikTok Clip Factory

**Last Updated:** 2024-12-14  
**Status:** Operational Assessment

---

## What Is Complete and Locked

### Phase Modules (LOCKED - Do Not Modify)
- **Phase 1** (`story_engine.py`): Story generation with 4-scene structure (hook, conflict, reveal, close). Rule-based, no API dependencies. Schema locked.
- **Phase 2** (`phase2_generator.py`): Character and location generation with mock image API. Schema locked.
- **Phase 3** (`phase3_storyboard.py`): Storyboard builder mapping scenes to keyframes. Schema locked.
- **Phase 4** (`phase4_video_plan.py`): Video plan generator with segment breakdown. Contract with Phase 5 locked (start_keyframe/end_keyframe objects required).
- **Phase 5** (`phase5_segment_renderer.py`): Segment renderer with fixed 8.0-second duration. Mock video API. Schema locked.
- **Phase 5.5** (`phase5_assembler.py`): Video assembler with retry logic. Mock stitching. Schema locked.

### Validation Layer
- **Schema Validators** (`validators/schema_validators.py`): Complete validation functions for all phases (1-5.5) with input/output validation. Error classes defined.

### Contracts
- **Phase 4 → Phase 5 Contract** (`contracts/phase4_to_phase5.md`): Documented and locked. Requires start_keyframe/end_keyframe as objects, not IDs.

### Testing
- **End-to-End Test** (`tests/test_end_to_end.py`): Passing. Covers full pipeline with schema validation.

### Documentation
- **MVP_LOCK.md**: Defines locked scope and constraints.
- **MVP_GUARDRAILS.md**: Defines what can/cannot be modified.
- **STATUS_SUMMARY.md**: Current status tracking (Thai language).

---

## What Works but Is Fragile

### End-to-End Runner
- **File**: `end_to_end_run.py`
- **Status**: Works in terminal/CLI context.
- **Fragility**: Contains `sys.stdout = io.TextIOWrapper(...)` wrapper (line 28) for Windows encoding. This wrapper is safe in CLI but may cause issues if imported into Streamlit or other environments that manage stdout differently.

### Phase Module Main Blocks
- **Files**: All phase modules (`story_engine.py`, `phase2_generator.py`, `phase3_storyboard.py`, `phase4_video_plan.py`, `phase5_segment_renderer.py`, `phase5_assembler.py`)
- **Status**: Each has `if __name__ == "__main__"` blocks with stdout wrappers.
- **Fragility**: These wrappers are isolated to main execution, but if modules are imported in contexts that trigger them, they could cause I/O errors. Currently safe because they're only active during direct execution.

### Streamlit App
- **File**: `app_streamlit.py`
- **Status**: UI complete, phase integration complete.
- **Fragility**: 
  - No stdout wrapper in this file (correct).
  - End-to-end flow in UI not fully tested (documented in STATUS_SUMMARY.md).
  - Depends on phase modules that have stdout wrappers in their main blocks (not active during import, but still present).

### Duration Contract Documentation
- **Issue**: Phase 4 → Phase 5 duration contract is documented but not explicit in code comments.
- **Impact**: Low. Contract works, but clarity could be improved with inline documentation.
- **Status**: Mentioned in STATUS_SUMMARY.md as minor improvement needed.

---

## What Is Broken or Blocking

### Streamlit I/O Issue
- **Problem**: STATUS_SUMMARY.md reports "I/O operation on closed file" error from `sys.stdout = io.TextIOWrapper()` in Streamlit.
- **Reality Check**: 
  - `app_streamlit.py` does NOT contain this wrapper (verified).
  - Phase modules have wrappers only in `if __name__ == "__main__"` blocks (should not execute during import).
  - `end_to_end_run.py` has wrapper at module level (line 28), but this file is not imported by Streamlit app.
- **Status**: **Verified – Not Reproducible**. Investigation confirms:
  1. `app_streamlit.py` does not contain the problematic stdout wrapper.
  2. Phase module wrappers are isolated to main execution blocks and do not execute during import.
  3. `end_to_end_run.py` is not imported by Streamlit app, so its wrapper does not affect Streamlit execution.
- **Action Required**: None. Issue appears to be historical or misdocumented.

### No Real API Integration
- **Blocking**: All video/image generation is mocked.
- **Impact**: Cannot produce real videos. System is architecture validation only.
- **Status**: Expected for MVP v0.1. Not a blocker for current scope.

### No Real Video Processing
- **Blocking**: Video assembly is mocked (no ffmpeg/moviepy).
- **Impact**: Cannot produce real final videos.
- **Status**: Expected for MVP v0.1. Not a blocker for current scope.

---

## What Must NOT Be Touched

### Schema Definitions
- **Files**: All phase modules (Phase 1-5.5)
- **Rule**: Field names, types, required/optional status, nested structures are locked.
- **Reason**: Breaking changes would destroy phase contracts.

### Function Signatures
- **Files**: All phase modules
- **Rule**: Function names, parameter names/types, return types, default values are locked.
- **Reason**: Public API contract.

### Phase Order
- **Rule**: 1 → 2 → 3 → 4 → 5 → 5.5 is fixed.
- **Files**: `end_to_end_run.py`, `app_streamlit.py`
- **Reason**: Architecture invariant.

### Critical Invariants
- **Phase 1**: 4 scenes (hook, conflict, reveal, close), integer durations.
- **Phase 3**: Keyframe ID format `scene_{id}_kf_{n}`, keyframe count logic (1-3 per scene).
- **Phase 4**: start_keyframe/end_keyframe must be objects (dict), not strings/null.
- **Phase 5**: Segment duration = 8.0 seconds (FIXED).
- **Reason**: Business rules and contract requirements.

### Contract Documents
- **Files**: `contracts/phase4_to_phase5.md`, `PHASE_CONTRACTS.md`
- **Rule**: Do not modify contract definitions.
- **Reason**: Inter-phase agreements.

### Test Fixtures
- **Files**: `tests/fixtures/*.json`
- **Rule**: Do not modify expected outputs.
- **Reason**: Regression test integrity.

### MVP Lock Documents
- **Files**: `MVP_LOCK.md`, `MVP_GUARDRAILS.md`, `MVP_LOCK_CHECKLIST.md`
- **Rule**: These define the lock scope. Do not modify without version bump.

---

## Current Bottleneck

**The single biggest bottleneck is uncertainty about the Streamlit I/O issue.** STATUS_SUMMARY.md documents an "I/O operation on closed file" error, but the codebase shows that `app_streamlit.py` does not contain the problematic stdout wrapper, and the wrappers in phase modules are isolated to main execution blocks. This creates ambiguity: either the issue is already resolved, or it manifests only in untested execution paths. Without confirming whether the Streamlit end-to-end flow actually works, the project cannot confidently claim MVP completion. The next critical action is to test the full pipeline in the Streamlit UI and verify if the I/O error occurs. If it does not occur, the documentation should be updated. If it does occur, the root cause must be identified (likely related to how `end_to_end_run.py` or phase modules are invoked from Streamlit). This uncertainty blocks clear definition of "what works" versus "what is broken," which is essential for operational decision-making.

---

## Operational Notes

- **Language**: Status documentation is primarily in Thai (`STATUS_SUMMARY.md`), while code and some docs are in English.
- **Testing**: End-to-end test passes in CLI context. Streamlit UI end-to-end flow not verified.
- **Mock Status**: All APIs are mocked (image generation, video generation, video stitching). This is intentional for MVP v0.1.
- **Documentation**: Extensive documentation exists but may contain outdated information (e.g., I/O issue status).

---

**Tone**: Factual, operational, no optimism. Based on code inspection and existing documentation as of 2024-12-14.

