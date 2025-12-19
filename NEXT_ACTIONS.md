# NEXT_ACTIONS — Execution Plan

## EP S01 — Demo Stabilization

### Priority 1: Fix Streamlit I/O Error

**Goal:** Remove the `sys.stdout` wrapper that causes "I/O operation on closed file" error in Streamlit environment.

**Why this matters:** This error prevents the Streamlit app from running properly. The demo cannot be executed until this is fixed.

**Files allowed to touch:**
- `app_streamlit.py` (line 16 area - remove or comment out sys.stdout wrapper)

**Action:**
1. Open `app_streamlit.py`
2. Locate the `sys.stdout = io.TextIOWrapper(...)` assignment (around line 16)
3. Remove or comment out this line
4. Verify Streamlit app can start without errors
5. Update `CURRENT_STATE.md` to mark this as complete

**Success criteria:**
- `streamlit run app_streamlit.py` executes without I/O errors
- App loads in browser at `http://localhost:8501`
- No console errors related to closed file operations

---

### Priority 2: Verify End-to-End Flow in Streamlit UI

**Goal:** Test that all phases (1-5.5) execute successfully through the Streamlit interface.

**Why this matters:** The backend pipeline works in CLI (`end_to_end_run.py`), but the UI integration must be validated for demo readiness.

**Files allowed to touch:**
- `app_streamlit.py` (only if bugs are found during testing)
- `CURRENT_STATE.md` (update after verification)

**Action:**
1. Start Streamlit app: `streamlit run app_streamlit.py`
2. Execute Phase 1: Generate story with sample inputs
3. Execute Phase 2: Generate characters and locations
4. Select a character and location
5. Execute Phase 3: Build storyboard
6. Execute Phase 4: Generate video plan
7. Execute Phase 5: Render segments
8. Execute Phase 5.5: Assemble final video
9. Verify session state persists correctly between phases
10. Test "Clear" button functionality
11. Update `CURRENT_STATE.md` with test results

**Success criteria:**
- All phases execute without errors in UI
- Data flows correctly between phases
- Session state management works as expected
- UI displays outputs correctly (JSON, metrics, expandable sections)

---

### What Is Explicitly Deferred

**Do NOT work on these until demo is stable:**

1. **API Integration**
   - Google Image Generation API (Phase 2)
   - Google Video Generation API (Phase 5)
   - Video stitching with ffmpeg/moviepy (Phase 5.5)

2. **Infrastructure Changes**
   - Environment variables (.env files)
   - .gitignore updates
   - Deployment configurations
   - Logging/monitoring infrastructure

3. **Schema & Contract Modifications**
   - Phase 1-5.5 schema changes
   - Contract modifications between phases
   - Breaking changes to function signatures

4. **New Features**
   - Additional UI components
   - New phase logic
   - Performance optimizations
   - Error recovery mechanisms

5. **Refactoring**
   - Code structure changes
   - Architecture modifications
   - Phase logic rewrites

---

## Execution Rules

1. **One task at a time**
   - Complete Priority 1 fully before starting Priority 2
   - Do not work on multiple priorities simultaneously

2. **No parallel edits on core phases**
   - Phase 1-5.5 files are LOCKED (per MVP_LOCK.md)
   - Only touch phase files if critical bugs are discovered
   - Document any phase file changes in CURRENT_STATE.md

3. **Update CURRENT_STATE.md after each completed task**
   - Mark task as complete
   - Document any issues found
   - Update overall project status percentage

4. **Test before marking complete**
   - Verify the fix works
   - Run relevant test commands
   - Check for regressions

5. **Command-like execution**
   - Each action is unambiguous
   - No interpretation needed
   - Clear success criteria

---

## Notes

- All phases (1-5.5) are LOCKED per MVP_LOCK.md
- Backend pipeline works in CLI (`end_to_end_run.py`)
- Focus is on making the demo UI functional
- Mock outputs are expected and acceptable for demo

