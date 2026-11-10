"""Fony Meubles — plans animés à partir de vraies photos produit (0 $, local, sans IA générative).

Chaque photo devient un plan vidéo avec un mouvement de caméra lent et fluide.
Le produit n'est JAMAIS redessiné : c'est la photo d'origine, recadrée et animée.
L'agent monte ensuite ces plans (musique, carton, transitions) avec Remotion/HyperFrames/FFmpeg.

Moteur : tools/video/_fony_motion.py (copié par l'installateur Fony).
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    ResumeSupport,
    RetryPolicy,
    ToolResult,
    ToolStability,
    ToolTier,
)

FORMATS = {"portrait": (1080, 1920), "landscape": (1920, 1080), "square": (1080, 1080)}


class FonyPhotoMotion(BaseTool):
    name = "fony_photo_motion"
    version = "1.0.0"
    tier = ToolTier.CORE
    capability = "video_post"
    provider = "fony"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC

    dependencies = ["cmd:ffmpeg", "python:PIL"]
    install_instructions = "brew install ffmpeg && pip install pillow"
    agent_skills = ["fony-meubles"]

    capabilities = ["photo_to_motion_clip", "product_identity_preserving", "zero_cost"]
    best_for = [
        "Fony Meubles product videos from supplied product photos",
        "any shot where the real product must stay exactly as photographed",
    ]
    not_good_for = ["shots needing a real 3D camera orbit or angles absent from the photos"]

    input_schema = {
        "type": "object",
        "required": ["image_path", "output_path"],
        "properties": {
            "image_path": {"type": "string", "description": "Photo produit fournie par le client (JPG/PNG)."},
            "output_path": {"type": "string", "description": "Chemin du plan .mp4 à écrire."},
            "duration_seconds": {"type": "number", "default": 4.0, "minimum": 2.0, "maximum": 8.0},
            "aspect": {"type": "string", "enum": list(FORMATS), "default": "portrait"},
            "movement": {
                "type": "string",
                "enum": ["avance", "recule", "derive_droite", "derive_gauche"],
                "default": "avance",
                "description": "avance = push-in lent ; recule = pull-out ; derive = léger travelling.",
            },
            "framing": {
                "type": "string",
                "enum": ["auto", "remplir", "galerie"],
                "default": "auto",
                "description": "remplir = plein cadre ; galerie = photo entière sur fond blanc cassé avec ombre douce.",
            },
        },
    }
    output_schema = {"type": "object", "properties": {"output_path": {"type": "string"}, "duration_seconds": {"type": "number"}}}

    resource_profile = ResourceProfile(cpu_cores=2, ram_mb=1500, vram_mb=0, disk_mb=200, network_required=False)
    retry_policy = RetryPolicy(max_retries=1, retryable_errors=["ffmpeg"])
    resume_support = ResumeSupport.FROM_START
    idempotency_key_fields = ["image_path", "duration_seconds", "aspect", "movement", "framing"]
    side_effects = ["writes one silent mp4 clip to output_path"]
    user_visible_verification = [
        "Le meuble est identique à la photo (couleur, forme, pieds, tissu)",
        "Mouvement lent et fluide, sans saccade ni bord vide",
    ]

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        from tools.video._fony_motion import rendre_plan

        src = Path(inputs["image_path"])
        if not src.is_file():
            return ToolResult(success=False, error=f"Photo introuvable : {src}")
        w, h = FORMATS[inputs.get("aspect", "portrait")]
        secondes = float(inputs.get("duration_seconds", 4.0))
        t0 = time.time()
        try:
            out = rendre_plan(src, Path(inputs["output_path"]), w, h, secondes,
                              inputs.get("movement", "avance"), inputs.get("framing", "auto"))
        except Exception as exc:  # noqa: BLE001 — message renvoyé tel quel à l'agent
            return ToolResult(success=False, error=str(exc))
        return ToolResult(
            success=True,
            data={"output_path": str(out), "duration_seconds": secondes, "width": w, "height": h},
            artifacts=[str(out)],
            cost_usd=0.0,
            duration_seconds=time.time() - t0,
            model="fony_motion (local, no generation)",
        )
