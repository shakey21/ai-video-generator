# Unreal Engine Automation Guide

## Overview

This guide shows how to programmatically control Unreal Engine 5 from Python to assemble and render MetaHuman videos.

---

## Setup

### 1. Enable Python Plugin in Unreal

1. Open your Unreal project
2. Edit → Plugins → Search "Python"
3. Enable "Python Editor Script Plugin"
4. Enable "Editor Scripting Utilities"
5. Restart editor

### 2. Configure Python Paths

Edit → Project Settings → Plugins → Python:
- Enable "Developer Mode"
- Add to "Additional Paths": `/Users/you/ai-metahuman-influencer/unreal_scripts`

### 3. Test Python Access

Output Log → Py console:
```python
import unreal
print(unreal.SystemLibrary.get_engine_version())
```

---

## Core Automation Tasks

### Create Level Sequence

**File**: `unreal_scripts/create_sequence.py`

```python
import unreal

def create_level_sequence(sequence_name, duration_seconds=45):
    """Create a new Level Sequence for the video."""
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    
    sequence = asset_tools.create_asset(
        asset_name=sequence_name,
        package_path="/Game/Sequences",
        asset_class=unreal.LevelSequence,
        factory=unreal.LevelSequenceFactoryNew()
    )
    
    sequence.set_display_rate(unreal.FrameRate(30, 1))
    sequence.set_playback_end_seconds(duration_seconds)
    
    unreal.EditorAssetLibrary.save_loaded_asset(sequence)
    return sequence
```

---

### Import Audio

```python
def import_audio(audio_file_path, sequence):
    """Import audio and add to sequence."""
    import_task = unreal.AssetImportTask()
    import_task.filename = audio_file_path
    import_task.destination_path = "/Game/Audio/Narration"
    import_task.automated = True
    import_task.save = True
    
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    asset_tools.import_asset_tasks([import_task])
    
    sound_wave = unreal.load_asset(import_task.imported_object_paths[0])
    
    audio_track = sequence.add_master_track(unreal.MovieSceneAudioTrack)
    audio_section = audio_track.add_section()
    audio_section.set_sound(sound_wave)
    audio_section.set_range(0, int(sound_wave.get_duration() * 30))
    
    unreal.EditorAssetLibrary.save_loaded_asset(sequence)
```

---

### Add MetaHuman to Sequence

```python
def add_metahuman(sequence, metahuman_bp_path):
    """Spawn MetaHuman in sequence."""
    metahuman_bp = unreal.load_asset(metahuman_bp_path)
    
    binding = sequence.add_spawnable_from_class(
        metahuman_bp.generated_class()
    )
    
    # Set spawn location
    spawnable = binding.get_object_template()
    spawnable.set_actor_location(unreal.Vector(0, 0, 100), False, False)
    
    unreal.EditorAssetLibrary.save_loaded_asset(sequence)
    return binding
```

---

### Apply Facial Animation

```python
import json

def apply_facial_curves(sequence, metahuman_binding, curves_json_path):
    """Apply blend shape curves from JSON."""
    with open(curves_json_path) as f:
        data = json.load(f)
    
    control_rig_track = metahuman_binding.add_track(
        unreal.MovieSceneControlRigParameterTrack
    )
    section = control_rig_track.add_section()
    
    for curve_name, keyframes in data['curves'].items():
        channel = section.add_scalar_parameter_key(curve_name)
        
        for frame, value in keyframes:
            channel.add_key(unreal.FrameNumber(frame), value)
    
    unreal.EditorAssetLibrary.save_loaded_asset(sequence)
```

---

### Apply Body Animation

```python
def apply_body_animation(sequence, metahuman_binding, anim_asset_path):
    """Apply body animation asset."""
    anim = unreal.load_asset(anim_asset_path)
    
    skel_track = metahuman_binding.add_track(
        unreal.MovieSceneSkeletalAnimationTrack
    )
    skel_section = skel_track.add_section()
    
    skel_section.params.set_editor_property("Animation", anim)
    duration_frames = int(anim.get_editor_property("sequence_length") * 30)
    skel_section.set_range(0, duration_frames)
    
    unreal.EditorAssetLibrary.save_loaded_asset(sequence)
```

---

### Add Camera

```python
def add_camera(sequence, location=(250, 0, 160)):
    """Add cine camera for 9:16 vertical framing."""
    camera_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.CineCameraActor,
        unreal.Vector(*location),
        unreal.Rotator(0, 0, 0)
    )
    
    # Configure for vertical video
    cine_camera = camera_actor.get_cine_camera_component()
    cine_camera.set_editor_property("filmback", 
        unreal.CameraFilmbackSettings(
            sensor_width=9.0,
            sensor_height=16.0
        )
    )
    cine_camera.set_editor_property("current_focal_length", 50.0)
    
    # Add to sequence
    camera_binding = sequence.add_possessable(camera_actor)
    
    # Set as camera cut
    cut_track = sequence.add_master_track(unreal.MovieSceneCameraCutTrack)
    cut_section = cut_track.add_section()
    cut_section.set_camera_binding_id(camera_binding.get_id())
    
    unreal.EditorAssetLibrary.save_loaded_asset(sequence)
```

---

### Configure Render Settings

```python
def configure_render_queue(sequence, output_path, preset="HighQuality"):
    """Setup Movie Render Queue."""
    subsystem = unreal.get_editor_subsystem(
        unreal.MoviePipelineQueueSubsystem
    )
    queue = subsystem.get_queue()
    
    job = queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
    job.sequence = unreal.SoftObjectPath(sequence.get_path_name())
    job.map = unreal.SoftObjectPath("/Game/Maps/RenderingMap")
    
    config = job.get_configuration()
    
    # Output settings
    output_setting = config.find_or_add_setting_by_class(
        unreal.MoviePipelineOutputSetting
    )
    output_setting.output_directory = unreal.DirectoryPath(output_path)
    output_setting.file_name_format = "{sequence_name}"
    output_setting.output_resolution = unreal.IntPoint(1080, 1920)
    output_setting.output_frame_rate = unreal.FrameRate(30, 1)
    
    # Quality settings
    if preset == "HighQuality":
        deferred = config.find_or_add_setting_by_class(
            unreal.MoviePipelineDeferredPassBase
        )
        aa = config.find_or_add_setting_by_class(
            unreal.MoviePipelineAntiAliasingSetting
        )
        aa.spatial_sample_count = 32
        aa.temporal_sample_count = 8
    
    # Apple ProRes output
    prores = config.find_or_add_setting_by_class(
        unreal.MoviePipelineAppleProResOutput
    )
    prores.codec = unreal.AppleProResEncoderCodec.PRORES_422_HQ
    
    return job
```

---

## Complete Assembly Script

**File**: `unreal_scripts/assemble_sequence.py`

```python
#!/usr/bin/env python3
import unreal
import sys
import json

def assemble_video_sequence(config_path):
    """
    Complete assembly: create sequence, add assets, configure render.
    
    Config JSON:
    {
        "sequence_name": "Influencer001_Video042",
        "audio_path": "/path/to/narration.wav",
        "metahuman_bp": "/Game/MetaHumans/Influencer001/BP_Influencer001",
        "facial_curves": "/path/to/face_curves.json",
        "body_animation": "/Game/Animations/Gesture_Explain_001",
        "output_path": "/path/to/renders/run_001"
    }
    """
    with open(config_path) as f:
        config = json.load(f)
    
    print("=== Unreal Sequence Assembly ===")
    
    # 1. Create sequence
    print("[1/7] Creating sequence...")
    sequence = create_level_sequence(config['sequence_name'])
    
    # 2. Import audio
    print("[2/7] Importing audio...")
    import_audio(config['audio_path'], sequence)
    
    # 3. Add MetaHuman
    print("[3/7] Adding MetaHuman...")
    mh_binding = add_metahuman(sequence, config['metahuman_bp'])
    
    # 4. Apply facial animation
    print("[4/7] Applying facial animation...")
    apply_facial_curves(sequence, mh_binding, config['facial_curves'])
    
    # 5. Apply body animation
    print("[5/7] Applying body animation...")
    apply_body_animation(sequence, mh_binding, config['body_animation'])
    
    # 6. Add camera
    print("[6/7] Adding camera...")
    add_camera(sequence)
    
    # 7. Configure render
    print("[7/7] Configuring render queue...")
    render_job = configure_render_queue(
        sequence,
        config['output_path'],
        config.get('render_preset', 'HighQuality')
    )
    
    print("=== Assembly Complete ===")
    print(f"Sequence: {sequence.get_path_name()}")
    print("Ready to render via Movie Render Queue")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: assemble_sequence.py <config.json>")
        sys.exit(1)
    
    assemble_video_sequence(sys.argv[1])
```

---

## Running from CLI

### Execute Python Script

```bash
/Applications/UE_5.7/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor \
  /Users/you/MyProject/MyProject.uproject \
  -ExecutePythonScript="/path/to/assemble_sequence.py /path/to/config.json" \
  -stdout -unattended -nopause -nosplash
```

### Trigger Render

```python
# In Unreal Python console or script
import unreal

def start_render():
    subsystem = unreal.get_editor_subsystem(
        unreal.MoviePipelineQueueSubsystem
    )
    executor = unreal.MoviePipelinePIEExecutor()
    subsystem.render_queue_with_executor(executor)

start_render()
```

---

## Live Link Face Integration

### Recording Workflow

1. **Setup**:
   - Install Live Link Face app on iPhone
   - In Unreal: Window → Live Link
   - Add source: Live Link Face (enter iPhone IP)

2. **Capture**:
   - Actor performs script while iPhone captures
   - Live Link streams 52 ARKit blend shapes

3. **Record to Sequence**:
   - Open Level Sequence
   - Add MetaHuman
   - In Live Link: Record → Take Recorder
   - Sequence now contains facial keyframes

4. **Use in Pipeline**:
   - Export as animation asset
   - Reference in config: `"facial_animation": "/Game/Captures/Take001"`

---

## MetaHuman Animator

### Audio → Face Workflow

1. Import audio WAV to Content Browser
2. Window → MetaHuman → MetaHuman Animator
3. Select MetaHuman + audio file
4. Click "Solve" (generates facial animation)
5. Export solved animation
6. Reference in pipeline config

**Note**: Currently cannot be automated via Python. Must run manually or via Blueprint.

---

## Debugging

### Enable Logging

```python
unreal.log("Your message")
unreal.log_warning("Warning!")
unreal.log_error("Error!")
```

View in: Output Log → Py

### Verify Assets

```python
asset = unreal.EditorAssetLibrary.load_asset("/Game/MyAsset")
if asset is None:
    print("Asset not found!")
```

### List Sequences

```python
sequences = unreal.EditorAssetLibrary.list_assets("/Game/Sequences")
for seq in sequences:
    print(seq)
```

---

## Performance Tips

1. **Reuse sequences**: Clone instead of creating new
2. **Batch imports**: Import multiple assets in one call
3. **Cache renders**: Don't re-render unchanged sequences
4. **Async rendering**: Queue multiple jobs overnight

---

## Next Steps

- See **ARCHITECTURE.md** for pipeline design
- See **EXECUTION_PLAN.md** for implementation roadmap
