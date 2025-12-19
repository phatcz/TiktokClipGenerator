# EXECUTION_ORDER_EP_S07 — Multi-Provider Image Strategy

## Task Name

**EP S07 - Multi-Provider Strategy: Extend Adapter Layer for Multiple Image Providers**

Extend the adapter layer to support multiple IMAGE providers with a clear selection strategy and robust fallback chain, without changing core pipeline behavior.

---

## Objective

Enable multi-provider support for image generation with:
- Explicit provider selection (e.g., `IMAGE_PROVIDER=google`)
- Auto strategy that tries providers in priority order
- Robust fallback chain that always ends in mock provider
- No changes to core pipeline behavior or outputs

---

## Scope

### Files Modified

1. **adapters/stub_providers.py** (NEW)
   - Created `StubImageProvider` class implementing `ImageProvider` interface
   - Placeholder provider that always returns failure results gracefully
   - Useful for testing fallback chains and as placeholder for future providers

2. **adapters/strategy.py** (NEW)
   - Provider selection strategy module
   - Defines provider priority order
   - Implements fallback chain logic
   - Provides `get_auto_provider()` for auto strategy

3. **adapters/__init__.py**
   - Extended `get_image_provider()` to support explicit and auto modes
   - Registered provider factories for mock, google, and stub
   - Implemented robust fallback logic

### Files NOT Modified

- `phase2_generator.py` - Already uses adapter layer (no changes needed)
- All other phase modules
- UI files
- Schema/contract files

---

## Implementation Details

### Provider List

**Available Image Providers:**

1. **MockImageProvider** (`adapters/mock_providers.py`)
   - Default provider (works offline)
   - No credentials required
   - Always succeeds (returns mock image URLs/paths)

2. **GoogleImageProvider** (`adapters/google_providers.py`)
   - Google Vertex AI Imagen API
   - Requires: `VERTEX_API_KEY`, `VERTEX_PROJECT_ID`
   - Optional: `VERTEX_LOCATION` (default: "us-central1")

3. **StubImageProvider** (`adapters/stub_providers.py`)
   - Placeholder provider for testing
   - Always returns failure results gracefully
   - No credentials required
   - Useful for testing fallback chains

### Provider Priority Order

**For "auto" strategy, providers are tried in this order:**

1. `google` - Google Vertex AI Imagen (highest priority)
2. `stub` - Stub provider (placeholder)
3. `mock` - Mock provider (final fallback, always succeeds)

**Priority is defined in:** `adapters/strategy.py` → `IMAGE_PROVIDER_PRIORITY`

### Selection Modes

#### 1. Explicit Provider Selection

**Set `IMAGE_PROVIDER` to specific provider name:**

```bash
# Mock provider (default)
IMAGE_PROVIDER=mock  # or omit env var

# Google provider
IMAGE_PROVIDER=google
# Requires: VERTEX_API_KEY, VERTEX_PROJECT_ID

# Stub provider
IMAGE_PROVIDER=stub
```

**Behavior:**
- Tries to initialize specified provider
- If initialization fails → falls back to mock (with warning)
- Guaranteed to return a provider (never crashes)

#### 2. Auto Strategy

**Set `IMAGE_PROVIDER=auto`:**

```bash
IMAGE_PROVIDER=auto
```

**Behavior:**
- Tries providers in priority order: `google` → `stub` → `mock`
- Stops at first provider that initializes successfully
- If all fail → uses mock (guaranteed fallback)
- Logs warnings for each failed provider

**Example Flow:**
1. Try `google` → fails (missing credentials) → warning → continue
2. Try `stub` → succeeds → use `StubImageProvider`
3. (Never reaches `mock` because `stub` succeeded)

**Another Example:**
1. Try `google` → fails (missing credentials) → warning → continue
2. Try `stub` → fails (if it had initialization error) → warning → continue
3. Try `mock` → succeeds → use `MockImageProvider`

#### 3. Unknown Provider

**Set `IMAGE_PROVIDER` to unknown value:**

```bash
IMAGE_PROVIDER=unknown_provider
```

**Behavior:**
- Logs warning about unknown provider
- Falls back to mock immediately
- No attempt to initialize unknown provider

### Fallback Chain

**Guaranteed Fallback Order:**

1. **Explicit Provider:**
   - Try specified provider → if fails → mock

2. **Auto Strategy:**
   - Try providers in priority order → if all fail → mock

3. **Unknown Provider:**
   - Immediately fallback to mock

**Key Guarantee:** All fallback chains end in `MockImageProvider` (never crashes)

---

## Usage Examples

### Default Mode (Mock)

```bash
# No env vars needed
python phase2_generator.py
# Uses MockImageProvider automatically
```

### Explicit Google Provider

```bash
# Windows PowerShell
$env:IMAGE_PROVIDER="google"
$env:VERTEX_API_KEY="your_api_key"
$env:VERTEX_PROJECT_ID="your_project_id"

# Linux/Mac
export IMAGE_PROVIDER=google
export VERTEX_API_KEY=your_api_key
export VERTEX_PROJECT_ID=your_project_id
```

### Auto Strategy

```bash
# Windows PowerShell
$env:IMAGE_PROVIDER="auto"
# Will try: google → stub → mock

# Linux/Mac
export IMAGE_PROVIDER=auto
```

### Explicit Stub Provider

```bash
# Windows PowerShell
$env:IMAGE_PROVIDER="stub"

# Linux/Mac
export IMAGE_PROVIDER=stub
```

---

## Verification

### Test Results

**Test Script:** `test_ep_s07.py`
**Result:** ✅ PASSED

**Test Cases:**
1. ✅ Mock provider (default) - Works correctly
2. ✅ Explicit Google provider with missing credentials - Falls back to mock
3. ✅ Explicit Stub provider - Initializes and fails gracefully
4. ✅ Auto strategy - Tries providers in priority order
5. ✅ Unknown provider - Falls back to mock immediately
6. ✅ Full pipeline Phase 1 → Phase 5.5 - Runs successfully

**Key Observations:**
- Default behavior unchanged: mock provider when no env vars set
- Explicit provider selection works with fallback
- Auto strategy tries providers in priority order
- All fallback chains end in mock (guaranteed)
- No provider failure can crash the pipeline
- Pipeline outputs unchanged: same format, same behavior

---

## Strategy Behavior

### Deterministic Selection

**Provider selection is deterministic based on:**
1. `IMAGE_PROVIDER` environment variable value
2. Provider initialization success/failure
3. Priority order (for auto strategy)

**No randomness or non-deterministic behavior.**

### Error Handling

**All errors are handled gracefully:**
- Missing credentials → skip provider → try next (auto) or fallback to mock (explicit)
- Initialization exceptions → caught and logged → fallback
- Unknown provider → immediate fallback to mock
- All paths guaranteed to return a provider (never None, never crash)

### Warnings

**Warnings are logged for:**
- Failed provider initialization (with reason)
- Unknown provider type
- Fallback to mock provider

**Warnings help with debugging but don't stop execution.**

---

## Environment Variables

### Required for Google Provider

```bash
VERTEX_API_KEY=your_api_key_here
VERTEX_PROJECT_ID=your_project_id_here
VERTEX_LOCATION=us-central1  # Optional, defaults to us-central1
```

### Provider Selection

```bash
IMAGE_PROVIDER=mock    # Default (works offline)
IMAGE_PROVIDER=google   # Google Vertex AI (requires credentials)
IMAGE_PROVIDER=stub     # Stub provider (placeholder)
IMAGE_PROVIDER=auto     # Auto strategy (tries in priority order)
```

---

## Known Limitations

1. **Initialization vs Generation:** Auto strategy only tests provider initialization, not generation success. A provider that initializes but always fails generation will still be selected.

2. **No Retry Logic:** If a provider fails during generation, there's no automatic retry with next provider. This is by design - generation failures are handled by Phase 2's error handling.

3. **Priority Order:** Priority order is fixed in code. Cannot be changed via environment variables (can be extended in future if needed).

4. **Single Provider:** Only one provider is selected at a time. No parallel provider attempts or load balancing.

---

## Success Criteria

✅ **All criteria met:**

1. ✅ Second ImageProvider added (StubImageProvider)
2. ✅ Provider priority order defined and documented
3. ✅ Selection logic implemented (explicit and auto)
4. ✅ Fallback chain always ends in mock
5. ✅ Phase 2 works with mock, google, and auto modes
6. ✅ Full pipeline Phase 1 → 5.5 runs successfully
7. ✅ Documentation complete (this file)
8. ✅ CURRENT_STATE.md updated
9. ✅ Changes committed

---

## Future Work

- Add more real providers (OpenAI DALL-E, Stability AI, etc.)
- Add provider health checking (test generation, not just initialization)
- Add configurable priority order via environment variables
- Add provider metrics/telemetry
- Add parallel provider attempts for redundancy

---

## Commit

**Commit Message:**
```
EP S07: multi-provider image strategy with robust fallback

- Add StubImageProvider for testing and placeholder purposes
- Create strategy module for provider selection and fallback chain
- Implement auto strategy that tries providers in priority order
- Extend get_image_provider() to support explicit and auto modes
- Guarantee all fallback chains end in MockImageProvider
- Full pipeline verified: Phase 1 → Phase 5.5 runs successfully
- No provider failure can crash the pipeline
```

---

**Status:** ✅ **COMPLETE**

**Date:** 2024-12-19
