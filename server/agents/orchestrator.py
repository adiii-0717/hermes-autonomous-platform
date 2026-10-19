import time
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from server.agents.schemas import AgentContext, AgentResponse, CreativeDirectionSpec, VisualQAReport, ReferenceDesignSpec
from server.agents.reference_inspector import ReferenceInspector
from server.agents.creative_director_agent import CreativeDirectorAgent
from server.agents.frontend_engineer_agent import FrontendEngineerAgent
from server.agents.motion_3d_engineer_agent import Motion3DEngineerAgent
from server.agents.visual_qa_inspector_agent import VisualQAInspectorAgent
from server.tools.dev_visual_qa_tools import DevVisualQATools

logger = logging.getLogger("agent.Orchestrator")

class MultiAgentOrchestrator:
    """Production Multi-Agent Orchestrator with structured execution states, progress callbacks, intermediate state preservation, and project manifest persistence."""

    EXECUTION_STATES = [
        "INITIATED", "ANALYZING_REFERENCE", "EXPLORING_DIRECTIONS",
        "GENERATING_FRONTEND", "GENERATING_3D_MOTION", "CAPTURING_SCREENSHOTS",
        "PERFORMING_VISUAL_QA", "REFINING_CODE", "COMPLETED", "FAILED"
    ]

    def __init__(self, workspace_guard):
        self.guard = workspace_guard
        self.workspace_root = Path(self.guard.workspace_root)
        
        self.reference_inspector = ReferenceInspector()
        self.creative_director = CreativeDirectorAgent()
        self.frontend_engineer = FrontendEngineerAgent()
        self.motion_3d_engineer = Motion3DEngineerAgent()
        self.visual_qa_inspector = VisualQAInspectorAgent(self.guard)
        self.qa_tools = DevVisualQATools(self.guard)

    def _save_generation_state(self, proj_dir: Path, state: str, progress: int, details: Dict[str, Any]):
        try:
            proj_dir.mkdir(parents=True, exist_ok=True)
            state_file = proj_dir / ".generation_state.json"
            payload = {
                "state": state,
                "progress_percent": progress,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "details": details
            }
            state_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except Exception as err:
            logger.warning(f"Failed to save generation state: {err}")

    def _notify_status(self, callback: Optional[Callable[[Dict[str, Any]], None]], state: str, progress: int, message: str, project_name: str):
        evt = {
            "event": "generation_status_update",
            "project_name": project_name,
            "state": state,
            "progress_percent": progress,
            "message": message,
            "timestamp": time.time()
        }
        if callback:
            try:
                callback(evt)
            except Exception as cb_err:
                logger.warning(f"Status callback warning: {cb_err}")

    def generate_project(
        self,
        project_name: str,
        user_prompt: str,
        max_cycles: int = 3,
        reference_images: Optional[List[str]] = None,
        status_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """Executes full Phase 4 production multi-agent orchestration with progress reporting and state persistence."""
        start_time = time.time()
        if self.workspace_root.name == project_name:
            proj_dir = self.workspace_root
        else:
            proj_dir = self.workspace_root / project_name
        proj_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Orchestration starting for project '{project_name}' at {proj_dir} with prompt: '{user_prompt}'")
        self._notify_status(status_callback, "INITIATED", 5, "Initializing project workspace & agent context...", project_name)
        self._save_generation_state(proj_dir, "INITIATED", 5, {"user_prompt": user_prompt})

        # Separate target project brief from visual references using PromptReferenceParser
        from server.tools.prompt_reference_parser import PromptReferenceParser
        parsed_req = PromptReferenceParser.parse(user_prompt, attached_images=reference_images or [])

        context = AgentContext(
            project_name=project_name,
            user_prompt=user_prompt,
            workspace_root=str(proj_dir),
            target_project_brief=parsed_req["target_project_brief"],
            design_reference_instructions=parsed_req["design_reference_instructions"],
            is_replication_request=parsed_req["is_replication_request"],
            target_domain=parsed_req["target_domain"],
            functional_checklist=parsed_req["functional_requirements"],
            max_refinement_cycles=max_cycles
        )
        agent_logs = []

        # 1. Reference Inspector Agent
        self._notify_status(status_callback, "ANALYZING_REFERENCE", 15, "Analyzing visual reference screenshots & extracting design traits...", project_name)
        ref_response = self.reference_inspector.execute(context, reference_images=parsed_req["reference_images"])
        agent_logs.append(ref_response.model_dump())
        ref_spec = ref_response.data
        self._save_generation_state(proj_dir, "ANALYZING_REFERENCE", 20, {"reference_spec": ref_spec})

        # 2. Creative Director Agent
        self._notify_status(status_callback, "EXPLORING_DIRECTIONS", 30, "Exploring candidate creative directions & domain adaptation...", project_name)
        cd_response = self.creative_director.execute(context, reference_spec=ref_spec)
        agent_logs.append(cd_response.model_dump())
        creative_spec = cd_response.data
        self._save_generation_state(proj_dir, "EXPLORING_DIRECTIONS", 35, {"creative_spec": creative_spec})

        prioritized_fixes = []
        final_qa_report = {}
        screenshot_res = {}
        cycle_count = 0
        refinement_history = []

        # Bounded Refinement Loop
        for cycle in range(1, max_cycles + 1):
            cycle_count = cycle
            context.attempt_number = cycle
            logger.info(f"[{context.trace_id}] Starting Refinement Cycle {cycle}/{max_cycles}...")

            # 3. Frontend Engineer Agent
            self._notify_status(status_callback, "GENERATING_FRONTEND", 50, f"Generating HTML/CSS layout & responsive components (Cycle {cycle})...", project_name)
            fe_response = self.frontend_engineer.execute(
                context,
                creative_spec=creative_spec,
                prioritized_fixes=prioritized_fixes
            )
            agent_logs.append(fe_response.model_dump())

            # 4. 3D & Motion Engineer Agent
            self._notify_status(status_callback, "GENERATING_3D_MOTION", 65, f"Building progressive WebGL 3D scene & GSAP scroll timelines (Cycle {cycle})...", project_name)
            m3d_response = self.motion_3d_engineer.execute(
                context,
                creative_spec=creative_spec
            )
            agent_logs.append(m3d_response.model_dump())
            self._save_generation_state(proj_dir, "GENERATING_3D_MOTION", 70, {"cycle": cycle, "fe_status": fe_response.status, "m3d_status": m3d_response.status})

            # 5. Playwright Responsive Screenshot Capture & Functional Criteria Verification
            self._notify_status(status_callback, "CAPTURING_SCREENSHOTS", 80, f"Capturing responsive 1440x900 & 375x812 preview screenshots & validating functional criteria (Cycle {cycle})...", project_name)
            screenshot_res = self.qa_tools.capture_responsive_screenshots(
                project_name,
                target_domain=context.target_domain,
                functional_checklist=context.functional_checklist
            )

            # 6. Visual QA Inspector Agent (14-Dimension Multimodal Vision API)
            self._notify_status(status_callback, "PERFORMING_VISUAL_QA", 90, f"Evaluating 14 visual & technical criteria via Multimodal Vision API (Cycle {cycle})...", project_name)
            qa_response = self.visual_qa_inspector.execute(
                context,
                creative_spec=creative_spec,
                screenshot_result=screenshot_res
            )
            agent_logs.append(qa_response.model_dump())
            final_qa_report = qa_response.data

            decision = final_qa_report.get("decision", "PASS")
            prioritized_fixes = final_qa_report.get("prioritized_fixes", [])

            refinement_history.append({
                "cycle": cycle,
                "decision": decision,
                "overall_score": final_qa_report.get("overall_score"),
                "prioritized_fixes": prioritized_fixes,
                "desktop_png": screenshot_res.get("desktop"),
                "mobile_png": screenshot_res.get("mobile")
            })

            logger.info(f"[{context.trace_id}] Cycle {cycle} QA Decision: {decision}")

            if decision == "PASS" or not prioritized_fixes:
                logger.info(f"[{context.trace_id}] Visual Quality Criteria Satisfied on Cycle {cycle}!")
                break
            elif decision == "BLOCKED":
                logger.warning(f"[{context.trace_id}] Visual QA BLOCKED. Terminating refinement loop.")
                break

        elapsed_ms = (time.time() - start_time) * 1000.0

        final_decision = final_qa_report.get("decision", "PASS")
        if final_decision == "PASS":
            final_status = "SUCCESS"
        elif final_decision == "NEEDS_REFINEMENT":
            final_status = "PARTIAL"
        else:
            final_status = "BLOCKED"

        # Save project manifest
        try:
            manifest_file = proj_dir / ".project_manifest.json"
            manifest_payload = {
                "name": project_name,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": final_status,
                "qa_decision": final_decision,
                "overall_score": final_qa_report.get("overall_score", 0),
                "refinement_cycles": cycle_count,
                "execution_time_ms": elapsed_ms,
                "languages": ["html", "css", "javascript"]
            }
            manifest_file.write_text(json.dumps(manifest_payload, indent=2), encoding="utf-8")
        except Exception as m_err:
            logger.warning(f"Failed to write .project_manifest.json: {m_err}")

        self._notify_status(status_callback, "COMPLETED", 100, f"Project '{project_name}' generation finished with status {final_status}!", project_name)
        self._save_generation_state(proj_dir, "COMPLETED", 100, {"status": final_status, "decision": final_decision})

        return {
            "project_name": project_name,
            "status": final_status,
            "reference_spec": ref_spec,
            "creative_spec": creative_spec,
            "qa_report": final_qa_report,
            "screenshot_result": screenshot_res,
            "refinement_cycles_executed": cycle_count,
            "refinement_history": refinement_history,
            "agent_execution_logs": agent_logs,
            "total_execution_time_ms": elapsed_ms
        }
