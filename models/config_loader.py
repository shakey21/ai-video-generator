import json
from pathlib import Path
from typing import Dict, Any

class ModelConfig:
    """Load and manage AI model configurations from JSON"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent / "model_config.json"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load model configuration from JSON file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Model config not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def get_model(self, model_name: str = "default_model") -> Dict[str, Any]:
        """Get specific model configuration"""
        if model_name not in self.config:
            raise ValueError(f"Model '{model_name}' not found in config")
        
        return self.config[model_name]
    
    def get_full_prompt(self, model_name: str = "default_model") -> str:
        """Get complete prompt with base + style modifiers"""
        model = self.get_model(model_name)
        return f"{model['base_prompt']}, {model['style_modifiers']}"
    
    def get_negative_prompt(self, model_name: str = "default_model") -> str:
        """Get negative prompt for model"""
        model = self.get_model(model_name)
        return model['negative_prompt']
    
    def get_inference_steps(self, model_name: str = "default_model") -> int:
        """Get inference steps for model"""
        model = self.get_model(model_name)
        return model.get('inference_steps', 30)
    
    def get_guidance_scale(self, model_name: str = "default_model") -> float:
        """Get guidance scale for model"""
        model = self.get_model(model_name)
        return model.get('guidance_scale', 7.5)
    
    def get_seed(self, model_name: str = "default_model") -> int:
        """Get seed for consistent generation"""
        model = self.get_model(model_name)
        return model.get('seed', 42)
    
    def update_model(self, model_name: str, updates: Dict[str, Any]):
        """Update model configuration and save to file"""
        if model_name not in self.config:
            self.config[model_name] = {}
        
        self.config[model_name].update(updates)
        self._save_config()
    
    def _save_config(self):
        """Save configuration back to JSON file"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
