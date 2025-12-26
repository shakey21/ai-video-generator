# Setup Guide

## Prerequisites

### Hardware
- **Mac with Apple Silicon** (M2 Pro or better)
- **M4 Pro 48GB** (recommended and tested)
- **M3 Pro/Max 36GB+** (fully supported)
- **48GB+ RAM** recommended (32GB minimum)
- **100GB+ free SSD space**

### Software
- **macOS 13+** (Sonoma or Sequoia)
- **Python 3.13+**
- **Homebrew** package manager

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/you/ai-metahuman-content-creator
cd ai-metahuman-content-creator
```

### 2. Install System Dependencies

```bash
# FFmpeg for video processing
brew install ffmpeg

# Ollama for local LLM
brew install ollama
ollama pull llama3.1
```

### 3. Install Python Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Unreal Engine Setup

### 1. Install Unreal Engine 5.4+

Download from: https://www.unrealengine.com/download

Choose **Apple Silicon** build for Mac (native M-series support).

### 2. Create Project

1. Launch Unreal Engine
2. Create new project:
   - Template: **Blank**
   - Name: `MetaHumanContentCreator`
   - Location: `/Users/YOU/UnrealProjects/`

### 3. Install MetaHuman Plugin

1. Edit → Plugins
2. Search "MetaHuman"
3. Enable:
   - MetaHuman
   - MetaHuman Animator
4. Restart editor

### 4. Enable Python Plugin

1. Edit → Plugins
2. Search "Python"
3. Enable:
   - Python Editor Script Plugin
   - Editor Scripting Utilities
4. Restart editor

### 5. Configure Python Paths

1. Edit → Project Settings → Plugins → Python
2. Enable "Developer Mode"
3. Add to "Additional Paths":
   ```
   /Users/YOU/ai-metahuman-content-creator/unreal_scripts
   ```

### 6. Test Python Access

1. Window → Output Log
2. Switch to "Py" console
3. Run:
   ```python
   import unreal
   print(unreal.SystemLibrary.get_engine_version())
   ```

---

## MetaHuman Creation

### 1. Download MetaHuman Creator

1. Open Epic Games Launcher
2. Library → Quixel Bridge
3. Launch Quixel Bridge
4. Sign in

### 2. Create MetaHuman

1. MetaHuman tab in Quixel Bridge
2. Click "Create MetaHuman"
3. Customize appearance:
   - Face shape, skin, hair
   - Clothing (modern, stylish for Instagram)
   - Body type
4. Name it (e.g., "DancerAI")
5. Download to Unreal project

### 3. Import to Unreal

1. In Quixel Bridge: Send to Unreal
2. Select your project
3. Wait for import
4. MetaHuman appears in: `Content/MetaHumans/DancerAI/`

### 4. Create Blueprint

1. Right-click in Content Browser
2. Blueprint Class → Actor
3. Name: `BP_DancerAI`
4. Open blueprint
5. Add Component → Skeletal Mesh
6. Set to MetaHuman body
7. Compile and save

---

## Running the Pipeline
tts.tts_to_file(text="Hello, this is a test", file_path="test.wav")
```

---

## Configuration

### 1. Update config/default.yaml

Edit `unreal.project_path` and `unreal.editor_path`:

```yaml
unreal:
  project_path: "/Users/YOU/UnrealProjects/MetaHumanInfluencer/MetaHumanInfluencer.uproject"
  editor_path: "/Users/Shared/Epic Games/UE_5.7/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor"
```

### 2. Update persona.json

Edit `brand_packs/influencer_001/persona.json`:

```json
{
  "appearance": {
    "metahuman_blueprint": "/Game/MetaHumans/YOUR_METAHUMAN_NAME/BP_YOUR_METAHUMAN_NAME"
  }
}
```

---

## Verification

### Test Pipeline CLI

```bash
python main.py --help
```

### Test Dry Run

```bash
python main.py \
  --influencer influencer_001 \
  --brief brand_packs/influencer_001/content_briefs/example.md \
  --dry-run
```

### Test Unreal Python

```bash
/Users/Shared/Epic\ Games/UE_5.7/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor \
  /Users/YOU/UnrealProjects/MetaHumanInfluencer/MetaHumanInfluencer.uproject \
  -ExecutePythonScript="$PWD/unreal_scripts/test_connection.py" \
  -stdout -unattended -nopause
```

---

## Troubleshooting

### Python Import Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Unreal Python Not Working
- Verify Python plugin is enabled
- Check Additional Paths in settings
- Restart Unreal Editor

### Voice Model Issues
- Ensure WAV files are 44.1kHz mono
- Check GPU/CPU availability for training
- Try pre-trained models first

### FFmpeg Not Found
```bash
brew install ffmpeg
which ffmpeg  # Should show /opt/homebrew/bin/ffmpeg
```

---

## Optional: iPhone Setup (Live Link Face)

### 1. Install App
- Download "Live Link Face" from App Store (free)

### 2. Connect to Unreal
1. In Unreal: Window → Live Link
2. Click "+" → Message Bus Source
3. Enter iPhone IP address
4. iPhone app should show "Connected"

### 3. Record Performance
1. Open Level Sequence in Unreal
2. Add MetaHuman to sequence
3. In Live Link: Record → Take Recorder
4. Perform script on iPhone
5. Stop recording → animation saved

---

## Next Steps

1. **Test Stage 1-2**: Generate script → synthesize voice
2. **Create First Video**: Run full pipeline in fast preview mode
3. **Review Output**: Check quality, adjust settings
4. **Document Issues**: Note any workarounds needed

See **EXECUTION_PLAN.md** for 30-day roadmap.
