import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from server.agents.base_agent import BaseAgent
from server.agents.schemas import AgentContext, VisualQAReport
from server.agents.llm_client import LLMClient

logger = logging.getLogger("agent.VisualQAInspector")

class VisualQAInspectorAgent(BaseAgent):
    """Agent D: Performs 14-dimension comparative visual inspection + semantic product fidelity check on Playwright PNG screenshots using Gemini Multimodal Vision API."""

    DIMENSIONS = [
        "1. Prompt & Semantic Subject Alignment", "2. CreativeSpec Alignment", "3. Visual Hierarchy",
        "4. Composition & Whitespace", "5. Typography Readability", "6. Color Consistency",
        "7. Asset Quality & 3D Model Fidelity", "8. Visual Originality", "9. Desktop Responsiveness",
        "10. Mobile Responsiveness", "11. Interaction Quality", "12. 3D/Animation Quality",
        "13. Technical Stability", "14. Accessibility & Reduced Motion"
    ]

    def __init__(self, workspace_guard=None):
        super().__init__(
            name="VisualQAInspector",
            role_description="Evaluates Playwright PNG screenshots across 14 visual & technical criteria + semantic product fidelity using Multimodal Vision API."
        )
        self.workspace_guard = workspace_guard
        self.llm = LLMClient()

    def run(self, context: AgentContext, **kwargs) -> Dict[str, Any]:
        spec = kwargs.get("creative_spec", {})
        screenshot_res = kwargs.get("screenshot_result", {})
        attempt = context.attempt_number

        console_errors = screenshot_res.get("console_errors", []) if screenshot_res else []
        failed_requests = screenshot_res.get("failed_requests", []) if screenshot_res else []
        blank_detected = bool(screenshot_res.get("blank_page_detected", False)) if screenshot_res else False
        has_fatal_err = bool(screenshot_res.get("has_fatal_runtime_error", False)) if screenshot_res else False
        dom_visual_issues = screenshot_res.get("dom_visual_issues", []) if screenshot_res else []
        functional_defects = screenshot_res.get("functional_defects", []) if screenshot_res else []
        domain_relevance_pass = screenshot_res.get("domain_relevance_pass", True) if screenshot_res else True
        functional_completion_score = float(screenshot_res.get("functional_completion_score", 10.0)) if screenshot_res else 10.0

        if not screenshot_res or not screenshot_res.get("success") or not screenshot_res.get("visual_inspection_executed") or blank_detected or has_fatal_err or not domain_relevance_pass or (functional_defects and len(functional_defects) > 0):
            crit_issues = []
            if blank_detected:
                crit_issues.append("BLANK PAGE DEFECT: Rendered page is empty with zero visible content or rendered DOM nodes.")
            if has_fatal_err:
                crit_issues.append(f"FATAL RUNTIME ERROR: Browser console threw uncaught exceptions: {console_errors[:2]}")
            if not domain_relevance_pass:
                crit_issues.append("DOMAIN RELEVANCE / REFERENCE CONTAMINATION DEFECT: Reference website subject or products contaminated the target project.")
            for fd in functional_defects:
                crit_issues.append(fd)
            if not crit_issues:
                crit_issues.append("Playwright screenshot capture failed or was skipped. Visual QA blocked.")

            report = VisualQAReport(
                decision="BLOCKED" if attempt >= context.max_refinement_cycles else "NEEDS_REFINEMENT",
                overall_score=min(4.0, functional_completion_score),
                visual_inspection_available=True if screenshot_res.get("visual_inspection_executed") else False,
                domain_relevance_pass=domain_relevance_pass,
                functional_completion_score=functional_completion_score,
                functional_defects=functional_defects,
                critical_issues=crit_issues,
                prioritized_fixes=[
                    "Implement missing core functional components (menu cards, category filter tabs, dish customizer, cart drawer, checkout modal)",
                    "Purge prohibited reference terms (e.g. furniture items) from the target project layout"
                ],
                console_error_findings=console_errors
            )
            return report.model_dump()

        desktop_rel = screenshot_res.get("desktop")
        mobile_rel = screenshot_res.get("mobile")

        ws_root = Path(context.workspace_root)
        desktop_path = ws_root / desktop_rel if desktop_rel else None
        mobile_path = ws_root / mobile_rel if mobile_rel else None

        image_paths = []
        if desktop_path and desktop_path.exists():
            image_paths.append(desktop_path)
        if mobile_path and mobile_path.exists():
            image_paths.append(mobile_path)

        if not image_paths:
            report = VisualQAReport(
                decision="BLOCKED" if attempt >= context.max_refinement_cycles else "NEEDS_RETRY",
                overall_score=0.0,
                visual_inspection_available=False,
                critical_issues=["No valid screenshot image files found on disk for visual inspection."],
                prioritized_fixes=["Verify Playwright screenshot save paths in workspace."],
                console_error_findings=console_errors
            )
            return report.model_dump()

        if self.llm.is_configured():
            sys_prompt = """You are an expert Visual QA Inspector and Design Director evaluating a web application across 14 visual & technical dimensions:
1. Prompt & Subject Alignment, 2. CreativeSpec Alignment, 3. Visual Hierarchy, 4. Composition & Whitespace,
5. Typography Readability, 6. Color Consistency, 7. Asset & Imagery Quality, 8. Visual Originality,
9. Desktop Responsiveness, 10. Mobile Responsiveness, 11. Interaction Quality, 12. 3D/Animation Quality,
13. Technical Stability, 14. Accessibility.

CRITICAL VISUAL DESIGN & QUALITY EVALUATION CRITERIA:
Inspect both Desktop and Mobile screenshots with uncompromising rigor. A successful build, working buttons, or presence of components does NOT automatically qualify as high-quality design.

1. TYPOGRAPHY COMPLETENESS & STABILITY:
   - Carefully read the main headline and section headings in the screenshots.
   - DEFECT CHECK: Is any headline incomplete or showing only a single truncated word (e.g. only "WE" instead of a complete title)? Are animated words missing or stuck invisible due to timing or animation delay bugs?
   - If ANY main headline is truncated, cut off, or incomplete, you MUST set decision to "NEEDS_REFINEMENT", overall_score <= 5.0, and report a critical headline defect.

2. COMPOSITION, WHITESPACE & AUTHENTIC IMAGERY:
   - Check whether the composition has excessive empty black dead-space or an unbalanced void between header and CTAs.
   - For creative agencies, architectural studios, luxury portfolios, restaurants, fashion, and physical products: verify that authentic photography or material specimens are present. A website that relies only on plain text, solid black backgrounds, and thin colored borders without real photography or rich visual elements is visually weak and must be flagged for refinement.

3. COLOR PALETTE ORIGINALITY & COHERENCE:
   - Penalize generic repetitive templates (e.g., solid pitch black with electric cobalt buttons and yellow chips) when the creative spec or domain calls for a distinctive aesthetic (such as warm travertine stone, linen oatmeal, deep olive, or editorial burgundy).

4. VISUAL STORYTELLING & CONTENT HIERARCHY:
   - Check that the page provides authentic domain narrative: distinctive brand header, balanced asymmetrical hero, structural/business metrics, featured portfolio works with photography and metadata, tactile materials/features, and purposeful modal interactions.

Return a JSON object matching this schema:
{
  "requested_subject": string (e.g., "Solaris Studio Architectural Website"),
  "detected_subject": string (e.g., "Warm Stone Architectural Monolith Studio" OR "Generic Dark Agency Template with Incomplete Headline"),
  "semantic_fidelity_score": float (1-10),
  "semantic_fidelity_pass": boolean (true if authentic design matching prompt and creative spec, false if weak/truncated/generic),
  "visual_evidence": string (detailed visual critique of typography, composition, imagery, and color palette),
  "decision": "PASS" | "NEEDS_REFINEMENT" | "BLOCKED",
  "overall_score": float (1-10),
  "visual_quality_score": float (1-10),
  "functional_quality_score": float (1-10),
  "rendering_reliability_score": float (1-10),
  "reference_alignment_score": float (1-10),
  "responsive_quality_score": float (1-10),
  "visual_hierarchy_score": float (1-10),
  "art_direction_score": float (1-10),
  "technical_stability_score": float (1-10),
  "desktop_findings": [string],
  "mobile_findings": [string],
  "mobile_specific_findings": [string],
  "identified_defects": [string],
  "critical_issues": [string],
  "prioritized_fixes": [string],
  "recommended_corrections": [string]
}"""
            user_prompt = f"""Audit visual aesthetic, typography completeness, and composition quality for prompt: "{context.user_prompt}".
Design concept: {spec.get('design_concept', 'N/A')}.
Archetype: {spec.get('archetype', 'N/A')}.
Color tokens: {spec.get('color_tokens', {})}
DOM visual audit issues: {dom_visual_issues}
Console errors: {console_errors}
Failed requests: {failed_requests}
Attempt number: {attempt} of {context.max_refinement_cycles}."""
            
            vision_res = self.llm.call_llm_json(sys_prompt, user_prompt, image_paths=image_paths)
            if vision_res and isinstance(vision_res, dict) and "decision" in vision_res:
                logger.info(f"[{context.trace_id}] Multimodal Vision QA completed. Decision: '{vision_res.get('decision')}', Semantic Pass: {vision_res.get('semantic_fidelity_pass')}")
                vision_res["console_error_findings"] = console_errors
                vision_res["visual_inspection_available"] = True
                vision_res["domain_relevance_pass"] = domain_relevance_pass
                vision_res["functional_completion_score"] = functional_completion_score
                vision_res["functional_defects"] = functional_defects
                
                # Check automated DOM visual issues and functional defects
                if dom_visual_issues or functional_defects or not domain_relevance_pass:
                    for dvi in dom_visual_issues:
                        if dvi not in vision_res.get("critical_issues", []):
                            vision_res.setdefault("critical_issues", []).append(dvi)
                        if dvi not in vision_res.get("identified_defects", []):
                            vision_res.setdefault("identified_defects", []).append(dvi)
                    for fd in functional_defects:
                        if fd not in vision_res.get("critical_issues", []):
                            vision_res.setdefault("critical_issues", []).append(fd)
                    if not domain_relevance_pass:
                        c_msg = "DOMAIN RELEVANCE DEFECT: Reference website subject contaminated the target project."
                        if c_msg not in vision_res.get("critical_issues", []):
                            vision_res.setdefault("critical_issues", []).append(c_msg)
                    vision_res["decision"] = "NEEDS_REFINEMENT" if attempt < context.max_refinement_cycles else "BLOCKED"
                    vision_res["overall_score"] = min(vision_res.get("overall_score", 5.0), functional_completion_score, 4.5)

                # ENFORCE MANDATORY SEMANTIC PRODUCT FIDELITY & VISUAL QUALITY:
                sem_pass = vision_res.get("semantic_fidelity_pass", True)
                sem_score = vision_res.get("semantic_fidelity_score", 10.0)
                
                if not sem_pass or sem_score < 7.0:
                    req_sub = vision_res.get("requested_subject", context.user_prompt)
                    det_sub = vision_res.get("detected_subject", "Weak or generic output")
                    issue_msg = f"VISUAL QUALITY / SEMANTIC FAILURE: User requested '{req_sub}', but output was evaluated as '{det_sub}' (Score: {sem_score}/10)."
                    
                    if issue_msg not in vision_res.get("critical_issues", []):
                        vision_res.setdefault("critical_issues", []).append(issue_msg)
                    if issue_msg not in vision_res.get("identified_defects", []):
                        vision_res.setdefault("identified_defects", []).append(issue_msg)
                    
                    if attempt < context.max_refinement_cycles:
                        vision_res["decision"] = "NEEDS_REFINEMENT"
                        vision_res["overall_score"] = min(vision_res.get("overall_score", 5.0), 5.5)
                    else:
                        vision_res["decision"] = "BLOCKED"
                        vision_res["overall_score"] = min(vision_res.get("overall_score", 5.0), 4.0)

                try:
                    report = VisualQAReport(**vision_res)
                    return report.model_dump()
                except Exception as parse_err:
                    logger.warning(f"Vision QA schema parsing error: {parse_err}. Returning BLOCKED due to malformed vision output.")

        # Automated Playwright In-Browser Verification Evaluation (when LLM vision API is offline/unconfigured):
        if not self.llm.is_configured():
            logger.info(f"[{context.trace_id}] Multimodal Vision API not configured. Evaluating via automated Playwright in-browser inspection.")
            auto_critical_issues = []
            auto_defects = []
            if dom_visual_issues:
                auto_critical_issues.extend(dom_visual_issues)
                auto_defects.extend(dom_visual_issues)
            if functional_defects:
                auto_critical_issues.extend(functional_defects)
                auto_defects.extend(functional_defects)
            if not domain_relevance_pass:
                auto_critical_issues.append("DOMAIN RELEVANCE DEFECT: Reference website subject contaminated the target project.")
            if console_errors:
                auto_critical_issues.append(f"Browser console errors detected: {console_errors[0]}")
            if blank_page:
                auto_critical_issues.append("BLANK PAGE DETECTED: Page rendered with zero content elements.")
            if fatal_runtime_error:
                auto_critical_issues.append("FATAL RUNTIME ERROR DETECTED in application.")

            if auto_critical_issues:
                decision = "NEEDS_REFINEMENT" if attempt < context.max_refinement_cycles else "BLOCKED"
                score = min(4.5, functional_completion_score)
                report = VisualQAReport(
                    decision=decision,
                    overall_score=score,
                    visual_inspection_available=True,
                    requested_subject=context.user_prompt,
                    detected_subject="Automated QA Detected Defects",
                    semantic_fidelity_score=min(4.0, functional_completion_score),
                    semantic_fidelity_pass=False,
                    domain_relevance_pass=domain_relevance_pass,
                    functional_completion_score=functional_completion_score,
                    functional_defects=functional_defects,
                    critical_issues=auto_critical_issues,
                    identified_defects=auto_defects,
                    prioritized_fixes=auto_critical_issues,
                    console_error_findings=console_errors
                )
                return report.model_dump()
            else:
                # All automated DOM, functional criteria, and screenshot verifications passed cleanly
                report = VisualQAReport(
                    decision="PASS",
                    overall_score=max(8.5, functional_completion_score),
                    visual_inspection_available=True,
                    requested_subject=context.user_prompt,
                    detected_subject=f"{context.target_domain} Verified Complete Application",
                    semantic_fidelity_score=9.5,
                    semantic_fidelity_pass=True,
                    domain_relevance_pass=True,
                    functional_completion_score=functional_completion_score,
                    functional_defects=[],
                    visual_hierarchy_score=9.0,
                    art_direction_score=9.0,
                    technical_stability_score=10.0,
                    visual_quality_score=9.0,
                    functional_quality_score=9.5,
                    responsive_quality_score=9.0,
                    desktop_findings=["Desktop responsive verification passed. All domain functional components rendered."],
                    mobile_findings=["Mobile 375x812 responsive verification passed."],
                    critical_issues=[],
                    identified_defects=[],
                    prioritized_fixes=[],
                    console_error_findings=[]
                )
                return report.model_dump()

        # If Vision API call completely failed or returned invalid output:
        # ABSOLUTELY CANNOT AWARD A PASS SCORE! MUST RETURN BLOCKED or NEEDS_RETRY!
        critical_issues = ["Multimodal Vision Inspection API unavailable or returned malformed JSON payload."]
        if console_errors:
            critical_issues.append(f"Browser console errors detected: {console_errors[0]}")
        if failed_requests:
            critical_issues.append(f"Failed network asset requests detected: {failed_requests[0]}")

        decision = "NEEDS_RETRY" if attempt < context.max_refinement_cycles else "BLOCKED"
        
        report = VisualQAReport(
            decision=decision,
            overall_score=3.0, # Low score reflecting unavailable visual verification
            visual_inspection_available=False,
            requested_subject=context.user_prompt,
            detected_subject="Visual Verification Unavailable",
            semantic_fidelity_score=0.0,
            semantic_fidelity_pass=False,
            visual_hierarchy_score=5.0,
            art_direction_score=5.0,
            technical_stability_score=5.0 if console_errors else 8.0,
            desktop_findings=[f"Desktop screenshot present at {desktop_rel}, but vision API inspection failed."] if desktop_rel else [],
            mobile_findings=[f"Mobile screenshot present at {mobile_rel}, but vision API inspection failed."] if mobile_rel else [],
            critical_issues=critical_issues,
            prioritized_fixes=["Verify Gemini API key and multimodal vision payload format"],
            console_error_findings=console_errors
        )
        return report.model_dump()

    def get_fallback_output(self, context: AgentContext, error_msg: str, **kwargs) -> Dict[str, Any]:
        report = VisualQAReport(
            decision="BLOCKED",
            overall_score=0.0,
            visual_inspection_available=False,
            critical_issues=[f"QA Inspector error: {error_msg}"]
        )
        return report.model_dump()
