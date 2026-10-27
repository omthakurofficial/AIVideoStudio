"""End-to-end persistent production workflow with checkpoints, asset reuse, scene-level retry, and QC repair."""
from __future__ import annotations
import hashlib, json, time
from pathlib import Path
from .config import Settings
from .models import RESOLUTIONS
from .store import Store
from .storyboard import Storyboard, Scene, store as sbstore
from .storyboard.timeline import scene_starts
from .engines.effectcraft import EffectCraftAdapter
from .engines.scene_renderer import render_scene
from .engines.filmcraft import (
    FilmCraftAdapter, TimelineManifest, ClipPlacement, AudioPlacement, CaptionEntry, write_srt
)
from .engines.assets import AssetManager
from .engines.narration import (
    synthesize_scene_narration, revise_storyboard_with_audio, build_synchronized_captions, validate_captions, SceneAudio
)
from .qc import inspect_rendered_scene, repair_scene_for_retry, inspect_final_video, SceneQCResult


def _scene_visual_hash(scene: Scene, width: int, height: int, fps: float, style: str) -> str:
    payload = scene.model_dump(exclude={"status", "quality_checks"})
    raw = json.dumps({"s": payload, "w": width, "h": height, "fps": fps, "style": style}, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _next_scene_version(ws_root: Path, scene_id: str) -> int:
    scenes_dir = ws_root / "scenes"
    scenes_dir.mkdir(parents=True, exist_ok=True)
    vers = [0]
    for d in scenes_dir.glob(f"{scene_id}_v*"):
        tail = d.name.split("_v")[-1]
        if tail.isdigit():
            vers.append(int(tail))
    return max(vers) + 1


class ProductionPipeline:
    def __init__(self, settings: Settings, director_factory=None):
        self.settings = settings
        self.director_factory = director_factory
        self.ec = EffectCraftAdapter(settings.effectcraft_cli)
        self.fc = FilmCraftAdapter(settings.filmcraft_cli, settings.ffmpeg, settings.ffprobe)
        self.assets = AssetManager(settings.data_dir / "asset_cache", settings.ffprobe)

    def run_production(
        self, store: Store, job: dict, is_cancelled=lambda: False,
        only_scene_id: str | None = None, force_scene_ids: set[str] | None = None,
    ) -> None:
        jid, pid = job["id"], job["project_id"]
        ws = store.workspace(pid)
        project = store.get_project(pid)
        if not project:
            raise ValueError(f"Project {pid} not found")
        pset = project["settings"]
        width, height = RESOLUTIONS[pset["aspect_ratio"]]
        fps = float(pset["fps"])
        style = pset.get("visual_style", "clean-technical")
        force_scene_ids = set(force_scene_ids or ())
        if only_scene_id:
            force_scene_ids.add(only_scene_id)

        ckpt: dict = dict(job.get("checkpoint") or {})
        rendered_map: dict[str, dict] = dict(ckpt.get("rendered_scenes") or {})
        repairs: list[dict] = list(ckpt.get("repairs") or [])

        # Load or generate storyboard
        sb = sbstore.load(ws.root)
        if not sb:
            if not self.director_factory:
                raise ValueError("No storyboard exists yet and no AI Director is configured. Plan a storyboard first.")
            script = ws.read_script()
            if not script.strip():
                raise ValueError("Project script is empty.")
            store.update_job(jid, state="planning", current_step="Planning storyboard with AI Director", progress_done=0, progress_total=6)
            director = self.director_factory()
            sb, rep = director.plan(pid, script, pset, log=lambda m: store.log(jid, "info", m))
            if pset.get("approval_mode") == "automatic":
                sb = sb.model_copy(update={"approved": True})
            sb = sbstore.save(ws.root, sb, bump=True)
            ws.write_json("reports/director_usage.json", {**rep.__dict__, "outcome": "ok", "revision": sb.revision})
            if not sb.approved:
                store.update_job(jid, state="awaiting_approval", current_step="Review and approve storyboard before rendering", progress_done=1, progress_total=6, checkpoint=ckpt)
                store.log(jid, "info", "Storyboard planned; awaiting user approval before rendering.")
                return

        n_scenes = len(sb.scenes)
        total_steps = n_scenes + 4  # assets + narration/captions + N scenes + assembly + QC

        # Stage 1: Asset discovery
        if is_cancelled():
            store.update_job(jid, state="cancelled", current_step="Cancelled", checkpoint=ckpt)
            return
        store.update_job(jid, state="generating_assets", current_step="Discovering and validating assets", progress_done=1, progress_total=total_steps, checkpoint=ckpt)
        sb, disc = self.assets.resolve_for_storyboard(sb, ws, log=lambda m: store.log(jid, "info", m))
        sb = sbstore.save(ws.root, sb, bump=False)

        # Stage 2: Narration & Captions (and revise scene timings against actual audio)
        if is_cancelled():
            store.update_job(jid, state="cancelled", current_step="Cancelled", checkpoint=ckpt)
            return
        nar_mode = pset.get("narration", {}).get("mode", "none")
        voice = pset.get("narration", {}).get("voice")
        cap_enabled = bool(pset.get("captions", {}).get("enabled", False))
        scene_audios: dict[str, SceneAudio] = {}

        store.update_job(jid, state="generating_narration", current_step="Generating narration & aligning timing", progress_done=2, progress_total=total_steps, checkpoint=ckpt)
        if nar_mode in ("generate", "user_audio"):
            for sc in sb.scenes:
                sa = synthesize_scene_narration(sc, ws, voice=voice, mode=nar_mode, ffmpeg=self.settings.ffmpeg, ffprobe=self.settings.ffprobe, log=lambda m: store.log(jid, "info", m))
                scene_audios[sc.id] = sa
                store.log(jid, "info", f"Narration {sc.id}: {sa.duration_s:.2f}s ({'reused cache' if sa.reused_cache else sa.provider})")
            sb = revise_storyboard_with_audio(sb, scene_audios)
            sb = sbstore.save(ws.root, sb, bump=False)

        captions: list[CaptionEntry] = []
        if cap_enabled or nar_mode in ("generate", "user_audio"):
            captions = build_synchronized_captions(sb, scene_audios)
            srt_file = write_srt(captions, ws.root / "captions" / "captions.srt")
            ws.add_asset("captions/captions.srt", "captions_srt", {"segments": len(captions)})
            cap_val = validate_captions(captions, sb, sum(s.duration for s in sb.scenes))
            ws.write_json("reports/caption_validation.json", cap_val.__dict__)
            store.log(jid, "info", f"Captions synchronized: {len(captions)} segments (valid={cap_val.ok})")

        ckpt["narration_done"] = True
        store.update_job(jid, checkpoint=ckpt)

        # Stage 3: Render scenes via EffectCraft (with reuse of valid scenes and targeted repair on failure)
        scene_qc_results: list[SceneQCResult] = []
        sb_data = sb.model_dump()

        for idx, sc in enumerate(sb.scenes):
            if is_cancelled():
                store.update_job(jid, state="cancelled", current_step="Cancelled", checkpoint=ckpt)
                return
            step_num = 2 + idx + 1
            vhash = _scene_visual_hash(sc, width, height, fps, style)
            prev_info = rendered_map.get(sc.id)

            # Check if we can reuse an existing verified render for this scene
            if prev_info and sc.id not in force_scene_ids:
                prev_dir = ws.root / prev_info.get("scene_dir", "")
                if prev_info.get("hash") == vhash and (prev_dir / "scene.mp4").is_file() and (prev_dir / "scene.ecproj").is_file():
                    qc_res = inspect_rendered_scene(sc, prev_dir, ws.root, width, height, fps, prev_info.get("version", 1), self.settings.ffmpeg, self.settings.ffprobe)
                    if qc_res.ok:
                        store.log(jid, "info", f"Scene {sc.id}: reused verified render v{qc_res.version} ({qc_res.mp4_path})")
                        scene_qc_results.append(qc_res)
                        sb_data["scenes"][idx]["status"] = "rendered"
                        store.update_job(jid, state="rendering_scenes", current_step=f"Scene {sc.id} reused", progress_done=step_num, progress_total=total_steps, checkpoint=ckpt)
                        continue

            store.update_job(jid, state="rendering_scenes", current_step=f"Rendering scene {sc.id} ({idx + 1}/{n_scenes})", progress_done=step_num - 1, progress_total=total_steps, checkpoint=ckpt)
            ver = _next_scene_version(ws.root, sc.id)
            sdir = ws.root / "scenes" / f"{sc.id}_v{ver}"

            qc_res = self._render_and_inspect_with_repair(
                store, jid, ws, sc, sdir, ver, width, height, fps, style, repairs
            )
            scene_qc_results.append(qc_res)
            if not qc_res.ok:
                sb_data["scenes"][idx]["status"] = "failed"
                sb = sbstore.save(ws.root, Storyboard.model_validate(sb_data), bump=False)
                ckpt["rendered_scenes"] = rendered_map
                ckpt["repairs"] = repairs
                store.update_job(jid, checkpoint=ckpt)
                raise ValueError(f"Scene {sc.id} failed quality control after targeted repair: {'; '.join(qc_res.failed_checks)}")

            # Update storyboard with any repaired scene definition and status="rendered"
            repaired_sc = sbstore.load(ws.root)
            if repaired_sc:
                sb_data["scenes"][idx] = repaired_sc.scenes[idx].model_dump()
            sb_data["scenes"][idx]["status"] = "rendered"
            sb = sbstore.save(ws.root, Storyboard.model_validate(sb_data), bump=False)

            rel_sdir = str(Path(qc_res.mp4_path).parent)
            rendered_map[sc.id] = {
                "scene_dir": rel_sdir,
                "mp4": qc_res.mp4_path,
                "preview": qc_res.preview_png,
                "version": qc_res.version,
                "hash": _scene_visual_hash(sb.scenes[idx], width, height, fps, style),
            }
            ws.add_asset(qc_res.mp4_path, "scene_render", {"scene_id": sc.id, "version": qc_res.version, "engine": "effectcraft"})
            ws.add_asset(f"{rel_sdir}/scene.ecproj", "effectcraft_project", {"scene_id": sc.id, "version": qc_res.version})
            ckpt["rendered_scenes"] = rendered_map
            ckpt["repairs"] = repairs
            store.update_job(jid, state="rendering_scenes", current_step=f"Rendered {sc.id} (v{qc_res.version})", progress_done=step_num, progress_total=total_steps, checkpoint=ckpt)

        # Stage 4: Timeline Assembly via FilmCraft
        if is_cancelled():
            store.update_job(jid, state="cancelled", current_step="Cancelled", checkpoint=ckpt)
            return
        store.update_job(jid, state="assembling", current_step="Assembling timeline in FilmCraft", progress_done=2 + n_scenes + 1, progress_total=total_steps, checkpoint=ckpt)
        starts = scene_starts(sb)
        clips: list[ClipPlacement] = []
        audio_clips: list[AudioPlacement] = []
        for sc in sb.scenes:
            rm = rendered_map[sc.id]
            clips.append(ClipPlacement(
                scene_id=sc.id,
                source_path=rm["mp4"],
                track="V1",
                start_s=starts[sc.id],
                duration_s=sc.duration,
                transition_in=sc.transition.type,
                transition_duration_s=sc.transition.duration,
            ))
            if sc.id in scene_audios:
                sa = scene_audios[sc.id]
                audio_clips.append(AudioPlacement(
                    id=f"nar_{sc.id}",
                    source_path=sa.rel_wav,
                    track="A1",
                    start_s=starts[sc.id],
                    duration_s=sa.duration_s,
                ))

        manifest = TimelineManifest(
            project_id=pid,
            title=project["title"],
            width=width,
            height=height,
            fps=fps,
            clips=clips,
            audio_clips=audio_clips,
            captions=captions,
            burn_captions=cap_enabled and len(captions) > 0,
            caption_font_size=pset.get("captions", {}).get("font_size", 48),
        )
        final_mp4 = ws.root / "renders" / "final.mp4"
        fcproj = ws.root / "assembly" / "project.fcproj"
        asm = self.fc.assemble(manifest, ws.root, final_mp4, fcproj)
        ws.add_asset("renders/final.mp4", "final_video", {"width": width, "height": height, "fps": fps, "duration_s": asm.facts.duration})
        ws.add_asset("assembly/project.fcproj", "filmcraft_project", {"engine": "filmcraft"})
        for w in asm.warnings:
            store.log(jid, "info", f"Assembly note: {w}")

        # Stage 5: Final Quality Control
        store.update_job(jid, state="quality_check", current_step="Running technical & visual quality checks", progress_done=total_steps - 1, progress_total=total_steps, checkpoint=ckpt)
        qrep = inspect_final_video(
            pid, final_mp4, fcproj, ws.root, sb, scene_qc_results, captions, repairs,
            width, height, fps, expect_captions=(cap_enabled and len(captions) > 0), ffprobe=self.settings.ffprobe,
        )
        ws.write_json("reports/quality_report.json", qrep.__dict__)
        if not qrep.ok:
            raise ValueError("Final video failed quality control: " + "; ".join(qrep.failed_checks))

        ckpt["final_mp4"] = "renders/final.mp4"
        ckpt["quality_report"] = "reports/quality_report.json"
        store.conn.execute("UPDATE projects SET status='completed', updated_at=datetime('now') WHERE id=?", (pid,))
        store.update_job(jid, state="completed", current_step="Export ready & verified", progress_done=total_steps, progress_total=total_steps, checkpoint=ckpt)
        store.log(jid, "info", f"Production completed: renders/final.mp4 ({asm.facts.width}x{asm.facts.height} @ {asm.facts.fps:.0f}fps, {asm.facts.duration:.2f}s)")

    def _render_and_inspect_with_repair(
        self, store: Store, jid: str, ws, sc: Scene, sdir: Path, ver: int,
        width: int, height: int, fps: float, style: str, repairs: list[dict],
    ) -> SceneQCResult:
        err_msg = ""
        cat: str | None = None
        try:
            r = render_scene(self.ec, sc, sdir, width, height, fps, style, self.settings.ffprobe)
            for w in r.warnings:
                store.log(jid, "info", f"Scene {sc.id} note: {w}")
            qc = inspect_rendered_scene(sc, sdir, ws.root, width, height, fps, ver, self.settings.ffmpeg, self.settings.ffprobe)
            if qc.ok:
                store.log(jid, "info", f"Scene {sc.id} rendered & passed QC (v{ver}, {qc.duration_s:.2f}s)")
                return qc
            err_msg = "; ".join(qc.failed_checks)
            cat = qc.failure_category
        except Exception as e:
            err_msg = str(e)
            cat = "rendering"

        # Targeted repair & retry
        store.log(jid, "warn", f"Scene {sc.id} v{ver} failed ({cat}: {err_msg}); applying targeted repair.")
        repaired_scene, repair_note = repair_scene_for_retry(sc, cat, err_msg)
        # Persist repaired scene into storyboard
        sb = sbstore.load(ws.root)
        if sb:
            sdata = sb.model_dump()
            for item in sdata["scenes"]:
                if item["id"] == sc.id:
                    item.update(repaired_scene.model_dump())
            sbstore.save(ws.root, Storyboard.model_validate(sdata), bump=False)

        ver2 = ver + 1
        sdir2 = ws.root / "scenes" / f"{sc.id}_v{ver2}"
        render_scene(self.ec, repaired_scene, sdir2, width, height, fps, style, self.settings.ffprobe)
        qc2 = inspect_rendered_scene(repaired_scene, sdir2, ws.root, width, height, fps, ver2, self.settings.ffmpeg, self.settings.ffprobe)
        repairs.append({
            "scene_id": sc.id,
            "failed_version": ver,
            "repaired_version": ver2,
            "category": cat,
            "original_error": err_msg,
            "repair_applied": repair_note,
            "outcome": "passed" if qc2.ok else "failed",
        })
        if qc2.ok:
            store.log(jid, "info", f"Scene {sc.id} repaired ({repair_note}) and passed QC on v{ver2}.")
        return qc2
