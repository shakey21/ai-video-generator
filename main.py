#!/usr/bin/env python3
"""
MetaHuman Influencer Pipeline CLI
Generate AI influencer videos using Unreal Engine MetaHumans
"""

import argparse
import sys
import logging
from pathlib import Path
from datetime import datetime
import yaml
import json

sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import MetaHumanPipeline
from src.utils.config import load_config, merge_configs
from src.utils.timing import Timer


def setup_logging(level: str, log_file: Path = None):
    """Configure logging."""
    handlers = [logging.StreamHandler()]
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=handlers
    )


def create_run_id(influencer_id: str, video_id: str = None) -> str:
    """Generate run ID: YYYYMMDD_HHMMSS_influencer_videoid"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    parts = [timestamp, influencer_id]
    if video_id:
        parts.append(video_id)
    return "_".join(parts)


def main():
    parser = argparse.ArgumentParser(
        description="MetaHuman Influencer Pipeline",
        epilog="""
Examples:
  python main.py --influencer tech_tips --brief content_briefs/vid_001.md
  python main.py --influencer tech_tips --brief brief.md --config fast_preview
  python main.py --run-id 20251224_143022_tech_tips --start-from-stage 7
  python main.py --influencer tech_tips --brief brief.md --dry-run
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--influencer', help='Influencer ID')
    group.add_argument('--run-id', help='Resume existing run')
    
    parser.add_argument('--brief', type=Path, help='Content brief markdown')
    parser.add_argument('--persona', type=Path, help='Custom persona JSON')
    parser.add_argument('--config', default='default', 
                       choices=['default', 'fast_preview', 'high_quality'])
    parser.add_argument('--config-file', type=Path, help='Custom config YAML')
    parser.add_argument('--start-from-stage', type=int, metavar='N')
    parser.add_argument('--end-at-stage', type=int, metavar='N')
    parser.add_argument('--skip-stages', help='Comma-separated stages to skip')
    parser.add_argument('--force-rerun', action='store_true')
    parser.add_argument('--output-dir', type=Path, default=Path('runs'))
    parser.add_argument('--video-id', help='Custom video ID')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--verbose', action='store_true')
    
    args = parser.parse_args()
    
    if args.influencer and not args.brief:
        parser.error("--brief required for new runs")
    
    # Load config
    try:
        config = load_config(args.config)
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
            print(f"Error: Run not found: {run_dir}", file=sys.stderr)
            return 1
        with open(run_dir / "metadata.json") as f:
            run_metadata = json.load(f)
        influencer_id = run_metadata['influencer_id']
    else:
        influencer_id = args.influencer
        run_id = create_run_id(influencer_id, args.video_id)
        run_dir = args.output_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
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
    logger.info(f"MetaHuman Pipeline - Run: {run_id}")
    logger.info(f"Influencer: {influencer_id}, Config: {args.config}")
    
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
        logger.error(f"Failed to initialize: {e}", exc_info=True)
        return 1
    
    # Pipeline options
    options = {
        'start_from_stage': args.start_from_stage,
        'end_at_stage': args.end_at_stage,
        'skip_stages': args.skip_stages.split(',') if args.skip_stages else [],
        'force_rerun': args.force_rerun,
        'dry_run': args.dry_run
    }
    
    if args.dry_run:
        logger.info("DRY RUN - No execution")
        pipeline.print_execution_plan(options)
        return 0
    
    # Execute
    timer = Timer()
    timer.start()
    
    try:
        result = pipeline.execute(**options)
        timer.stop()
        
        if result['success']:
            logger.info("=" * 60)
            logger.info("Pipeline completed successfully!")
            logger.info(f"Total time: {timer.elapsed_str()}")
            logger.info(f"Output: {result['output_path']}")
            logger.info("=" * 60)
            
            if config.get('logging', {}).get('stage_timing'):
                logger.info("\nStage Timings:")
                for stage, t in result['stage_timings'].items():
                    logger.info(f"  {stage}: {t:.2f}s")
            
            return 0
        else:
            logger.error(f"Pipeline failed at: {result.get('failed_stage')}")
            logger.error(f"Error: {result.get('error')}")
            return 1
    
    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
