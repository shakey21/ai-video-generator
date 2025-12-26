#!/usr/bin/env python3
"""
MetaHuman Influencer Pipeline CLI
Local-first AI influencer video generation using Unreal Engine MetaHumans
"""

import argparse
import sys
import logging
from pathlib import Path
from datetime import datetime
import yaml
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import MetaHumanPipeline
from src.utils.config import load_config, merge_configs
from src.utils.timing import Timer


def setup_logging(level: str = "INFO", log_file: Path = None):
    """Configure logging for pipeline execution."""
    log_format = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    
    handlers = [logging.StreamHandler()]
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=handlers
    )


def create_run_id(influencer_id: str, video_id: str = None) -> str:
    """Generate unique run ID: YYYYMMDD_HHMMSS_influencer_videoid"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    parts = [timestamp, influencer_id]
    if video_id:
        parts.append(video_id)
    return "_".join(parts)


def main():
    parser = argparse.ArgumentParser(
        description="MetaHuman Influencer Pipeline - Generate AI influencer videos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate video with default config
  python main.py --influencer tech_tips_001 --brief content_briefs/video_042.md
  
  # Fast preview mode
  python main.py --influencer tech_tips_001 --brief brief.md --config fast_preview
  
  # High quality render
  python main.py --influencer tech_tips_001 --brief brief.md --config high_quality
  
  # Resume from specific stage
  python main.py --run-id 20251224_143022_tech_tips_001 --start-from-stage render
  
  # Dry run (no execution)
  python main.py --influencer tech_tips_001 --brief brief.md --dry-run
        """
    )
    
    # Required arguments
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--influencer',
        type=str,
        help='Influencer ID (must have matching brand pack)'
    )
    group.add_argument(
        '--run-id',
        type=str,
        help='Resume existing run by ID'
    )
    
    # Input files
    parser.add_argument(
        '--brief',
        type=Path,
        help='Content brief markdown file (required for new runs)'
    )
    
    parser.add_argument(
        '--persona',
        type=Path,
        help='Custom persona JSON (overrides brand pack default)'
    )
    
    # Configuration
    parser.add_argument(
        '--config',
        type=str,
        default='default',
        choices=['default', 'fast_preview', 'high_quality'],
        help='Config preset to use (default: default)'
    )
    
    parser.add_argument(
        '--config-file',
        type=Path,
        help='Custom config YAML file'
    )
    
    # Pipeline control
    parser.add_argument(
        '--start-from-stage',
        type=int,
        metavar='N',
        help='Resume from stage N (1-10)'
    )
    
    parser.add_argument(
        '--end-at-stage',
        type=int,
        metavar='N',
        help='Stop after stage N (1-10)'
    )
    
    parser.add_argument(
        '--skip-stages',
        type=str,
        metavar='STAGES',
        help='Comma-separated list of stages to skip (e.g., "qa,publish")'
    )
    
    parser.add_argument(
        '--force-rerun',
        action='store_true',
        help='Force rerun all stages (ignore cache)'
    )
    
    # Output control
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('runs'),
        help='Base directory for pipeline runs (default: ./runs)'
    )
    
    parser.add_argument(
        '--video-id',
        type=str,
        help='Custom video ID for this run'
    )
    
    # Debugging
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show execution plan without running pipeline'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging (DEBUG level)'
    )
    
    parser.add_argument(
        '--keep-intermediate',
        action='store_true',
        help='Keep all intermediate files (don\'t clean up)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validation
    if args.influencer and not args.brief:
        parser.error("--brief is required when starting a new run")
    
    # Load configuration
    try:
        config = load_config(args.config)
        
        # Merge custom config if provided
        if args.config_file:
            custom_config = load_config(args.config_file)
            config = merge_configs(config, custom_config)
    
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        return 1
    
    # Create or load run directory
    if args.run_id:
        run_id = args.run_id
        run_dir = args.output_dir / run_id
        
        if not run_dir.exists():
            print(f"Error: Run directory not found: {run_dir}", file=sys.stderr)
            return 1
        
        # Load run metadata
        metadata_file = run_dir / "metadata.json"
        with open(metadata_file) as f:
            run_metadata = json.load(f)
        
        influencer_id = run_metadata['influencer_id']
    else:
        influencer_id = args.influencer
        run_id = create_run_id(influencer_id, args.video_id)
        run_dir = args.output_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # Save run metadata
        run_metadata = {
            'run_id': run_id,
            'influencer_id': influencer_id,
            'video_id': args.video_id,
            'brief': str(args.brief) if args.brief else None,
            'config_preset': args.config,
            'started_at': datetime.now().isoformat()
        }
        
        with open(run_dir / "metadata.json", 'w') as f:
            json.dump(run_metadata, f, indent=2)
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else config.get('logging', {}).get('level', 'INFO')
    log_file = run_dir / "logs" / "pipeline.log"
    setup_logging(log_level, log_file)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting MetaHuman Pipeline - Run ID: {run_id}")
    logger.info(f"Influencer: {influencer_id}")
    logger.info(f"Config: {args.config}")
    
    # Initialize pipeline
    try:
        pipeline = MetaHumanPipeline(
            config=config,
            run_dir=run_dir,
            influencer_id=influencer_id,
            content_brief=args.brief,
            persona_file=args.persona
        )
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}", exc_info=True)
        return 1
    
    # Configure pipeline options
    pipeline_options = {
        'start_from_stage': args.start_from_stage,
        'end_at_stage': args.end_at_stage,
        'skip_stages': args.skip_stages.split(',') if args.skip_stages else [],
        'force_rerun': args.force_rerun,
        'keep_intermediate': args.keep_intermediate,
        'dry_run': args.dry_run
    }
    
    # Show execution plan
    if args.dry_run:
        logger.info("DRY RUN MODE - No execution will occur")
        pipeline.print_execution_plan(pipeline_options)
        return 0
    
    # Execute pipeline
    timer = Timer()
    timer.start()
    
    try:
        result = pipeline.execute(**pipeline_options)
        
        timer.stop()
        
        if result['success']:
            logger.info("=" * 60)
            logger.info("Pipeline completed successfully!")
            logger.info(f"Total time: {timer.elapsed_str()}")
            logger.info(f"Output: {result['output_path']}")
            logger.info("=" * 60)
            
            # Print stage timings
            if config.get('logging', {}).get('stage_timing', False):
                logger.info("\nStage Timings:")
                for stage_name, stage_time in result['stage_timings'].items():
                    logger.info(f"  {stage_name}: {stage_time:.2f}s")
            
            return 0
        else:
            logger.error("Pipeline failed!")
            logger.error(f"Error: {result.get('error', 'Unknown error')}")
            logger.error(f"Failed at stage: {result.get('failed_stage', 'Unknown')}")
            return 1
    
    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user")
        return 130
    
    except Exception as e:
        logger.error(f"Pipeline failed with exception: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
