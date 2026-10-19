import time
import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ReferenceDesignSpec(BaseModel):
    """Structured extraction of visual characteristics from user-supplied reference screenshots."""
    visual_identity: str = Field(default="Modern Editorial", description="Overall aesthetic identity extracted from reference")
    layout_structure: str = Field(default="Asymmetric Grid", description="Composition and grid layout structure")
    typography_hierarchy: str = Field(default="High Contrast Serif/Sans", description="Font pairings and scale hierarchy")
    color_palette: List[str] = Field(default_factory=list, description="Dominant and accent color hex tokens")
    composition_spatial_rhythm: str = Field(default="Fluid grid with generous vertical rhythm", description="Spatial spacing and content cadence")
    visual_density: str = Field(default="Clean Editorial", description="Content density and visual rhythm")
    image_treatment: str = Field(default="High-contrast product showcase", description="Aspect ratio, cropping, and framing")
    shape_language: str = Field(default="Subtle architectural geometry", description="Corner radii, border strokes, and silhouettes")
    interaction_motion_cues: str = Field(default="Scroll-linked parallax", description="Observed animation and section transition style")
    visual_atmosphere: str = Field(default="Sophisticated Dark Slate", description="Mood, lighting, and ambient tone")
    brand_personality: str = Field(default="Technical Elegance", description="Brand voice and character")
    adaptable_elements: List[str] = Field(default_factory=list, description="Key aesthetic principles to adapt to target domain")
    protected_elements_to_avoid: List[str] = Field(default_factory=list, description="Copyrighted logos or proprietary elements to avoid")

class CreativeDirectionSpec(BaseModel):
    """Structured design direction produced by the Creative Director Agent."""
    design_concept: str = Field(description="Core visual concept and title rationale")
    visual_identity: str = Field(description="Brand personality and design archetype")
    target_domain: str = Field(default="CREATIVE_AGENCY", description="Primary industry domain for content & business logic")
    functional_checklist: List[Dict[str, Any]] = Field(default_factory=list, description="Verifiable functional features required for domain completeness")
    signature_interaction: str = Field(default="", description="Memorable domain-specific interactive feature")
    section_sequence: List[str] = Field(default_factory=list, description="Complete page section layout sequence")
    design_principles_borrowed: List[str] = Field(default_factory=list, description="Visual principles borrowed from reference without subject contamination")
    color_tokens: Dict[str, str] = Field(default_factory=dict, description="CSS variable color tokens")
    typography_system: Dict[str, Any] = Field(default_factory=dict, description="Google fonts and typography scale")
    layout_rules: List[str] = Field(default_factory=list, description="Container max-widths, spacing, and grid rules")
    motion_philosophy: str = Field(default="", description="GSAP scroll and interaction motion rules")
    requires_3d: bool = Field(default=False, description="Whether spatial 3D viewport is required")
    three_d_spec: Dict[str, Any] = Field(default_factory=dict, description="R3F model URL, cameraZ, lighting, and particles spec")
    progressive_rendering_fallback: Dict[str, Any] = Field(default_factory=dict, description="Immediate SVG/CSS hero fallback, animation CSS, and WebGL timeout guard")
    domain_adaptation_notes: str = Field(default="", description="Explicit rationale for translating reference traits into target product domain")
    asset_spec: Dict[str, Any] = Field(default_factory=dict, description="Curated Unsplash CDNs, HDR maps, and fallback rules")
    responsive_rules: List[str] = Field(default_factory=list, description="Mobile breakpoint and drawer navigation rules")
    accessibility_rules: List[str] = Field(default_factory=list, description="A11y ARIA and reduced-motion fallback rules")
    anti_patterns: List[str] = Field(default_factory=list, description="Explicit visual tropes to avoid")
    react_bits_spec: Dict[str, Any] = Field(default_factory=dict, description="Purpose-selected React Bits animated backgrounds, text effects, and cards")
    icon_spec: Dict[str, Any] = Field(default_factory=dict, description="Lucide React vector icons and clean typographic branding guidelines")


class VisualQAReport(BaseModel):
    visual_inspection_available: bool = Field(default=True, description="Whether multimodal vision inspection was successfully executed")
    requested_subject: str = Field(default="N/A", description="Primary subject requested in user prompt")
    detected_subject: str = Field(default="N/A", description="Primary subject detected in rendered screenshots")
    semantic_fidelity_score: float = Field(default=5.0, description="1-10 semantic product recognition score")
    semantic_fidelity_pass: bool = Field(default=False, description="Whether rendered 3D product matches requested subject")
    domain_relevance_pass: bool = Field(default=True, description="Whether rendered content matches target domain without reference contamination")
    functional_completion_score: float = Field(default=5.0, description="1-10 score for functional criteria completeness (menu, search, cart, checkout)")
    functional_defects: List[str] = Field(default_factory=list, description="Identified functional or interactive defects")
    visual_evidence: str = Field(default="", description="Visual evidence for subject detection")
    identified_defects: List[str] = Field(default_factory=list, description="Identified visual or semantic defects")
    recommended_corrections: List[str] = Field(default_factory=list, description="Recommended fixes for refinement loop")

    """Structured visual inspection critique produced by the Visual QA Inspector Agent."""
    decision: str = Field(description="'PASS', 'NEEDS_REFINEMENT', or 'BLOCKED'")
    overall_score: float = Field(default=5.0, description="1-10 visual quality score")
    visual_quality_score: float = Field(default=5.0, description="1-10 aesthetic & visual composition score")
    functional_quality_score: float = Field(default=5.0, description="1-10 interaction & functional correctness score")
    rendering_reliability_score: float = Field(default=5.0, description="1-10 WebGL & asset rendering stability score")
    reference_alignment_score: float = Field(default=5.0, description="1-10 domain-adapted reference alignment score")
    responsive_quality_score: float = Field(default=5.0, description="1-10 mobile & desktop layout responsiveness score")
    visual_hierarchy_score: float = Field(default=5.0, description="1-10 visual hierarchy rating")
    art_direction_score: float = Field(default=5.0, description="1-10 art direction distinctiveness")
    technical_stability_score: float = Field(default=5.0, description="1-10 runtime stability score")
    desktop_findings: List[str] = Field(default_factory=list, description="Desktop screenshot critique points")
    mobile_findings: List[str] = Field(default_factory=list, description="Mobile screenshot critique points")
    mobile_specific_findings: List[str] = Field(default_factory=list, description="Detailed mobile typography, touch target, and container findings")
    critical_issues: List[str] = Field(default_factory=list, description="Blocking defects")
    prioritized_fixes: List[str] = Field(default_factory=list, description="Actionable fix recommendations for refinement loop")
    refinement_progress_delta: Dict[str, str] = Field(default_factory=dict, description="Dimension improvement comparison vs previous cycle ('+','-','=')")
    console_error_findings: List[str] = Field(default_factory=list, description="Evaluation of browser console logs")

class AgentContext(BaseModel):
    """Shared contextual execution envelope passed to agents."""
    project_name: str
    user_prompt: str
    workspace_root: str
    target_project_brief: str = Field(default="", description="Clean target product requirements separated from reference text")
    design_reference_instructions: str = Field(default="", description="Visual guidelines extracted from references")
    is_replication_request: bool = Field(default=False, description="True ONLY when user explicitly asks to clone/recreate reference")
    target_domain: str = Field(default="CREATIVE_AGENCY", description="Classified primary industry domain")
    functional_checklist: List[Dict[str, Any]] = Field(default_factory=list, description="Verifiable functional features required for domain completeness")
    reference_spec: Optional[Dict[str, Any]] = Field(default=None, description="Extracted reference visual specifications")
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    attempt_number: int = 1
    max_refinement_cycles: int = 3

class AgentResponse(BaseModel):
    """Unified response container returned by all specialised agents."""
    agent_name: str
    status: str  # 'SUCCESS', 'FAILED', 'FALLBACK'
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    execution_time_ms: float = 0.0
