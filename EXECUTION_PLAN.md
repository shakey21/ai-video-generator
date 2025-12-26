# 30-Day Execution Plan

## Goal
Ship first AI MetaHuman influencer video (Influencer #1) in 30 days, then scale to Influencers #2-10.

---

## Week 1: Foundation (Days 1-7)

### Day 1-2: Environment Setup
- [ ] Install Unreal Engine 5.7.1 (Apple Silicon build)
- [ ] Install Python 3.11, FFmpeg, Ollama
- [ ] Create Unreal project with MetaHuman plugin
- [ ] Enable Python scripting in Unreal
- [ ] Test basic Python → Unreal communication

**Deliverable**: Working Unreal project with Python access

---

### Day 3-4: MetaHuman Creation
- [ ] Download MetaHuman from Quixel Bridge
- [ ] Customize appearance (face, hair, clothing)
- [ ] Import to Unreal project
- [ ] Create Blueprint for MetaHuman actor
- [ ] Test spawning in level

**Deliverable**: Custom MetaHuman ready for animation

---

### Day 5-7: Voice Cloning
- [ ] Record voice samples (5-10 minutes of clean audio)
- [ ] Install Coqui TTS
- [ ] Train voice clone model
- [ ] Test synthesis quality
- [ ] Generate test narration

**Deliverable**: Cloned voice model producing natural speech

**Acceptance**: Voice sounds like target, no artifacts

---

## Week 2: Core Pipeline (Days 8-14)

### Day 8-9: Stage 1-2 (Planning + Voice)
- [ ] Implement `src/planning/generate_script.py`
- [ ] Setup Ollama with llama3.1
- [ ] Create prompt templates for persona
- [ ] Implement `src/voice/synthesize.py`
- [ ] Integrate Coqui TTS

**Test**: Generate script → synthesize voice → verify output

---

### Day 10-11: Stage 3 (Facial Animation)
- [ ] Implement audio-driven facial animation
- [ ] Map phonemes to ARKit blend shapes
- [ ] Add procedural blinks and eye movement
- [ ] Export curves as JSON
- [ ] Test import to Unreal

**Test**: Audio → face curves → visual playback in Unreal

---

### Day 12-14: Stage 4-5 (Body + Scene)
- [ ] Capture 10-15 gesture animations (Rokoko or iPhone)
- [ ] Import to Unreal, create animation library
- [ ] Implement gesture selection logic
- [ ] Create 2-3 scene templates (studio, office, outdoor)
- [ ] Setup camera presets for 9:16 framing

**Test**: Script keywords → correct gestures selected

---

## Week 3: Unreal Integration (Days 15-21)

### Day 15-17: Stage 6 (Unreal Assembly)
- [ ] Write `unreal_scripts/assemble_sequence.py`
- [ ] Implement:
  - Create Level Sequence
  - Import audio
  - Add MetaHuman
  - Apply facial/body animation
  - Add camera
- [ ] Test end-to-end assembly

**Test**: Run script → complete Level Sequence created

---

### Day 18-19: Stage 7 (Rendering)
- [ ] Configure Movie Render Queue presets
- [ ] Implement `src/rendering/render.py`
- [ ] Test fast preview render (draft quality)
- [ ] Test high quality render (production)
- [ ] Measure render times

**Test**: Sequence → rendered video file

**Target**: 30s video renders in <3min (preview mode)

---

### Day 20-21: Stage 8 (Post-Processing)
- [ ] Implement audio mixing (narration + music)
- [ ] Install Whisper for subtitles
- [ ] Implement subtitle generation
- [ ] Implement subtitle burning with FFmpeg
- [ ] Test color grading (optional)

**Test**: Raw video → final video with subs + music

---

## Week 4: Polish + Launch (Days 22-30)

### Day 22-23: Stage 9-10 (QA + Publishing)
- [ ] Implement QA checks (duration, audio levels, black frames)
- [ ] Implement platform transcoding (TikTok, Instagram, YouTube)
- [ ] Generate thumbnails
- [ ] Create upload manifest

**Test**: Final video → deliverables for all platforms

---

### Day 24-25: CLI + Orchestrator
- [ ] Finalize `main.py` CLI
- [ ] Implement caching system
- [ ] Add dry-run mode
- [ ] Add resume from stage functionality
- [ ] Test full pipeline end-to-end

**Test**: Single command generates complete video

---

### Day 26-27: Brand Pack Creation
- [ ] Create `brand_packs/influencer_001/`
- [ ] Add persona.json
- [ ] Add voice model
- [ ] Add overlays (logos, lower thirds)
- [ ] Add music tracks
- [ ] Document brand guidelines

**Deliverable**: Complete brand pack for Influencer #1

---

### Day 28-29: First Production Video
- [ ] Write content brief for real video
- [ ] Run full pipeline with high quality config
- [ ] Review output quality
- [ ] Fix any issues
- [ ] Optimize render time

**Deliverable**: Production-ready 30-60s influencer video

**Acceptance**: Publishable quality, <20min render time

---

### Day 30: Documentation + Handoff
- [ ] Document any workarounds or gotchas
- [ ] Create troubleshooting guide
- [ ] Record demo video of pipeline
- [ ] Update README with actual performance metrics
- [ ] Tag v1.0 release

**Deliverable**: Complete, documented pipeline for Influencer #1

---

## Scaling Plan: Influencers #2-10

### Per Additional Influencer (2-3 days each)

**Day 1: Asset Creation**
- [ ] Create new MetaHuman (1-2 hours)
- [ ] Record voice samples (30min)
- [ ] Train voice model (2-4 hours)
- [ ] Clone brand pack from template
- [ ] Customize persona.json

**Day 2: Testing**
- [ ] Generate test video
- [ ] Review quality
- [ ] Adjust persona parameters
- [ ] Record 2-3 unique gestures (optional)

**Day 3: Production**
- [ ] Generate first real video
- [ ] Optimize settings
- [ ] Document influencer-specific quirks

**Effort Reduction**: 80% code reuse, 20% customization

---

## Timeline Summary

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Foundation | 7 days | Unreal + MetaHuman + Voice |
| Core Pipeline | 7 days | Stages 1-5 working |
| Unreal Integration | 7 days | Stages 6-8 working |
| Polish + Launch | 9 days | Full pipeline + first video |
| **TOTAL** | **30 days** | **Influencer #1 shipping** |

---

## Scaling Timeline

| Milestone | Cumulative Days | Influencers |
|-----------|-----------------|-------------|
| MVP | 30 | 1 |
| Influencer #2 | 33 | 2 |
| Influencer #3 | 36 | 3 |
| Influencer #4-5 | 42 | 5 |
| Influencer #6-10 | 60 | 10 |

**Total time to 10 influencers**: ~60 days

---

## Risk Mitigation

### High Risk
1. **Unreal Python API limitations**
   - Mitigation: Test early (Week 1)
   - Fallback: Manual Unreal steps, Blueprint automation

2. **Render time too slow**
   - Mitigation: Optimize settings, simplify scenes
   - Fallback: Cloud rendering (AWS, Pixel Streaming)

3. **Voice quality poor**
   - Mitigation: More training data, better voice model
   - Fallback: Use ElevenLabs API (paid)

### Medium Risk
1. **Facial animation not realistic**
   - Mitigation: Use Live Link Face capture instead of audio-driven
   - Timeline impact: +2 days per video

2. **Gestures look repetitive**
   - Mitigation: Capture more variations
   - Timeline impact: +1 day

---

## Success Criteria (Day 30)

- [ ] Generate 30-60s video in single command
- [ ] Preview mode: <5min total time
- [ ] High quality mode: <20min total time
- [ ] Voice sounds natural (>80% believable)
- [ ] Facial animation lip synced (no obvious desyncs)
- [ ] Body language looks intentional (not robotic)
- [ ] Video passes all QA checks
- [ ] Deliverables ready for all platforms
- [ ] Pipeline documented and reproducible

---

## Next Steps After Day 30

1. **Content Production**: Generate 5-10 videos for Influencer #1
2. **Analytics Integration**: Track view metrics
3. **Influencer #2**: Apply learnings, faster execution
4. **Automation**: Schedule daily/weekly video generation
5. **Refinement**: Improve gesture library, add more scenes

---

## Weekly Checkpoints

**End of Week 1**: MetaHuman created, voice cloned  
**End of Week 2**: Scripts generate voice output  
**End of Week 3**: Unreal renders video from pipeline  
**End of Week 4**: First production video published

**Miss a checkpoint?** Reassess timeline, cut scope if needed.
