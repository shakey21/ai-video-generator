# AI MetaHuman Content Creator

> **Professional Instagram Reels generation using Unreal Engine MetaHumans on Apple Silicon**

Create viral-ready Instagram Reels featuring AI-powered MetaHuman performers. Fully automated pipeline from concept to 9:16 vertical video, optimized for dance, movement, and visual content.

## Overview

This is a **9-stage automated pipeline** that generates professional Instagram Reels with:
- AI-generated choreography concepts
- Procedural facial expressions
- Dance and movement sequences
- Cinematic Unreal Engine rendering
- Instagram-optimized post-processing
- Platform-ready deliverables (9:16, 30-90s)

**Key Features:**
- **Apple Silicon Optimized** - M4 Pro 48GB tested, blazing fast
- **MetaHuman Native** - Photorealistic digital performers
- **Movement Focused** - Dance routines, poses, choreography
- **Cached Pipeline** - Iteration in minutes, not hours
- **IG Reels Ready** - 1080x1920, 30fps, perfect formatting
- **Production Grade** - Concept to upload in single command

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup Unreal Engine project with MetaHuman (see SETUP.md)

# 3. Configure your performer
cp -r brand_packs/influencer_001 brand_packs/my_performer
# Edit brand_packs/my_performer/persona.json

# 4. Generate an Instagram Reel
python main.py \
  --performer my_performer \
  --brief content_briefs/example.md \
  --config fast_preview

# Output: runs/YYYYMMDD_HHMMSS_my_performer/output/instagram_reel.mp4
```

## Project Structure

```
ai-metahuman-content-creator/
├── main.py                          # CLI entry point
├── config/
│   ├── default.yaml                 # Balanced quality
│   ├── fast_preview.yaml            # Quick iteration (~2min)
│   └── high_quality.yaml            # Production render (~10min)
├── src/
│   ├── pipeline.py                  # Orchestrator
│   ├── planning/                    # Stage 1: Concept generation
│   ├── facial/                      # Stage 2: Facial expressions
│   ├── body/                        # Stage 3: Dance/movement
│   ├── scenes/                      # Stage 4: Scene selection
│   ├── unreal_automation/           # Stage 5: UE assembly
│   ├── rendering/                   # Stage 6: Render
│   ├── post/                        # Stage 7: Post-processing
│   ├── qa/                          # Stage 8: Quality checks
│   ├── publish/                     # Stage 9: IG optimization
│   └── utils/                       # Shared utilities
├── brand_packs/
│   └── performer_001/               # Performer assets
│       ├── persona.json             # Character config
│       ├── scenes/                  # Custom environments
│       └── overlays/                # Graphics/branding
├── shared_assets/
│   └── animation_library/           # Dance & movement animations
│       ├── dances/                  # Full routines
│       ├── movements/               # Gestures, poses
│       └── idles/                   # Standing loops
├── unreal_scripts/                  # Python automation for UE
├── runs/                            # Pipeline execution runs
└── deliverables/                    # Final Instagram-ready MP4s
```

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete 10-stage pipeline design
- **[UNREAL_AUTOMATION.md](UNREAL_AUTOMATION.md)** - Unreal Engine automation guide
- **[EXECUTION_PLAN.md](EXECUTION_PLAN.md)** - 30-day implementation roadmap
- **[SETUP.md](SETUP.md)** - Installation and setup guide
- **[MVP_CHECKLIST.md](MVP_CHECKLIST.md)** - Acceptance criteria

## Pipeline Stages

| # | Stage | Input | Output | Time (M4 Pro) |
|---|-------|-------|--------|---------------|
| 1 | Planning | Brief + Persona | Concept JSON | 5-10s |
| 2 | Facial | Concept | Expression curves | 15s |
| 3 | Body | Concept | Dance sequence | 20s |
| 4 | Scene | Brief | Scene template | 5s |
| 5 | Unreal | All assets | Level Sequence | 30s |
| 6 | Render | Sequence | Raw video | 45-90s |
| 7 | Post | Raw video | IG-ready MP4 | 20s |
| 8 | QA | Final video | Report | 10s |
| 9 | Publish | Video | Deliverables | 5s |

**Total Time (Fast Preview)**: ~2-3 minutes  
**Total Time (High Quality)**: ~8-12 minutes

## Requirements

### Software
- **macOS 13+** (Sonoma or Sequoia)
- **Python 3.13+** (Apple Silicon native)
- **Unreal Engine 5.4+** with MetaHuman plugin
- **FFmpeg** (video encoding)
- **Ollama** (local LLM - llama3.1)

### Hardware
- **M4 Pro** (48GB) - Recommended & tested
- **M3 Pro/Max** (36GB+) - Fully supported
- **M2 Pro/Max** (32GB+) - Supported
- **100GB+ free SSD space**

### Optional Capture Devices
- iPhone with Live Link Face app (optional facial)
- Motion capture suit (advanced movement)

## Configuration Presets

### Fast Preview (`--config fast_preview`)
- **Use case:** Rapid iteration, testing choreography
- **Render time:** ~2 min (30s reel)
- **Quality:** Draft  
- **Settings:** 1080x1920 @ 24fps, low AA

### Default (`--config default`)
- **Use case:** Standard Instagram posting
- **Render time:** ~6 min (30s reel)
- **Quality:** Production
- **Settings:** 1080x1920 @ 30fps, medium AA

### High Quality (`--config high_quality`)
- **Use case:** Viral-quality, featured content
- **Render time:** ~10 min (30s reel)
- **Quality:** Maximum
- **Settings:** 1080x1920 @ 60fps, high AA, motion blur

## CLI Usage

```bash
# Basic Instagram Reel generation
python main.py --performer PERFORMER_ID --brief BRIEF.md

# High quality mode
python main.py --performer dancer_001 --brief brief.md --config high_quality

# Resume from specific stage
python main.py --run-id 20251226_143022_dancer_001 --start-from-stage 6

# Dry run (preview execution plan)
python main.py --performer dancer_001 --brief brief.md --dry-run

# Force full rerun (ignore cache)
python main.py --performer dancer_001 --brief brief.md --force-rerun
```

## Scaling Multiple Performers

```bash
# Performer #1: Initial setup (7-14 days)
# - Configure pipeline
# - Create MetaHuman
# - Build animation library (15-30 dance/movement sequences)

# Performer #2+: Clone & customize (1-2 days each)
# - Clone brand pack
# - Import new MetaHuman  
# - Reuse 90% of animations & code
```

**Effort per additional performer:** ~10-15% of initial

## Technology Stack

| Category | Tool | Purpose |
|----------|------|---------|
| **LLM** | Ollama (llama3.1) | Concept generation |
| **Animation** | MetaHuman Animator | Procedural expressions |
| **Rendering** | Unreal Engine 5.4+ | Cinematic MetaHuman render |
| **Video** | FFmpeg | Instagram encoding |
| **Cache** | SHA256 hashing | Stage-level caching |
| **Orchestration** | Python 3.13 | Pipeline control |

## Output Deliverables

Each run produces:
- **Instagram Reel MP4** (1080x1920, optimized bitrate)
- **Raw render** (ProRes for editing)
- **Thumbnail variants** (3-5 options)
- **Metadata JSON** (caption, hashtags, timing)
- **QA report** (validation results)
- **Unreal sequence** (Level Sequence .uasset)

## Performance Benchmarks (M4 Pro 48GB)

| Video Length | Fast Preview | Default | High Quality |
|--------------|--------------|---------|--------------|
| 15s Reel | ~90s | ~3min | ~5min |
| 30s Reel | ~2min | ~6min | ~10min |
| 60s Reel | ~4min | ~12min | ~20min |
| 90s Reel | ~6min | ~18min | ~30min |

*Times include full pipeline execution with caching enabled*

## What You Need to Create

### 1. Unreal Engine Project
- MetaHuman character imported
- Studio/environment scene(s)
- Camera setup for 9:16 framing
- Lighting configuration

### 2. Animation Library
Build or source 15-30 animation sequences:
- **Dance routines** (5-15s choreographed sequences)
- **Movement clips** (1-5s gestures, poses, transitions)
- **Idle variations** (looping standing/swaying patterns)

*Tip: Mixamo, marketplace assets, or motion capture*

### 3. Brand Pack
Configure in `brand_packs/your_performer/`:
- `persona.json` - Character style, energy, preferences
- `scenes/` - Custom Unreal environments (optional)
- `overlays/` - Logo, graphics, branding (optional)

## Next Steps

1. **Setup**: Follow [SETUP.md](SETUP.md) for complete installation
2. **Quick Start**: See [QUICKSTART.md](QUICKSTART.md) for first video
3. **Architecture**: Read [ARCHITECTURE.md](ARCHITECTURE.md) for pipeline details
4. **Unreal Integration**: Review [UNREAL_AUTOMATION.md](UNREAL_AUTOMATION.md)

## License

MIT License

## Support

- **Documentation**: All `.md` files in root
- **Issues**: GitHub Issues
- **Updates**: Check [EXECUTION_PLAN.md](EXECUTION_PLAN.md) for roadmap

---

**Built for creators who want full control over their AI influencer pipeline**
