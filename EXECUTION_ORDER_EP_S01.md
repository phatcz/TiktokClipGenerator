# EXECUTION_ORDER_EP_S01 — Fix Streamlit I/O Error

## Task Name

**EP S01 - Priority 1: Fix Streamlit I/O Error**

Remove the `sys.stdout` wrapper that causes "I/O operation on closed file" error in Streamlit environment.

---

## Allowed Files

**Primary file:**
- `app_streamlit.py` (specifically around line 16 area, if the wrapper exists)

**Documentation update (after completion):**
- `CURRENT_STATE.md` (to mark task as complete)

**Do NOT modify:**
- Phase modules (Phase 1-5.5) - these are LOCKED per MVP_LOCK.md
- `end_to_end_run.py` - not imported by Streamlit app
- Any other files not explicitly listed above

---

## Step-by-Step Execution Plan

### Step 1: Verify the Issue Exists
1. Open `app_streamlit.py` in editor
2. Search for `sys.stdout` assignment
3. Search for `io.TextIOWrapper` usage
4. Check around line 16 (and nearby lines) for any stdout wrapper code
5. **Decision point:**
   - If wrapper exists: proceed to Step 2
   - If wrapper does NOT exist: proceed to Step 6 (Verification Only)

### Step 2: Locate the Problematic Code
1. Identify the exact line number(s) containing `sys.stdout = io.TextIOWrapper(...)`
2. Note any surrounding context (comments, conditional statements, etc.)
3. Check if `io` module is imported (should be in imports section if wrapper exists)

### Step 3: Remove or Comment Out the Wrapper
1. Choose one approach:
   - **Option A (Recommended):** Comment out the line using `#`
   - **Option B:** Delete the line entirely
2. If Option A: Add a comment explaining why it was commented (e.g., "Removed for Streamlit compatibility - causes I/O operation on closed file error")
3. Verify no syntax errors introduced

### Step 4: Verify Import Cleanup (if needed)
1. If `io` module was only used for the wrapper, check if it's still needed elsewhere in file
2. If `io` is not used elsewhere, consider removing the import (optional, not required)
3. If `io` is still needed, leave the import

### Step 5: Test Streamlit App Launch
1. Open terminal in project root directory
2. Run command: `streamlit run app_streamlit.py`
3. Observe console output for any errors
4. Wait for browser to open at `http://localhost:8501`
5. Check browser console for errors (F12 → Console tab)
6. Verify app UI loads correctly

### Step 6: Verification Only (if wrapper doesn't exist)
1. Document in CURRENT_STATE.md that wrapper was not found in `app_streamlit.py`
2. Note that issue may be resolved or may exist in different location
3. Mark task as "Verified - No action needed" or "Issue not found, requires investigation"

### Step 7: Update Documentation
1. Open `CURRENT_STATE.md`
2. Locate section "What Is Broken or Blocking" (around line 63)
3. Update the "Streamlit I/O Issue" subsection:
   - If fixed: Move to "What Works but Is Fragile" or mark as resolved
   - If not found: Document findings and mark as "Verified - No issue in app_streamlit.py"
4. Update "Current Bottleneck" section if this was the blocker
5. Save changes

---

## Success Criteria

### Primary Success Criteria
- [ ] `streamlit run app_streamlit.py` executes without I/O errors
- [ ] App loads successfully in browser at `http://localhost:8501`
- [ ] No console errors related to "closed file" or "I/O operation on closed file"
- [ ] Streamlit app UI displays correctly

### Verification Success Criteria
- [ ] Code inspection completed (wrapper found and removed, OR confirmed absent)
- [ ] `CURRENT_STATE.md` updated with results
- [ ] No regressions introduced (app still functions)

---

## What to Do If It Fails

### Scenario 1: Streamlit still shows I/O errors after removing wrapper
**Actions:**
1. Check if wrapper exists in imported modules (phase files) - note that these should NOT be modified per MVP_LOCK.md
2. Check if `end_to_end_run.py` is being imported by Streamlit (should not be)
3. Verify error message details (exact text, stack trace)
4. Check if error occurs at import time or runtime
5. Document findings in `CURRENT_STATE.md` under "What Is Broken or Blocking"
6. Mark task as "Partially Complete - Requires Further Investigation"
7. Note that wrapper may exist in a different location than expected

### Scenario 2: App fails to start after modification
**Actions:**
1. Check for syntax errors introduced during edit
2. Verify Python imports are correct
3. Check if `io` module is still imported but not used (should not cause failure, but verify)
4. Restore original file if modification broke functionality
5. Document issue in `CURRENT_STATE.md`
6. Mark task as "Failed - Rollback Required"

### Scenario 3: Wrapper code not found in app_streamlit.py
**Actions:**
1. Verify file is correct (`app_streamlit.py` in project root)
2. Search entire file for `sys.stdout` to confirm absence
3. Check if issue is documented elsewhere (may already be resolved)
4. Update `CURRENT_STATE.md` to reflect that wrapper does not exist in this file
5. Mark task as "Verified - No Action Needed" or "Issue Not Found"
6. Note that error may originate from different source (requires investigation)

### Scenario 4: Testing reveals different errors (unrelated to I/O)
**Actions:**
1. Document the actual error(s) encountered
2. Determine if errors are pre-existing or newly introduced
3. If pre-existing: note in `CURRENT_STATE.md` under appropriate section
4. If newly introduced: investigate cause, restore if necessary
5. Mark task status based on whether I/O error is resolved (even if other errors exist)

### General Failure Protocol
1. **DO NOT** modify phase modules (Phase 1-5.5) - these are LOCKED
2. **DO NOT** make additional changes beyond scope of this task
3. **DO** document all findings in `CURRENT_STATE.md`
4. **DO** preserve original file state if rollback is needed
5. **DO** mark task status clearly (Complete, Partial, Failed, Verified)

---

## Context Notes

- This task addresses Priority 1 from NEXT_ACTIONS.md
- The issue is reported to cause "I/O operation on closed file" error in Streamlit
- CURRENT_STATE.md notes uncertainty about whether issue actually exists in `app_streamlit.py`
- Phase modules and `end_to_end_run.py` have stdout wrappers, but those are in `if __name__ == "__main__"` blocks and should not execute when imported
- Focus is on making Streamlit UI functional for demo purposes
- All phases (1-5.5) are LOCKED per MVP_LOCK.md - do not modify

---

## Execution Rules

1. **One change at a time** - Make only the necessary modification to fix the I/O error
2. **Test immediately** - Verify fix works before marking complete
3. **Document changes** - Update CURRENT_STATE.md with results
4. **No scope creep** - Do not fix other issues or make improvements beyond this task
5. **Preserve functionality** - Ensure Streamlit app still works after modification
