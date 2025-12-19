# SYSTEM_MAP — TikTok Clip Factory

## 1. Vertical Pillars (Core Pipeline)

The system processes video generation through six sequential phases. Each phase transforms input data into output data that feeds the next phase.

### Phase 1: Story Engine (story_engine.py)

**Input:** User parameters (goal, product, audience, platform)

**Output:** Story JSON object containing:
- Story metadata (goal, product, audience, platform)
- Scenes array (4 scenes: hook, conflict, reveal, close)
- Each scene has: id, purpose, emotion, duration, description

**Purpose:** Converts user intent into a structured narrative with emotional beats and timing.

---

### Phase 2: Asset Generator (phase2_generator.py)

**Input:** Story object from Phase 1

**Output:** Phase 2 output containing:
- Original story object (preserved)
- Character candidates (3-5 options with images, style, personality)
- Location candidates (3-5 options with images, style, mood)
- Selection state (selected character ID, selected location ID)

**Purpose:** Generates visual asset candidates (characters and locations) using image generation APIs. User selects preferred options.

---

### Phase 3: Storyboard Engine (phase3_storyboard.py)

**Input:** Phase 2 output (story + selected character + selected location)

**Output:** Storyboard JSON containing:
- Story metadata
- Selected character and location objects
- Scenes array with keyframes (1-3 keyframes per scene based on duration)
- Each keyframe has: id, timing, description, image_path, image_prompt

**Purpose:** Breaks scenes into visual keyframes that represent moments in the video timeline.

---

### Phase 4: Video Plan (phase4_video_plan.py)

**Input:** Storyboard from Phase 3

**Output:** Video Plan JSON containing:
- Storyboard metadata (preserved)
- Segments array (each segment = transition from keyframe A to keyframe B)
- Each segment has: id, duration, start_time, end_time, start_keyframe object, end_keyframe object, purpose, emotion
- Total duration and segment count

**Purpose:** Maps storyboard keyframes into renderable video segments. Each segment defines a motion from one keyframe to the next.

**Note:** Segment durations are calculated from keyframe timing (not fixed to 8 seconds). Phase 5 will override durations to 8 seconds during rendering.

---

### Phase 5: Segment Renderer (phase5_segment_renderer.py)

**Input:** Video Plan from Phase 4

**Output:** Rendered segment results containing:
- Success status per segment
- Video file paths (one per segment)
- Each segment video is exactly 8 seconds (fixed duration)
- Metadata including original Phase 4 duration

**Purpose:** Renders individual video segments using video generation APIs. Each segment is generated separately as an 8-second video file.

**Duration Contract:** Phase 5 always renders 8-second segments regardless of Phase 4 duration. Original Phase 4 duration is preserved in metadata.

---

### Phase 5.5: Assembler (phase5_assembler.py)

**Input:** List of rendered segment video file paths from Phase 5

**Output:** Final video assembly result containing:
- Success status
- Final video file path
- Failed segment indices
- Retry count

**Purpose:** Stitches individual segment videos into a single final video file. Handles retry logic for failed segments.

---

## 2. Horizontal Pillars (Cross-cutting Systems)

### UI / UX (app_streamlit.py)

**Purpose:** Streamlit-based web interface for the video generation pipeline.

**Features:**
- Phase-by-phase navigation
- Visual preview of story, characters, locations, storyboard
- Progress tracking
- Parameter input (goal, product, audience, platform)
- Selection interface for characters and locations

**Integration:** Calls phase modules sequentially, maintains session state between phases.

---

### Orchestration (end_to_end_run.py)

**Purpose:** End-to-end execution script that runs all phases sequentially.

**Features:**
- Validates phase outputs before proceeding
- Error handling and reporting
- Summary generation
- Phase order enforcement

**Integration:** Imports and calls all phase modules, validates outputs using schema validators.

---

### Contracts & Validation (contracts/, validators/)

**Purpose:** Ensures data integrity and phase compatibility.

**Components:**
- **validators/schema_validators.py:** Validates phase outputs match expected schemas
- **contracts/phase4_to_phase5.md:** Defines contract between Phase 4 and Phase 5 (segment schema requirements)

**Features:**
- Input validation (checks previous phase output before processing)
- Output validation (checks current phase output before proceeding)
- Phase order validation (ensures phases run in correct sequence)
- Schema contract enforcement (ensures data structures match expectations)

---

### Testing & Documentation (tests/, *.md)

**Purpose:** Testing infrastructure and project documentation.

**Components:**
- **tests/:** Test fixtures and end-to-end tests
  - `test_end_to_end.py`: End-to-end pipeline tests
  - `fixtures/`: Sample story JSON files for testing
- **Documentation files:** Various markdown files describing system state, workflow, progress, and contracts

**Features:**
- Test fixtures for each phase
- End-to-end test coverage
- Documentation of system architecture, contracts, and progress

---

## 3. Source of Truth

Each phase owns specific aspects of the video generation process:

### Story Logic
**Owner: Phase 1 (Story Engine)**
- Narrative structure (hook, conflict, reveal, close)
- Scene purposes and emotional beats
- Scene durations
- Story descriptions

**Preserved through:** All phases maintain story metadata, but Phase 1 is the source.

---

### Visual Canon
**Owner: Phase 2 (Asset Generator)**
- Character appearance and style
- Location appearance and mood
- Visual consistency rules

**Preserved through:** Selected character and location objects flow through Phase 3, 4, and 5 as continuity locks.

---

### Timeline
**Owner: Phase 4 (Video Plan)**
- Segment timing and sequencing
- Keyframe transitions
- Original duration calculations

**Modified by:** Phase 5 overrides segment durations to 8 seconds but preserves original duration in metadata.

---

### Physical Constraints
**Owner: Phase 5 (Segment Renderer)**
- Fixed 8-second segment duration
- Video file format and encoding
- Render quality and parameters

**Enforced by:** Phase 5 always renders 8-second segments regardless of Phase 4 duration.

---

## 4. What This File Is For

This file serves as a high-level architectural map for humans and agents to understand the TikTok Clip Factory system without reading code.

**Use cases:**
- **Onboarding:** New team members or agents can understand system structure quickly
- **Architecture reference:** Clarifies phase responsibilities and data flow
- **Debugging:** Helps identify which phase owns specific functionality
- **Planning:** Shows where changes should be made for new features

**This file does NOT:**
- Show code implementations
- Define schemas in detail (see validators and contracts for that)
- Describe API endpoints or technical details
- Provide usage instructions (see other documentation files)

**Tone:** Clear, precise, non-marketing. Focuses on what the system does, not how to use it.

