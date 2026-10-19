import os
import sys
import json
import time
import shutil
import logging
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from server.security.workspace_guard import WorkspaceGuard
from server.agents.orchestrator import MultiAgentOrchestrator
from server.tools.dev_visual_qa_tools import DevVisualQATools

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger('phase3_1_audit')

class DummyGuard:
    def __init__(self, root_path):
        self.workspace_root = root_path

def run_phase3_1_audit():
    logger.info('Starting HERMES DEV STUDIO — PHASE 3.1: INDEPENDENT VISUAL QUALITY AUDIT')

    workspace_root = PROJECT_ROOT / 'workspace'
    workspace_root.mkdir(parents=True, exist_ok=True)
    
    guard = DummyGuard(workspace_root)
    orchestrator = MultiAgentOrchestrator(guard)

    audit_dir = workspace_root / '.visual_qa' / 'phase3_1_independent_audit'
    audit_dir.mkdir(parents=True, exist_ok=True)

    ref_img_path = os.getenv("HERMES_REFERENCE_IMAGE_PATH", "")
    if not ref_img_path or not os.path.exists(ref_img_path):
        ref_img_path = None

    benchmarks = [
        {
            'id': 'bench_a_luxury_audio',
            'category': 'Premium Product Commerce',
            'prompt': 'Create a high-end luxury audiophile headphones web application with interactive 3D product storytelling, spatial audio visualization, technical specs, and responsive e-commerce checkout flow.',
            'reference_images': None
        },
        {
            'id': 'bench_b_brutalist_artist',
            'category': 'Experimental Creative Portfolio',
            'prompt': 'Create an experimental digital artist portfolio featuring avant-garde typography, horizontal scroll transitions, immersive motion design, and interactive artwork gallery.',
            'reference_images': None
        },
        {
            'id': 'bench_c_timber_architecture',
            'category': 'Architecture & Spatial Experience',
            'prompt': 'Create an immersive sustainable architecture studio website with spatial composition, minimalist structural typography, material palette explorer, and smooth 3D viewport spatial transitions.',
            'reference_images': None
        },
        {
            'id': 'bench_d_ai_saas_platform',
            'category': 'Premium SaaS',
            'prompt': 'Create a premium SaaS landing page for an AI Autonomous Developer Workflow Platform featuring real-time telemetry graphs, dark mode glassmorphism, interactive feature cards, and clear pricing conversions.',
            'reference_images': None
        },
        {
            'id': 'bench_e_horology_reference',
            'category': 'Reference-Driven Website',
            'prompt': 'Create a minimalist luxury mechanical watch horology studio website featuring precision craftsmanship timelines, interactive movement assembly, and bespoke ordering.',
            'reference_images': [ref_img_path] if ref_img_path else None
        }
    ]

    audit_summary = {
        'audit_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'pipeline_verification': {},
        'benchmark_results': {},
        'creative_differentiation_audit': {},
        'asset_quality_audit': {},
        'visual_qa_reliability': {}
    }

    for bench in benchmarks:
        bench_id = bench['id']
        logger.info('==================================================')
        logger.info(f'Executing Audit Benchmark: {bench_id} ({bench["category"]})')
        logger.info('==================================================')

        bench_audit_dir = audit_dir / bench_id
        bench_audit_dir.mkdir(parents=True, exist_ok=True)
        bench_proj_dir = bench_audit_dir / 'project'
        bench_proj_dir.mkdir(parents=True, exist_ok=True)

        start_time = time.time()
        res = orchestrator.generate_project(
            project_name=bench_id,
            user_prompt=bench['prompt'],
            max_cycles=2,
            reference_images=bench['reference_images']
        )
        duration_s = time.time() - start_time

        proj_src = workspace_root / bench_id
        if proj_src.exists():
            for item in proj_src.iterdir():
                if item.is_file():
                    shutil.copy2(item, bench_proj_dir / item.name)
                elif item.is_dir() and item.name != '.visual_qa':
                    dest_sub = bench_proj_dir / item.name
                    if dest_sub.exists():
                        shutil.rmtree(dest_sub)
                    shutil.copytree(item, dest_sub)

        # Copy screenshots
        qa_src = proj_src / '.visual_qa'
        desktop_png = qa_src / 'desktop.png' if qa_src.exists() else None
        mobile_png = qa_src / 'mobile.png' if qa_src.exists() else None

        if desktop_png and desktop_png.exists():
            shutil.copy2(desktop_png, bench_audit_dir / 'final_desktop.png')
        if mobile_png and mobile_png.exists():
            shutil.copy2(mobile_png, bench_audit_dir / 'final_mobile.png')

        refinement_hist = res.get('refinement_history', [])
        if refinement_hist:
            first_cycle = refinement_hist[0]
            if first_cycle.get('desktop_png') and os.path.exists(first_cycle['desktop_png']):
                shutil.copy2(first_cycle['desktop_png'], bench_audit_dir / 'initial_desktop.png')
            if first_cycle.get('mobile_png') and os.path.exists(first_cycle['mobile_png']):
                shutil.copy2(first_cycle['mobile_png'], bench_audit_dir / 'initial_mobile.png')

        # Save artifacts
        with open(bench_audit_dir / 'selected_creative_spec.json', 'w') as f:
            json.dump(res.get('creative_spec', {}), f, indent=2)

        with open(bench_audit_dir / 'reference_spec.json', 'w') as f:
            json.dump(res.get('reference_spec', {}), f, indent=2)

        with open(bench_audit_dir / 'final_qa_report.json', 'w') as f:
            json.dump(res.get('qa_report', {}), f, indent=2)

        with open(bench_audit_dir / 'agent_execution_logs.json', 'w') as f:
            json.dump(res.get('agent_execution_logs', []), f, indent=2)

        # Check build and runtime health
        index_html = bench_proj_dir / 'index.html'
        build_passed = index_html.exists()
        console_errors = res.get('screenshot_result', {}).get('console_errors', [])

        qa_report = res.get('qa_report', {})
        qa_decision = qa_report.get('decision', 'BLOCKED')
        overall_score = qa_report.get('overall_score', 0)
        dimensions = qa_report.get('dimension_scores', {})

        status = 'FAIL'
        if build_passed and qa_decision == 'PASS' and overall_score >= 80 and not console_errors:
            status = 'PASS'
        elif build_passed and overall_score >= 60:
            status = 'PARTIAL'

        bench_result_entry = {
            'benchmark_id': bench_id,
            'category': bench['category'],
            'prompt': bench['prompt'],
            'build_healthy': build_passed,
            'runtime_healthy': len(console_errors) == 0,
            'qa_decision': qa_decision,
            'overall_score': overall_score,
            'dimension_scores': dimensions,
            'console_errors': console_errors,
            'refinement_cycles': res.get('refinement_cycles_executed', 1),
            'execution_duration_sec': round(duration_s, 2),
            'final_status': status,
            'desktop_screenshot': str(bench_audit_dir / 'final_desktop.png'),
            'mobile_screenshot': str(bench_audit_dir / 'final_mobile.png')
        }
        audit_summary['benchmark_results'][bench_id] = bench_result_entry
        logger.info(f'Benchmark {bench_id} Completed: Status={status}, Score={overall_score}, QA Decision={qa_decision}')

    # Save overall summary
    summary_path = audit_dir / 'audit_summary.json'
    with open(summary_path, 'w') as f:
        json.dump(audit_summary, f, indent=2)

    logger.info('==================================================')
    logger.info(f'Phase 3.1 Audit execution finished! Summary written to {summary_path}')
    logger.info('==================================================')

if __name__ == '__main__':
    run_phase3_1_audit()
