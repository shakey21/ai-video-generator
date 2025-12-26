# MetaHuman Content Creator Pipeline Architecture

## Philosophy

This is a **generation-first** pipeline that creates Instagram Reels from scratch using MetaHuman performers in Unreal Engine. Unlike traditional VFX or SaaS avatar platforms, this approach provides complete asset ownership and unlimited rendering at zero marginal cost.

**Core Principles:**
- **Local-First**: All processing on macOS Apple Silicon
- **Modular**: Clear stage boundaries with defined inputs/outputs
- **Cacheable**: Aggressive content-hashing at every stage
- **Scalable**: 1 to 10+ performers with reusable assets
- **Deterministic**: Same inputs always produce same outputs
- **Asset Ownership**: You own the MetaHuman, animations, and all outputs

---

## 9-Stage Pipeline

### Stage 1: Content Planning

**Module**: `src/planning/`

**Inputs**:
- `content_brief.md` - Reel concept, style, duration
- `persona.json` - Performer style, energy, movement preferences

**Outputs**:
- `concept.json` - Movement concept with timing and energy
- `metadata.json` - Title, description, hashtags

**Process**:
1. Load persona configuration
2. Generate movement concept using local LLM (Ollama)
3. Apply persona style, energy level, and preferences
4. Structure choreography timing and transitions
5. Add metadata for Instagram posting

**Tools**: Ollama (llama3.1), custom prompt templates

**Config**:
```yaml
planning:
  llm:
    provider: "ollama"
    model: "llama3.1"
    temperature: 0.7
```

---

### Stage 2: Facial Animation

**Module**: `src/facial/`

**Inputs**:
- `persona.json` (facial_style)
- `script.json` (emotion cues)

**Outputs**:
- `face_curves.json` - Basic expressions (smile, focus, etc.)
- `face_metadata.json` - Emotion timeline

**Process**:
1. Generate procedural blinks (every 3-5 seconds)
2. Add subtle head movement and eye tracking
3. Map script emotions to facial expressions
4. Export basic ARKit blend shapes (no lip sync)

**Tools**: Procedural animation, MetaHuman preset expressions

---

### Stage 3: Body Animation

**Module**: `src/body/`

**Inputs**:
- `script.json` (timing, beat markers)
- `animation_library/dances/`
- `animation_library/movements/`
- `persona.json` (energy_level, style)

**Outputs**:
- `body_sequence.uasset` - Full body animation
- `movement_timeline.json` - Which moves when

**Process**:
1. Select dance/movement sequences from library
2. Chain animations based on energy level and style
3. Add procedural upper body movement
4. Blend animations with smooth transitions (0.3-0.5s)
5. Synchronize to music/beat if provided

**Animation Library**:
- `dances/` - Dance routines, grooves, expressions (5-15s)
- `movements/` - Gestures, poses, transitions (1-5s)
- `idles/` - Standing variations, sway patterns (loops)
- `transitions/` - Movement connectors

---

### Stage 4: Scene Selection

**Module**: `src/scenes/`

**Inputs**:
- `content_brief.md` (setting preference)
- `brand_pack/scenes/`

**Outputs**:
- `selected_template.txt` - Path to UE level
- `camera_setup.json` - Camera positions

**Process**:
1. Match brief keywords to scene templates
2. Select lighting preset from brand pack
3. Configure camera for 9:16 vertical framing
4. Set MetaHuman spawn position

**Scene Templates**:
- Studio_Minimal_001 (fastest)
- Office_Modern_001
- Outdoor_Urban_001

---

### Stage 5: Unreal Assembly

**Module**: `src/unreal_automation/`

**Inputs**:
- Background music (optional)
- `face_curves.json`
- `body_sequence.uasset`
- `selected_template.txt`

**Outputs**:
- Level Sequence in Unreal project
- `sequence_path.txt` - Path to .uasset

**Process** (via Python API):
1. Create new Level Sequence
2. Import audio track
3. Add MetaHuman to sequence
4. Apply facial animation
5. Apply body animation
6. Add camera and set as cut
7. Add brand overlays (logos, lower thirds)

**Script**: `unreal_scripts/assemble_sequence.py`

---

### Stage 6: Rendering

**Module**: `src/rendering/`

**Inputs**:
- Level Sequence path
- `render_preset.yaml`

**Outputs**:
- `video_raw.mov` - ProRes or H264
- `render_stats.json` - Timing, frames

**Process**:
1. Configure Movie Render Queue
2. Set resolution 1080x1920, fps, quality
3. Trigger render via CLI
4. Monitor progress and handle failures
5. Validate output file

**Render Times** (M4 Pro 48GB, 30s reel):
- Fast: 45s (24fps, draft quality)
- Default: 3min (30fps, production quality)
- High: 6min (60fps, ProRes, high AA)

---

### Stage 7: Post-Processing

**Module**: `src/post/`

**Inputs**:
- `video_raw.mov`
- `brand_pack/music/` (optional)
- `brand_pack/overlays/` (optional)

**Outputs**:
- `video_final.mp4` - Instagram-optimized MP4
- `encoding_log.json` - Compression stats

**Process**:
1. Mix audio (background music if specified)
2. Apply color grading LUT (optional)
3. Add brand overlays (logos, graphics)
4. Transcode to Instagram specs (1080x1920, 30fps, 8-12 Mbps)
5. Validate output file

**Tools**: FFmpeg

---

### Stage 8: Quality Assurance

**Module**: `src/qa/`

**Inputs**:
- `video_final.mp4`
- `qa_rules.yaml`

**Outputs**:
- `qa_report.json` - Pass/fail
- `qa_preview.gif` - Quick preview

**Checks**:
- Video duration within tolerance
- Resolution correct (1080x1920)
- Frame rate correct (30 or 60fps)
- No black frames or render artifacts
- File size < 100MB (Instagram limit)

---

### Stage 9: Publishing Preparation

**Module**: `src/publish/`

**Inputs**:
- `video_final.mp4`
- `metadata.json`

**Outputs**:
- `instagram_reel.mp4` - Final Instagram-ready file
- `upload_manifest.json` - Caption, hashtags, metadata
- `thumbnail_01.jpg` - Preview image
- `thumbnail_02.jpg` - Alternate preview
- `thumbnail_03.jpg` - Alternate preview

**Process**:
1. Copy final video to deliverables
2. Generate Instagram metadata (caption, hashtags)
3. Extract thumbnail frames (3 options)
4. Package deliverables in publish folder
5. Create upload instructions

---

## Data Flow

```
content_brief.md + persona.json
  ↓
[1: Planning] → script.json, metadata.json
  ↓
[2: Facial] → face_curves.json
  ↓
[3: Body] → body_sequence.uasset
  ↓
[4: Scene] → selected_template.txt
  ↓
[5: Unreal] → Level Sequence (.uasset)
  ↓
[6: Render] → video_raw.mov
  ↓
[7: Post] → video_final.mp4, subtitles.srt
  ↓
[8: QA] → qa_report.json
  ↓
[9: Publish] → platform videos, thumbnails, manifest
```

---

## Run Directory Structure

```
runs/20251224_143022_influencer001_video042/
├── 00_planning/
│   ├── script.json
│   └── metadata.json
├── 01_facial/
│   └── face_curves.json
├── 02_body/
│   └── body_sequence.uasset
├── 03_scene/
│   └── selected_template.txt
├── 04_unreal/
│   └── sequence_path.txt
├── 05_render/
│   └── video_raw.mov
├── 06_post/
│   ├── video_final.mp4
│   └── subtitles.srt
├── 07_qa/
│   └── qa_report.json
├── 08_publish/
│   ├── tiktok.mp4
│   ├── instagram.mp4
│   ├── youtube.mp4
│   └── upload_manifest.json
├── logs/
│   └── pipeline.log
└── metadata.json
```

---

## Caching Strategy

**Content Hashing**: SHA256 of stage inputs determines if rerun needed

**Cache Hit**: Skip stage, use existing output  
**Cache Miss**: Execute stage, save result

**Benefits**:
- Rerun from any stage: `--start-from-stage 5`
- Partial updates: Change script → only reruns facial onwards
- Experimentation: Try different configs without full reruns

---

## Scalability Model

### Single Influencer
- **Setup time**: 20-30 days (first influencer)
- **Per-video time**: 3-20 min (depending on quality)
- **Assets needed**: MetaHuman, 20-30 gestures, audio files

### Multiple Influencers
- **Influencer #2 setup**: 2-3 days (clone brand pack)
- **Effort reduction**: 80% reuse of code, scenes, workflows
- **Scaling target**: 10 influencers in 60 days total

---

## Technology Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| **Orchestration** | Python 3.11 | Pipeline control |
| **Config** | YAML | Stage settings |
| **LLM** | Ollama | Script generation |

| **Lip Sync** | MetaHuman Animator | Audio-driven facial |
| **Facial Capture** | Live Link Face | iPhone ARKit |
| **Animation** | MetaHuman Animator | Face solve |
| **Rendering** | Unreal Engine 5.7.1 | MetaHuman render |
| **Video** | FFmpeg | Transcoding |
| **Subtitles** | Whisper | STT |
| **Caching** | SHA256 + JSON | Content hashing |

---

## Performance Targets

**Fast Preview** (30s video):
- Total time: ~2.5 minutes
- Unattended: Yes
- Quality: Draft (good for iteration)

**High Quality** (30s video):
- Total time: ~15 minutes  
- Unattended: Yes
- Quality: Production (final delivery)

---

## Next Steps

See:
- **UNREAL_AUTOMATION.md** - How to control Unreal Engine
- **EXECUTION_PLAN.md** - 30-day implementation roadmap
- **SETUP.md** - Installation guide
