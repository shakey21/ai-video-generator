import warnings
warnings.filterwarnings("ignore", message=".*CUDA.*")

import gradio as gr
from pathlib import Path
from models.processor import VideoProcessor
from models.config_loader import ModelConfig

class VideoModelReplacer:
    def __init__(self):
        # Enable all advanced features by default
        self.processor = VideoProcessor(
            use_stabilization=True,  # Camera stabilization
            use_segments=True,  # Segment-based processing
            enable_upscaling=False  # 4K upscaling (disabled by default - very slow)
        )
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)
    
    def process_video(
        self, 
        input_video, 
        selected_model, 
        use_background_plate=False,
        enable_4k_upscale=False,
        progress=gr.Progress()
    ):
        """
        Process video with advanced features:
        - Camera stabilization
        - Segment-based generation (3 segments)
        - Foot locking
        - Temporal consistency with optical flow
        - Color correction to match original
        - Temporal denoising
        - Optional 4K upscaling
        """
        
        if input_video is None:
            return None
        
        try:
            progress(0, desc="Initializing...")
            
            # Update processor to use selected model and upscaling setting
            self.processor.generator.model_name = selected_model
            self.processor.enable_upscaling = enable_4k_upscale
            
            output_path = self.processor.replace_model(
                video_path=input_video,
                model_description=None,  # Uses JSON config
                use_background_plate=use_background_plate,
                progress_callback=progress
            )
            
            progress(1.0, desc="Complete")
            return output_path
            
        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

def create_ui():
    replacer = VideoModelReplacer()
    
    # Load model config dynamically
    config = ModelConfig()
    
    # Create mapping of display names to model keys
    model_choices = {}
    for key, model_data in config.config.items():
        display_name = model_data.get('name', key)
        model_choices[display_name] = key
    
    display_names = list(model_choices.keys())
    default_display = display_names[0] if display_names else "Default Model"
    
    with gr.Blocks(title="AI Video Model Replacer") as app:
        gr.Markdown("# AI Video Model Replacer")
        gr.Markdown("Replace people in videos with AI-generated models while preserving all movements and poses.")
        
        with gr.Row():
            with gr.Column(scale=1):
                input_video = gr.Video(
                    label="Input Video",
                    sources=["upload"]
                )
                
                model_selector = gr.Dropdown(
                    choices=display_names,
                    value=default_display,
                    label="AI Model",
                    interactive=True
                )
                
                with gr.Accordion("Advanced Options", open=False):
                    use_bg_plate = gr.Checkbox(
                        label="Extract Background Plate",
                        value=False,
                        info="Extract clean background for potential replacement"
                    )
                    
                    enable_4k = gr.Checkbox(
                        label="4K Upscaling (Real-ESRGAN)",
                        value=False,
                        info="⚠️ Very slow! Upscale output to 4K resolution"
                    )
                    
                    gr.Markdown("### Quality Features (Always On)")
                    gr.Markdown("✅ 1080p HD Output  \n✅ Color Correction  \n✅ Temporal Denoising  \n✅ Optical Flow Smoothing")
                
                process_btn = gr.Button("Process Video", variant="primary", size="lg")
            
            with gr.Column(scale=1):
                output_video = gr.Video(label="Output Video")
        
        def process_with_model_key(input_video, selected_display_name, use_bg_plate, enable_4k_upscale, progress=gr.Progress()):
            # Convert display name to model key
            model_key = model_choices.get(selected_display_name, "default_model")
            return replacer.process_video(input_video, model_key, use_bg_plate, enable_4k_upscale, progress)
        
        process_btn.click(
            fn=process_with_model_key,
            inputs=[input_video, model_selector, use_bg_plate, enable_4k],
            outputs=[output_video]
        )
    
    return app

if __name__ == "__main__":
    app = create_ui()
    
    css = """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    footer {display: none !important;}
    body {background-color: #000000 !important; color: #ffffff !important;}
    .gradio-container {background-color: #000000 !important;}
    
    /* Typography improvements */
    body, .gradio-container, button, input, textarea {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }
    
    /* Monospace for logs */
    .log-output, textarea[placeholder*="Log"], textarea[aria-label*="Log"] {
        font-family: 'JetBrains Mono', 'Monaco', 'Courier New', monospace !important;
        font-size: 13px !important;
        line-height: 1.6 !important;
    }
    
    /* Better markdown rendering */
    .markdown-body {
        font-size: 15px !important;
        line-height: 1.7 !important;
    }
    
    .markdown-body strong {
        font-weight: 600 !important;
    }
    """
    
    app.launch(
        share=True,
        server_name="0.0.0.0",
        server_port=7860,
        theme=gr.themes.Monochrome(),
        css=css
    )
