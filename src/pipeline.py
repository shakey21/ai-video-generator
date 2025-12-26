"""
MetaHuman Pipeline Orchestrator
Coordinates 10-stage execution with caching
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from src.utils.timing import Timer
from src.utils.cache import CacheManager


@dataclass
class StageResult:
    """Result from pipeline stage."""
    stage_name: str
    success: bool
    output_path: Optional[Path] = None
    metadata: Dict[str, Any] = None
    error: Optional[str] = None
    cached: bool = False
    duration_seconds: float = 0.0


class MetaHumanPipeline:
    """
    MetaHuman influencer video generation pipeline.
    
    Manages 10-stage execution, caching, error handling.
    """
    
    STAGE_NAMES = [
        'planning', 'facial', 'body', 'scene',
        'unreal', 'render', 'post', 'qa', 'publish'
    ]
    
    def __init__(
        self,
        config: Dict[str, Any],
        run_dir: Path,
        influencer_id: str,
        content_brief: Optional[Path] = None,
        persona_file: Optional[Path] = None
    ):
        self.config = config
        self.run_dir = Path(run_dir)
        self.influencer_id = influencer_id
        self.content_brief = content_brief
        self.persona_file = persona_file
        
        self.logger = logging.getLogger(__name__)
        self.cache_manager = CacheManager(self.run_dir, config.get('cache', {}))
        
        # Load brand pack
        self.brand_pack_dir = Path(f"brand_packs/{influencer_id}")
        if not self.brand_pack_dir.exists():
            raise ValueError(f"Brand pack not found: {self.brand_pack_dir}")
        
        # Load persona
        if persona_file:
            with open(persona_file) as f:
                self.persona = json.load(f)
        else:
            persona_path = self.brand_pack_dir / "persona.json"
            with open(persona_path) as f:
                self.persona = json.load(f)
        
        # Create stage directories
        for i, stage_name in enumerate(self.STAGE_NAMES):
            (self.run_dir / f"{i:02d}_{stage_name}").mkdir(exist_ok=True)
        
        self.stage_results: Dict[str, StageResult] = {}
    
    def execute(
        self,
        start_from_stage: Optional[int] = None,
        end_at_stage: Optional[int] = None,
        skip_stages: List[str] = None,
        force_rerun: bool = False,
        dry_run: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute pipeline stages."""
        skip_stages = skip_stages or []
        timer = Timer()
        timer.start()
        
        start_idx = (start_from_stage - 1) if start_from_stage else 0
        end_idx = end_at_stage if end_at_stage else len(self.STAGE_NAMES)
        
        self.logger.info(f"Executing stages {start_idx+1} to {end_idx}")
        
        for i in range(start_idx, end_idx):
            stage_name = self.STAGE_NAMES[i]
            stage_num = i + 1
            
            if stage_name in skip_stages:
                self.logger.info(f"[{stage_num}/10] Skipping: {stage_name}")
                continue
            
            self.logger.info(f"[{stage_num}/10] Starting: {stage_name}")
            
            if dry_run:
                self.logger.info(f"  [DRY RUN] Would execute: {stage_name}")
                continue
            
            # Check cache
            if not force_rerun and self.cache_manager.is_cached(stage_name):
                self.logger.info(f"  Using cached: {stage_name}")
                result = StageResult(stage_name=stage_name, success=True, cached=True)
            else:
                result = self._execute_stage(stage_name, stage_num)
            
            self.stage_results[stage_name] = result
            
            if not result.success:
                self.logger.error(f"Failed: {stage_name} - {result.error}")
                return {
                    'success': False,
                    'failed_stage': stage_name,
                    'error': result.error,
                    'stage_timings': self._get_timings()
                }
            
            self.logger.info(f"  ✓ {stage_name} ({result.duration_seconds:.2f}s)")
        
        timer.stop()
        
        return {
            'success': True,
            'output_path': self._get_final_output(),
            'stage_timings': self._get_timings(),
            'total_duration': timer.elapsed()
        }
    
    def _execute_stage(self, stage_name: str, stage_num: int) -> StageResult:
        """Execute single stage."""
        timer = Timer()
        timer.start()
        
        stage_dir = self.run_dir / f"{stage_num-1:02d}_{stage_name}"
        
        try:
            # Placeholder - actual implementations in stage modules
            self.logger.info(f"  Stage {stage_name} implementation pending")
            self.logger.info(f"  See EXECUTION_PLAN.md for roadmap")
            
            # Create dummy output
            output = {
                'output_path': stage_dir / f"{stage_name}_output.txt",
                'metadata': {'stage': stage_name}
            }
            
            # Write placeholder
            with open(output['output_path'], 'w') as f:
                f.write(f"Placeholder output for {stage_name}\n")
            
            timer.stop()
            self.cache_manager.save(stage_name, output)
            
            return StageResult(
                stage_name=stage_name,
                success=True,
                output_path=output['output_path'],
                metadata=output.get('metadata'),
                duration_seconds=timer.elapsed()
            )
        
        except Exception as e:
            timer.stop()
            self.logger.error(f"Stage failed: {stage_name}", exc_info=True)
            return StageResult(
                stage_name=stage_name,
                success=False,
                error=str(e),
                duration_seconds=timer.elapsed()
            )
    
    def _get_timings(self) -> Dict[str, float]:
        """Get stage timings."""
        return {
            name: result.duration_seconds
            for name, result in self.stage_results.items()
        }
    
    def _get_final_output(self) -> Optional[Path]:
        """Get final output path."""
        for stage in ['publish', 'post', 'render']:
            result = self.stage_results.get(stage)
            if result and result.output_path:
                return result.output_path
        return None
    
    def print_execution_plan(self, options: Dict[str, Any]):
        """Print execution plan (dry-run)."""
        print("\n" + "=" * 60)
        print("EXECUTION PLAN")
        print("=" * 60)
        print(f"Run ID: {self.run_dir.name}")
        print(f"Influencer: {self.influencer_id}")
        print(f"Brief: {self.content_brief}")
        print(f"\nStages:")
        
        start = (options.get('start_from_stage', 1) - 1) if options.get('start_from_stage') else 0
        end = options.get('end_at_stage') or len(self.STAGE_NAMES)
        skip = options.get('skip_stages', [])
        
        for i in range(start, end):
            stage = self.STAGE_NAMES[i]
            status = "SKIP" if stage in skip else "RUN"
            cached = "✓ CACHED" if self.cache_manager.is_cached(stage) else ""
            print(f"  [{i+1:2d}] {stage:15s} [{status}] {cached}")
        
        print("=" * 60 + "\n")
