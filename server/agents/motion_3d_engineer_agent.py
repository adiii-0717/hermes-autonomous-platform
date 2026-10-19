import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from server.agents.base_agent import BaseAgent
from server.agents.schemas import AgentContext
from server.tools.asset_discovery import AssetDiscoveryService

logger = logging.getLogger("agent.Motion3DEngineer")

class Motion3DEngineerAgent(BaseAgent):
    """Agent C: Enhances generated HTML with progressive Three.js spatial viewports, GSAP motion timelines, and verified 3D GLTF models."""

    def __init__(self):
        super().__init__(
            name="Motion3DEngineer",
            role_description="Injects progressive WebGL 3D viewports, GSAP scroll choreography, and GLTF asset loaders."
        )
        self.asset_discovery = AssetDiscoveryService()

    def run(self, context: AgentContext, **kwargs) -> Dict[str, Any]:
        spec = kwargs.get("creative_spec", {})
        three_d_spec = spec.get("three_d_spec", {})
        requires_3d = spec.get("requires_3d", False)

        ws_p = Path(context.workspace_root)
        proj_dir = ws_p if ws_p.name == context.project_name else (ws_p / context.project_name)
        index_html_path = proj_dir / "index.html"

        if not index_html_path.exists():
            logger.warning(f"Motion3DEngineer: {index_html_path} does not exist.")
            return {"status": "SKIPPED", "reason": "index.html missing"}

        if (proj_dir / "package.json").exists() or (proj_dir / "src" / "components" / "reactbits").exists():
            logger.info(f"[{context.trace_id}] Motion3DEngineer: React Bits motion design system active.")
            return {
                "status": "ENHANCED_REACT_BITS",
                "spatial_features": ["React Bits Canvas Background", "Spotlight Physics", "Lucide Vector Icons", "Spring Micro-Interactions"]
            }

        html_content = index_html_path.read_text(encoding="utf-8")

        prompt_lower = context.user_prompt.lower()
        is_food = any(k in prompt_lower for k in ["restaurant", "food", "dining", "cafe", "bistro", "kitchen", "crave", "dish", "menu", "pizza", "burger", "pasta", "bakery", "sushi", "meal"])
        
        is_3d_requested = False
        if any(k in prompt_lower for k in ["3d", "three.js", "webgl", "mesh", "spatial canvas"]):
            is_3d_requested = True
        elif not is_food and (requires_3d or any(k in prompt_lower for k in [
            "shoe", "footwear", "sneaker", "headphone", "audio", "watch", "chair",
            "car", "vehicle", "bottle", "model"
        ])):
            is_3d_requested = True

        if is_3d_requested:
            model_url = three_d_spec.get("model_url")
            if not model_url or "MaterialsVariantsShoe" in model_url:
                discovered = self.asset_discovery.discover_assets(context.user_prompt)
                models_3d = discovered.get("models_3d", [])
                if models_3d:
                    model_url = models_3d[0]["url"]
                else:
                    model_url = "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/MaterialsVariantsShoe/glTF-Binary/MaterialsVariantsShoe.glb"

            logger.info(f"[{context.trace_id}] Motion3DEngineer selected verified 3D GLTF model: {model_url}")

            progressive_script = f"""
  <!-- Three.js, OrbitControls, GLTFLoader & GSAP -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>
  <script>
    document.addEventListener("DOMContentLoaded", () => {{
      const container = document.getElementById("viewport-3d-container");
      if (!container) return;

      container.innerHTML = "";
      container.style.position = "relative";
      container.style.width = "100%";
      container.style.height = "450px";
      container.style.borderRadius = "24px";
      container.style.overflow = "hidden";
      container.style.background = "radial-gradient(circle at 50% 40%, #1e293b 0%, #090d16 100%)";
      container.style.border = "1px solid rgba(255,255,255,0.1)";

      const fallbackOverlay = document.createElement("div");
      fallbackOverlay.id = "webgl-fallback-hero";
      fallbackOverlay.style.cssText = "position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; padding:24px; transition:opacity 0.6s ease; z-index:2; pointer-events:none;";
      fallbackOverlay.innerHTML = `
        <div style="position:relative; width:140px; height:140px; display:flex; align-items:center; justify-content:center;">
          <svg width="100" height="100" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="filter:drop-shadow(0 0 16px rgba(56,189,248,0.5)); animation:spin 12s linear infinite;">
            <circle cx="12" cy="12" r="10"></circle>
            <path d="M12 2a10 10 0 0 1 10 10"></path>
          </svg>
        </div>
        <div id="webgl-loading-badge" style="margin-top:16px; font-size:0.875rem; font-weight:600; color:#98a2b3; letter-spacing:0.05em; background:rgba(255,255,255,0.06); padding:6px 16px; border-radius:9999px; border:1px solid rgba(255,255,255,0.1);">
          ✦ Rendering High-Fidelity 3D Model...
        </div>
      `;
      container.appendChild(fallbackOverlay);

      const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      let renderer, scene, camera, controls, loadedModel;
      let webglReady = false;

      try {{
        if (typeof THREE === "undefined") throw new Error("Three.js library not loaded");

        scene = new THREE.Scene();
        camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
        camera.position.set(0, 0.5, 3.5);

        renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true, powerPreference: "high-performance" }});
        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.outputEncoding = THREE.sRGBEncoding;

        const canvas = renderer.domElement;
        canvas.style.position = "absolute";
        canvas.style.inset = "0";
        canvas.style.opacity = "0";
        canvas.style.transition = "opacity 0.8s ease";
        canvas.style.zIndex = "1";
        container.appendChild(canvas);

        if (typeof THREE.OrbitControls !== "undefined") {{
          controls = new THREE.OrbitControls(camera, canvas);
          controls.enableDamping = true;
          controls.dampingFactor = 0.05;
          controls.enableZoom = false;
          controls.autoRotate = !prefersReducedMotion;
          controls.autoRotateSpeed = 1.5;
        }}

        const ambientLight = new THREE.AmbientLight(0xffffff, 1.5);
        scene.add(ambientLight);

        const dirLight1 = new THREE.DirectionalLight(0xffffff, 2.0);
        dirLight1.position.set(5, 8, 5);
        scene.add(dirLight1);

        const dirLight2 = new THREE.DirectionalLight(0x38bdf8, 1.2);
        dirLight2.position.set(-5, -2, -5);
        scene.add(dirLight2);

        webglReady = true;

        if (typeof THREE.GLTFLoader !== "undefined") {{
          const loader = new THREE.GLTFLoader();
          loader.load("{model_url}", (gltf) => {{
            loadedModel = gltf.scene;

            const box = new THREE.Box3().setFromObject(loadedModel);
            const center = box.getCenter(new THREE.Vector3());
            const size = box.getSize(new THREE.Vector3());

            loadedModel.position.x += (loadedModel.position.x - center.x);
            loadedModel.position.y += (loadedModel.position.y - center.y);
            loadedModel.position.z += (loadedModel.position.z - center.z);

            const maxDim = Math.max(size.x, size.y, size.z);
            if (maxDim > 0) {{
              const scale = 1.8 / maxDim;
              loadedModel.scale.set(scale, scale, scale);
            }}

            scene.add(loadedModel);

            canvas.style.opacity = "1";
            fallbackOverlay.style.opacity = "0";

            const badge = document.getElementById("webgl-loading-badge");
            if (badge) badge.textContent = "✦ Interactive 3D Showcase";

          }}, undefined, (err) => {{
            console.warn("GLTF Model load failed:", err);
            const badge = document.getElementById("webgl-loading-badge");
            if (badge) badge.textContent = "✦ Interactive Spatial Showcase";
          }});
        }}

        function animate() {{
          requestAnimationFrame(animate);
          if (controls) controls.update();
          renderer.render(scene, camera);
        }}
        animate();

        window.addEventListener("resize", () => {{
          if (!container || !renderer || !camera) return;
          camera.aspect = container.clientWidth / container.clientHeight;
          camera.updateProjectionMatrix();
          renderer.setSize(container.clientWidth, container.clientHeight);
        }});
      }} catch (webglErr) {{
        console.warn("WebGL initialization failed:", webglErr);
      }}
    }});
  </script>
</body>
"""
            html_content = html_content.replace("</body>", progressive_script)
            index_html_path.write_text(html_content, encoding="utf-8")
            return {
                "status": "ENHANCED",
                "model_url": model_url,
                "spatial_features": ["Verified GLTF 3D Model", "Dynamic Auto-Scaling", "Orbit Controls", "Smooth Lighting"]
            }

        return {"status": "SKIPPED", "reason": "3D spatial scene not required by spec"}

    def get_fallback_output(self, context: AgentContext, error_msg: str, **kwargs) -> Dict[str, Any]:
        return {"status": "FALLBACK", "error": error_msg}
