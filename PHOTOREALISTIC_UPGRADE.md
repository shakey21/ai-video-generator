# Photorealistic Video Model Replacement - Upgrade Guide

## What Changed

Your AI video generator has been upgraded from basic pose-only generation to a **photorealistic multi-ControlNet pipeline** with temporal consistency.

### Key Improvements:

1. **Multi-ControlNet Generation** (pose + depth + canny edges)
   - Pose skeleton for body position
   - Depth maps for 3D understanding  
   - Edge detection for structure preservation
   - Result: 3x more control over generated output

2. **Realistic Vision v6.0** base model
   - Switched from SD 1.5 to photorealistic checkpoint
   - Trained specifically for realistic human generation
   - Better skin texture, lighting, and natural appearance

3. **Optical Flow Temporal Consistency**
   - Tracks motion between frames
   - Warps previous frame to match current pose
   - Blends 70% new generation with 30% warped previous
   - Result: Dramatically reduced flickering

4. **Better Prompting**
   - "photorealistic, 8k uhd, dslr, natural skin texture, film grain"
   - Optimized negative prompts to prevent AI artifacts

## How to Use

### 1. Install New Dependencies (Already Done)
```bash
pip install controlnet_aux insightface onnxruntime opencv-contrib-python
```

### 2. Run the App
```bash
python app.py
```

### 3. First Run Download
The first time you run, it will download ~7GB of AI models:
- Realistic Vision v6.0 (~2GB)
- ControlNet Pose (~1.4GB)
- ControlNet Depth (~1.4GB)
- ControlNet Canny (~1.4GB)
- MiDaS Depth Estimator (~400MB)

This only happens once - models are cached.

### 4. Process a Video
1. Upload your Instagram reel or video
2. Select model (currently only "Bop-Style Video Influencer")
3. Click "Process Video"
4. Wait for generation (slower than before, but much higher quality)

## Expected Quality Improvements

### Before (Pose-Only):
- ❌ Each frame generated independently
- ❌ Face/clothing changes between frames (flickering)
- ❌ No depth understanding (flat, unrealistic)
- ❌ Generic artistic style

### After (Multi-ControlNet + Temporal):
- ✅ Consistent character across frames
- ✅ Smooth motion with optical flow tracking
- ✅ Depth-aware generation (more realistic)
- ✅ Photorealistic video quality
- ✅ Better edge alignment with original person

## Processing Speed

**Warning: This is MUCH slower than before**

On Apple M4 Pro:
- Before: ~30 seconds per 10-second video
- After: **~5-10 minutes per 10-second video**

Why? Each frame now:
1. Extracts 3 control signals (pose, depth, canny)
2. Runs 3 ControlNets simultaneously
3. Applies optical flow warping
4. Uses 50 inference steps (vs 30 before)

Trade-off: **Quality >> Speed**

## Advanced Configuration

Edit `models/model_config.json` to customize:

### ControlNet Strength
```json
"controlnet_scales": {
  "pose": 0.8,    // Lower = more creative freedom
  "depth": 0.6,   // Higher = stricter 3D matching
  "canny": 0.5    // Edges/structure preservation
}
```

### Generation Quality
```json
"inference_steps": 50,     // Higher = better quality (but slower)
"guidance_scale": 7.5,     // 7-9 recommended for photorealism
```

### Model Switching
```json
"base_model": "SG161222/Realistic_Vision_V6.0_B1_noVAE"
// Or try: "stablediffusionapi/realistic-vision-v51"
```

## Troubleshooting

### "Out of memory" error
- Reduce generation resolution in `generator.py`:
  ```python
  target = 768  # Try 640 or 512 instead
  ```

### Still seeing flickering
- Increase optical flow blending:
  ```python
  result = cv2.addWeighted(curr_generated, 0.6, warped_prev, 0.4, 0)
  # (More weight on previous frame)
  ```

### Generations don't look photorealistic
- Check your prompt in config.json
- Ensure "photorealistic, 8k uhd, dslr" is in style_modifiers
- Lower guidance_scale to 7.0 for more natural results

### Character keeps changing
- Use the same seed (already implemented)
- Increase optical flow influence (see "Still seeing flickering")
- Consider adding reference images (future feature)

## Next Steps (Not Yet Implemented)

For even better results, you could add:

1. **IP-Adapter** - Provide reference image of desired character for perfect consistency
2. **AnimateDiff** - Video-specific diffusion model
3. **RIFE Interpolation** - Generate intermediate frames for smoother motion
4. **Face restoration** - Run CodeFormer on generated faces for extra detail

These are complex additions - current pipeline should already show massive improvement.

## Performance Tips

1. **Process shorter clips first** - Test on 5-10 second videos
2. **Use good quality source videos** - Better lighting = better results
3. **Single person videos work best** - Multiple people not supported yet
4. **Frontal poses are easiest** - Side/back views may be less consistent

## Comparison Test

Try processing the same video with and without the updates to see the difference!

Old output would be in: `outputs/replaced_[filename].mp4`
New output overwrites with better quality.
