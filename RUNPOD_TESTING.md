# RunPod Testing Guide

## Quick Start on RunPod A40

### 1. Pull Latest Code
```bash
cd /workspace/ai-video-generator
git pull origin master
```

**Expected output:**
```
From https://github.com/shakey21/ai-video-generator
   23cc98d..4c60a46  master     -> origin/master
Updating 23cc98d..4c60a46
Fast-forward
 OPTIMIZATION_CHECKLIST.md | 178 ++++++++++++++++++++++++++++++++++
 models/detector.py         |  10 +-
 models/processor.py        |  10 ++
 3 files changed, 183 insertions(+), 5 deletions(-)
```

### 2. Launch Application
```bash
python app.py
```

**Expected behavior:**
- Loads models (Realistic Vision v5.1, ControlNets, YOLO, MiDaS)
- Launches Gradio on port 7860
- Access via RunPod HTTP proxy URL

### 3. Monitor GPU Memory (Separate Terminal)
```bash
watch -n 1 nvidia-smi
```

**What to watch:**
- Peak VRAM usage (should stay < 45GB on A40 48GB)
- Memory clears between segments
- No "CUDA out of memory" errors

## Test Scenarios

### Test 1: Basic Generation (No OOM)
**Video**: 5-10 second clip, 720p
**Settings**: Default model, background plate OFF
**Success criteria**:
- ✅ Completes without CUDA OOM error
- ✅ Output video generated in `outputs/` folder
- ✅ All 3 segments process successfully

**Monitor**:
```bash
# In separate terminal
tail -f /workspace/ai-video-generator/app.log
```

### Test 2: Stabilization Quality
**Video**: Handheld footage (shaky camera)
**Settings**: Default (stabilization enabled)
**Success criteria**:
- ✅ Generated person appears stable
- ✅ Output video retains original camera shake (re-applied)
- ✅ No warping artifacts at edges

**Check**:
- Compare input vs output side-by-side
- Original camera movement should be preserved
- Person should be smooth during generation

### Test 3: Foot Locking
**Video**: Walking/dancing clip
**Settings**: Default
**Success criteria**:
- ✅ Feet don't slide when in contact with ground
- ✅ Ankle positions stabilize during stance phase
- ✅ Natural movement preserved

**Visual check**:
- Watch feet during contact moments
- Should see clear plant/push without slide

### Test 4: Background Plate Extraction
**Video**: Any clip
**Settings**: Enable "Extract Background Plate"
**Success criteria**:
- ✅ Completes successfully
- ✅ Slightly longer processing time (expected)
- ✅ Background extraction logged in console

**Console output should show**:
```
🎨 Extracting background plate...
✅ Background plate extracted
```

### Test 5: Segment Processing Memory
**Video**: 30+ second clip (longer test)
**Settings**: Default
**Success criteria**:
- ✅ Processes all 3 segments without OOM
- ✅ VRAM resets between segments
- ✅ Output has smooth segment transitions

**Watch nvidia-smi**:
- Memory should spike during segment processing
- Should drop between segments
- Peak < 45GB

## Troubleshooting

### Issue: CUDA Out of Memory
**Diagnosis**:
```bash
# Check current VRAM
nvidia-smi
```

**Solutions**:
1. Use shorter video (< 10 seconds for testing)
2. Verify segment processing is working:
   ```bash
   grep "Processing segment" app.log
   ```
3. Check CUDA cache clearing:
   ```bash
   grep "torch.cuda.empty_cache" models/processor.py
   ```

### Issue: Foot Sliding Still Occurs
**Diagnosis**:
```bash
# Check foot locking is applied
grep "Applying foot locking" app.log
```

**Possible causes**:
- Pose keypoints not detected (check YOLO model loaded)
- Velocity threshold too high (check `utils/foot_lock.py`)
- Video too short to detect contacts

**Debug**:
```python
# In Python console
from utils.foot_lock import FootLocker
locker = FootLocker()
print(f"Velocity threshold: {locker.velocity_threshold}")
print(f"Height threshold: {locker.contact_height_threshold}")
```

### Issue: Stabilization Artifacts
**Symptoms**: Warped edges, black borders
**Cause**: Extreme camera motion exceeds stabilization limits

**Solution**:
- Disable stabilization for this clip:
  ```python
  # In processor.py constructor
  VideoProcessor(use_stabilization=False, use_segments=True)
  ```

### Issue: Segment Transitions Visible
**Symptoms**: Flickering or jump at segment boundaries
**Check**: Overlap blending
```bash
grep "_blend_segment_overlaps" models/processor.py
```

**Adjustment**:
- Increase overlap_frames in `utils/segmentation.py`:
  ```python
  VideoSegmenter(num_segments=3, overlap_frames=10)  # Default is 5
  ```

## Performance Benchmarks

### Expected Processing Times (A40 GPU)

| Video Length | Segments | Est. Time | Memory Peak |
|--------------|----------|-----------|-------------|
| 5 seconds    | 1        | ~2 min    | 25-30GB     |
| 10 seconds   | 3        | ~5 min    | 35-40GB     |
| 20 seconds   | 3        | ~10 min   | 40-45GB     |
| 30 seconds   | 3        | ~15 min   | 40-45GB     |

**Note**: Times vary based on resolution and complexity

### Optimization Tips

1. **Lower resolution for testing**:
   ```python
   # In video_utils.py, resize input
   frame = cv2.resize(frame, (640, 480))
   ```

2. **Reduce ControlNet strength** (if quality acceptable):
   ```python
   # In generator.py
   controlnet_conditioning_scale=[0.7, 0.5, 0.3]  # Reduce from [1.0, 0.8, 0.5]
   ```

3. **Skip background plate** for faster testing

## Success Indicators

### Console Output Should Show:
```
🎬 Loading video: input.mp4
🎥 Stabilizing video...
✅ Video stabilized
📐 Creating 3 segments...
✅ Segments created

🎬 Processing segment 1/3: approach (frames 0-55)
🦴 Extracting poses...
Segment 1: 100%|████████████| 55/55
👣 Applying foot locking...

🎬 Processing segment 2/3: hold (frames 50-110)
🦴 Extracting poses...
Segment 2: 100%|████████████| 60/60
👣 Applying foot locking...

🎬 Processing segment 3/3: exit (frames 105-152)
🦴 Extracting poses...
Segment 3: 100%|████████████| 47/47
👣 Applying foot locking...

🎥 Reapplying camera motion...
✅ Camera motion reapplied

💾 Writing output video...
Writing: 100%|████████████| 152/152
✅ Output saved: outputs/replaced_input.mp4
```

### Gradio UI Should Show:
- ✅ Video upload successful
- ✅ Progress bar advances smoothly
- ✅ Output video plays in preview
- ✅ Download button available

## Next Steps After Successful Testing

1. **Commit test results**:
   ```bash
   echo "Tested on RunPod A40 - all features working" > TEST_RESULTS.md
   git add TEST_RESULTS.md
   git commit -m "Add test results from RunPod A40"
   git push
   ```

2. **Tune parameters** based on observed quality

3. **Test different video types**:
   - Walking
   - Dancing
   - Sports movements
   - Different lighting conditions

4. **Production deployment**:
   - Set up persistent storage
   - Add batch processing
   - Implement queue system

## Quick Commands Reference

```bash
# Start app
python app.py

# Watch logs
tail -f app.log

# Monitor GPU
watch -n 1 nvidia-smi

# Check git status
git status

# Pull latest
git pull origin master

# View video outputs
ls -lh outputs/

# Clean outputs
rm outputs/*

# Restart app (if frozen)
pkill -f "python app.py"
python app.py
```

---

**Status**: Ready to test Phase 1+2 implementation on RunPod A40
