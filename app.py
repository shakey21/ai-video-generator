import warnings
warnings.filterwarnings("ignore", message=".*CUDA.*")

import gradio as gr
from pathlib import Path
from models.processor import VideoProcessor
from models.config_loader import ModelConfig

class VideoModelReplacer:
    def __init__(self):
        self.processor = VideoProcessor()
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)
    
    def process_video(self, input_video, selected_model, progress=gr.Progress()):
        """Process video and replace human model with AI-generated person from JSON config"""
        
        if input_video is None:
            return None
        
        try:
            progress(0, desc="Initializing...")
            
            # Update processor to use selected model
            self.processor.generator.model_name = selected_model
            
            output_path = self.processor.replace_model(
                video_path=input_video,
                model_description=None,  # Uses JSON config
                progress_callback=progress
            )
            
            progress(1.0, desc="Complete")
            return output_path
            
        except Exception as e:
            print(f"Error: {str(e)}")
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
                
                process_btn = gr.Button("Process Video", variant="primary", size="lg")
            
            with gr.Column(scale=1):
                output_video = gr.Video(label="Output Video")
        
        def process_with_model_key(input_video, selected_display_name, progress=gr.Progress()):
            # Convert display name to model key
            model_key = model_choices.get(selected_display_name, "default_model")
            return replacer.process_video(input_video, model_key, progress)
        
        process_btn.click(
            fn=process_with_model_key,
            inputs=[input_video, model_selector],
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
