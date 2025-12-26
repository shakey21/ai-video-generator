# MVP Acceptance Criteria

## Goal
Ship first production-quality Instagram Reel using MetaHuman dance/movement pipeline.

**Target**: 30-second viral-ready Reel, 1080x1920, Instagram-optimized

---

## Phase 1: Foundation (Days 1-5)

### Infrastructure
- [ ] Unreal Engine 5.4+ installed and running on macOS
- [ ] Python 3.13+ environment configured  
- [ ] FFmpeg installed (`brew install ffmpeg`)
- [ ] Ollama installed with llama3.1 model
- [ ] Pipeline runs `--dry-run` without errors

**Acceptance**: `python main.py --dry-run` completes successfully

**Test**:
```bash
python3 --version  # Should be 3.13+
ffmpeg -version
ollama list  # Should show llama3.1
```

---

### Unreal Engine Project
- [ ] New UE project created (Blank template)
- [ ] MetaHuman plugin enabled
- [ ] Python scripting plugin enabled
- [ ] Python paths configured to project directory

**Acceptance**: Unreal opens project without errors

---

### MetaHuman Character
- [ ] MetaHuman created in MetaHuman Creator (or Quixel Bridge)
- [ ] Imported to Unreal project via Bridge
- [ ] Blueprint created (`BP_YourPerformer`)
- [ ] Character spawns in level and is visible
- [ ] Default animations work (T-pose, idle)

**Acceptance**: MetaHuman renders correctly in viewport

**Test**: Place MetaHuman in level, play scene, confirm visible

---

## Phase 2: Animation Library (Days 6-10)

### Animation Sequences
- [ ] 5-10 dance/movement animations imported to Unreal
- [ ] Animations organized in folder structure:
  - `Content/Animations/Dances/`
  - `Content/Animations/Movements/`
  - `Content/Animations/Idles/`
- [ ] Animations retargeted to MetaHuman skeleton
- [ ] Test animation plays on MetaHuman

**Acceptance**: All animations play smoothly on MetaHuman

**Sources**: Mixamo, Unreal Marketplace, motion capture

---

### Scene Setup
- [ ] Simple studio scene created (plain background, good lighting)
- [ ] Camera positioned for 9:16 vertical framing
- [ ] Camera aspect ratio set to 1080x1920
- [ ] Lighting configured (3-point or environmental)
- [ ] MetaHuman spawn point marked

**Acceptance**: Scene renders cleanly with good lighting

---

## Phase 3: Core Pipeline (Days 11-20)

### Stage 1: Planning
- [ ] Ollama generates concept from brief
- [ ] Concept includes movement keywords and timing
- [ ] Output: `concept.json`

**Acceptance**: Brief → concept.json generation works

**Test**:
```bash
python main.py --performer performer_001 --brief example.md --end-at-stage 1
```

---

### Stage 2: Facial Animation
- [ ] Procedural blinks generated (every 3-5s)
- [ ] Eye movement added
- [ ] Subtle head sway implemented
- [ ] Output: `face_curves.json`

**Acceptance**: Facial expressions look natural and alive

---

### Stage 3: Body Animation
- [ ] Dance/movement sequences selected from library
- [ ] Animations chain smoothly (transitions work)
- [ ] Timing aligns with concept duration
- [ ] Energy level matches persona config
- [ ] Output: `body_sequence.json`

**Acceptance**: Movement looks intentional and fluid

**Test**: Verify 30s sequence plays without animation pops

---

### Stage 4-5: Scene + Unreal Assembly
- [ ] Scene selected based on brief
- [ ] Camera positioned for 9:16 framing
- [ ] Python script creates Level Sequence in Unreal
- [ ] MetaHuman added to sequence
- [ ] Facial curves applied
- [ ] Body animations applied
- [ ] Camera set as master shot

**Acceptance**: Complete Level Sequence playable in Unreal

**Test**: Open sequence, scrub timeline, see full performance

---

## Phase 4: Rendering + Polish (Days 21-25)

### Stage 6: Rendering
- [ ] Movie Render Queue configured
- [ ] Fast preview renders in < 2 min (30s reel)
- [ ] High quality renders in < 10 min (30s reel)
- [ ] Output resolution: 1080x1920
- [ ] Frame rate: 30fps (default) or 60fps (high quality)
- [ ] No render artifacts or black frames

**Acceptance**: Sequence → video_raw.mov playable in QuickTime

**Performance Test (M4 Pro)**:
- Fast: < 2min for 30s
- Default: < 6min for 30s
- High: < 10min for 30s

---

### Stage 7-8: Post-Processing + QA
- [ ] Video transcoded to Instagram-optimized MP4
- [ ] Bitrate set appropriately (8-12 Mbps)
- [ ] Optional: Background music mixed
- [ ] Optional: Graphics/overlays added
- [ ] QA checks run automatically
- [ ] Duration within tolerance (±2s)
- [ ] No black frames detected
- [ ] File size < 100MB

**Acceptance**: video_final.mp4 ready for Instagram upload

**Quality Check**:
- [ ] Movement looks smooth (no stuttering)
- [ ] Facial expressions visible and natural
- [ ] Lighting looks professional
- [ ] No render glitches

---

### Stage 9: Publishing
- [ ] Instagram-optimized MP4 generated (1080x1920, 30fps)
- [ ] Thumbnail variants extracted (3-5 frames)
- [ ] Metadata JSON created (caption, hashtags)
- [ ] All deliverables in `08_publish/` directory

**Acceptance**: Ready to upload directly to Instagram

---

## End-to-End Test

### Single Command Generation

```bash
python main.py \
  --performer performer_001 \\\n  --brief content_briefs/example.md \
  --config default
```

**Success Criteria**:
- [ ] Command completes without errors
- [ ] Total time < 6 minutes (30s reel, default config)
- [ ] Output video is Instagram-ready
- [ ] All files present in run directory

---

## Quality Criteria

### Technical
- [ ] Video resolution: 1080x1920 (Instagram Reels spec)
- [ ] Frame rate: 30fps (default) or 60fps (high quality)
- [ ] Bitrate: 8-12 Mbps (Instagram optimal)
- [ ] File size: < 100MB
- [ ] No render artifacts or black frames

### Creative
- [ ] Movement looks intentional and engaging
- [ ] Facial expressions natural (blinks, eye contact)
- [ ] Animation transitions smooth (no pops)
- [ ] Pacing appropriate for Instagram
- [ ] Lighting professional (no harsh shadows)

### User Experience
- [ ] Pipeline fails gracefully (clear errors)
- [ ] Can resume from any stage (`--start-from-stage`)
- [ ] Caching works (reruns are instant)
- [ ] Logs readable and helpful
- [ ] Documentation accurate

---

## Performance Targets (M4 Pro 48GB)

### Fast Preview Mode
- **Total Time**: < 2 minutes (30s reel)
- **Render Time**: < 45 seconds
- **Use Case**: Testing choreography

### Default Mode
- **Total Time**: < 6 minutes (30s reel)
- **Render Time**: < 3 minutes
- **Use Case**: Standard Instagram posting

### High Quality Mode
- **Total Time**: < 10 minutes (30s reel)
- **Render Time**: < 6 minutes
- **Use Case**: Featured/viral content

---

## Documentation Completeness

- [ ] README.md complete and Instagram-focused
- [ ] ARCHITECTURE.md describes all 9 stages
- [ ] UNREAL_AUTOMATION.md shows Python automation
- [ ] EXECUTION_PLAN.md timeline realistic
- [ ] SETUP.md covers M4 Pro setup
- [ ] QUICKSTART.md: first reel in 30 minutes
- [ ] Example brand pack functional

---

## Scaling Readiness

### Performer #2 Preparation
- [ ] Brand pack template-ready (easy clone)
- [ ] MetaHuman creation process documented
- [ ] Animation library reusable
- [ ] Unreal project accepts new characters

**Target**: Add Performer #2 in 1-2 days

---

## Definition of Done

**The pipeline is MVP-ready when:**

1. Complete 30s Instagram Reel generated in single command
2. Reel passes all QA checks
3. Quality is viral-worthy (would actually post)
4. Performance < 6min (default config, M4 Pro)
5. Documentation complete
6. Can demo end-to-end successfully

**Final Test**: Show reel to 10 people. At least 8 should say:
- "This looks like a real Instagram Reel"
- "The movement looks natural"
- "I would watch this content"

---

## Known Limitations (Acceptable for MVP)

- Limited animation library (10-15 sequences)
- Single camera angle per reel
- No speech/voice (movement only)
- Basic facial expressions (no complex emotions)
- One performer only (scaling later)

---

## Go/No-Go Checklist

Before shipping MVP:

- [ ] All Phase 1-4 acceptance criteria met
- [ ] End-to-end test passes
- [ ] Quality criteria met
- [ ] Performance targets hit (M4 Pro)
- [ ] Documentation complete
- [ ] Ready to post publicly on Instagram

**If any item fails**: Fix before shipping. This is your quality bar.
