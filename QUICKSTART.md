# Quick Start Guide

Get your first AI MetaHuman Instagram Reel in 30 minutes.

## Prerequisites Check

```bash
# Verify installations
python3 --version          # Should be 3.13+
ffmpeg -version            # Should be installed
ollama list                # Should show llama3.1
```

## 1. Setup (5 minutes)

```bash
# Clone and install
cd ai-metahuman-content-creator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start Ollama
ollama serve &
ollama pull llama3.1
```

## 2. Test Pipeline (2 minutes)

```bash
# Dry run to verify setup
python main.py \
  --performer performer_001 \
  --brief brand_packs/performer_001/content_briefs/example.md \
  --dry-run
```

You should see execution plan with 9 stages listed.

## 3. First Instagram Reel (Fast Preview)

```bash
# Generate 30s reel in fast preview mode
python main.py \
  --performer performer_001 \
  --brief brand_packs/performer_001/content_briefs/example.md \
  --config fast_preview
```

**Output**: `runs/YYYYMMDD_HHMMSS_performer_001/output/instagram_reel.mp4`

**Expected time**: ~2-3 minutes (M4 Pro)

## 4. Check Output

```bash
# Find your reel
ls -lt runs/ | head -1

# Play it
open runs/YYYYMMDD_HHMMSS_performer_001/06_post/video_final.mp4
```

## What's Next?

### Try High Quality Mode

```bash
python main.py \
  --performer performer_001 \
  --brief brand_packs/performer_001/content_briefs/example.md \
  --config high_quality
```

### Create Custom Content

1. Write new brief: `brand_packs/performer_001/content_briefs/my_reel.md`
2. Run pipeline: `python main.py --performer performer_001 --brief my_reel.md`

### Resume Failed Runs

```bash
# If pipeline fails at stage 6
python main.py --run-id YYYYMMDD_HHMMSS_performer_001 --start-from-stage 6
```

## Troubleshooting

**"Brand pack not found"**
- Ensure `brand_packs/performer_001/` exists
- Check `persona.json` is present

**"Config not found"**
- Verify `config/default.yaml` exists
- Try absolute path: `--config-file /full/path/to/config.yaml`

**"Ollama connection failed"**
```bash
# Start Ollama server
ollama serve
```

**"Module not found"**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

## Full Documentation

- **Setup**: See [SETUP.md](SETUP.md) for complete installation
- **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md) for pipeline design
- **Unreal**: See [UNREAL_AUTOMATION.md](UNREAL_AUTOMATION.md) for UE integration
- **Roadmap**: See [EXECUTION_PLAN.md](EXECUTION_PLAN.md) for 30-day plan

## CLI Reference

```bash
# Basic
python main.py --performer ID --brief FILE.md

# With config
python main.py --performer ID --brief FILE.md --config fast_preview

# Partial execution
python main.py --performer ID --brief FILE.md --end-at-stage 3

# Resume
python main.py --run-id RUN_ID --start-from-stage 6

# Skip stages
python main.py --performer ID --brief FILE.md --skip-stages qa,publish

# Force rerun (ignore cache)
python main.py --performer ID --brief FILE.md --force-rerun

# Dry run
python main.py --performer ID --brief FILE.md --dry-run

# Verbose logging
python main.py --performer ID --brief FILE.md --verbose
```

## Performance Tips

1. **Use caching**: Don't use `--force-rerun` unless needed
2. **Fast preview first**: Test with `--config fast_preview`
3. **Partial runs**: Use `--end-at-stage 5` to test early stages
4. **Monitor logs**: Check `runs/*/logs/pipeline.log` for issues

---

**Ready to build? Start with SETUP.md for full environment configuration.**
