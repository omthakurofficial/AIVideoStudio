#!/usr/bin/env python3
"""Automated pipeline runner for AWS Masterclass (Slides 1-15) based on Cloud X Berry reference style."""
import json, os, sys, time
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from services.api.aivs.config import load_settings
from services.api.aivs.db import connect
from services.api.aivs.store import Store

settings = load_settings()
def get_store():
    return Store(connect(settings.db_path), settings.projects_dir)
from services.api.aivs.workspace import Workspace
from services.api.aivs.storyboard import store as sbstore
from services.api.aivs.storyboard.schema import (
    Storyboard, Scene, VisualElement, Relationship, AnimationStep,
    CameraInstruction, OnScreenText, AssetRequirement, Transition, SceneTiming
)
from services.api.aivs.engines.narration import (
    synthesize_scene_narration, revise_storyboard_with_audio, build_synchronized_captions, validate_captions
)
from services.api.aivs.engines.effectcraft import EffectCraftAdapter
from services.api.aivs.engines.scene_renderer import render_scene
from services.api.aivs.engines.filmcraft import FilmCraftAdapter, TimelineManifest, ClipPlacement, AudioPlacement
from services.api.aivs.qc import inspect_final_video

def main():
    print("=== STARTING AWS MASTERCLASS SLIDES 1-15 GENERATION ===")
    title = "AWS Certified Solutions Architect Associate (SAA-C03) — Foundation"
    
    # 1. Create or load project
    script_path = ROOT / "docs" / "aws_slides_script.md"
    project_settings = {
        "aspect_ratio": "16:9",
        "fps": 30,
        "style": "dark-neon",
        "target_duration_s": 180.0,
        "narration": {
            "mode": "kokoro",
            "voice": "kokoro:am_michael"
        }
    }
    
    if len(sys.argv) > 1 and sys.argv[1]:
        pid = sys.argv[1]
        ws = get_store().workspace(pid)
        print(f"Resuming existing Project: {pid}")
    else:
        p = get_store().create_project(title, "", project_settings)
        pid = p["id"]
        ws = get_store().workspace(pid)
        print(f"Created Project: {pid}")

    # 2. Build 15-Scene Storyboard matching Slides 1-15 & Cloud X Berry Style
    scenes_data = [
        {
            "id": "s01", "order": 1, "title": "Course Hook & Accreditation",
            "narration": "Welcome to the AWS Certified Solutions Architect Associate masterclass. I'm Om Thakur, and throughout this series, we’re bridging theoretical cloud concepts with battle-tested enterprise architecture.",
            "card_title": "SAA-C03 MASTERCLASS", "sub": "AWS Certified Solutions Architect",
            "bullets": ["Lead Trainer: Om Thakur", "Enterprise DevOps & Cloud"],
            "archetype": "tekbay",
            "ost": "AWS CERTIFIED · SAA-C03"
        },
        {
            "id": "s02", "order": 2, "title": "The Cloud Revolution",
            "narration": "Amazon Web Services is the world’s leading cloud platform. Instead of buying physical hardware, you rent on-demand compute and storage that scales instantaneously, powering titans like Netflix and Amazon.com.",
            "card_title": "AMAZON WEB SERVICES", "sub": "Elastic On-Demand Cloud Platform",
            "bullets": ["Powers Netflix & Amazon.com", "Instant Compute & Storage Scaling"],
            "archetype": "ec2",
            "ost": "ON-DEMAND ELASTIC CLOUD"
        },
        {
            "id": "s03", "order": 3, "title": "Why AWS & Economics",
            "narration": "Why has AWS transformed global IT? Because it converts heavy upfront capital expenses into variable operating costs. You only pay for what you consume, with enterprise-grade security out of the box.",
            "card_title": "CLOUD ECONOMICS", "sub": "CapEx to OpEx Transformation",
            "bullets": ["Zero Upfront Server Hardware", "Pay Only for Active Compute"],
            "archetype": "lambda",
            "ost": "PAY-AS-YOU-GO · 65% SAVINGS"
        },
        {
            "id": "s04", "order": 4, "title": "Enterprise Use Cases",
            "narration": "From mission-critical enterprise backups and petabyte-scale data analytics to real-time multiplayer gaming and mobile backends, AWS provides the foundational building blocks for every industry.",
            "card_title": "ENTERPRISE USE CASES", "sub": "Universal Workload Foundations",
            "bullets": ["Big Data Analytics & Storage", "Gaming & Mobile Web Backends"],
            "archetype": "s3",
            "ost": "PETABYTE STORAGE & ANALYTICS"
        },
        {
            "id": "s05", "order": 5, "title": "Global Infrastructure Blueprint",
            "narration": "How does AWS deliver this unmatched reliability? It all rests on four distinct layers of global infrastructure: AWS Regions, Availability Zones, Data Centers, and Edge Locations.",
            "card_title": "GLOBAL INFRASTRUCTURE", "sub": "4-Tier Architectural Hierarchy",
            "bullets": ["Regions & Availability Zones", "Data Centers & Edge PoPs"],
            "archetype": "strata",
            "ost": "4-TIER GLOBAL INFRASTRUCTURE"
        },
        {
            "id": "s06", "order": 6, "title": "Anatomy of an AWS Region",
            "narration": "An AWS Region is a distinct geographical area around the world, completely isolated from other regions. This ensures that a localized disaster in one territory never cascades into another.",
            "card_title": "AWS REGIONS", "sub": "Geographically Isolated Clusters",
            "bullets": ["100% Fault Domain Isolation", "Compliance & Data Residency"],
            "archetype": "route53",
            "ost": "GLOBAL GEOGRAPHIC REGIONS"
        },
        {
            "id": "s07", "order": 7, "title": "Availability Zones (AZs)",
            "narration": "Inside every Region, you'll find multiple Availability Zones. Each AZ consists of one or more physical data centers separated by meaningful distance, yet linked by ultra-fast private fiber optic networks.",
            "card_title": "AVAILABILITY ZONES", "sub": "Multi-Datacenter Resilience",
            "bullets": ["Redundant Power & Grid Feeds", "<1ms Private Fiber Interconnect"],
            "archetype": "rds",
            "ost": "MULTI-AZ FAULT TOLERANCE"
        },
        {
            "id": "s08", "order": 8, "title": "Physical Data Centers",
            "narration": "Beneath each Availability Zone are the physical data centers: fortress-like facilities equipped with custom server racks, biometric security, and redundant backup generators operating 24/7.",
            "card_title": "AWS DATA CENTERS", "sub": "Tier-4 Physical Facilities",
            "bullets": ["Biometric Security & Cages", "Redundant Backup Diesel Power"],
            "archetype": "datacenter",
            "ost": "TIER-4 PHYSICAL SECURITY"
        },
        {
            "id": "s09", "order": 9, "title": "Edge Locations & PoPs",
            "narration": "For lightning-fast performance, AWS deploys hundreds of Edge Locations worldwide. These power Amazon CloudFront, caching static and dynamic content right at your users' doorsteps.",
            "card_title": "EDGE LOCATIONS & POPS", "sub": "Amazon CloudFront Global CDN",
            "bullets": ["Sub-10ms Global Latency", "DDoS Shield & Anycast Routing"],
            "archetype": "cloudfront",
            "ost": "GLOBAL EDGE ACCELERATION"
        },
        {
            "id": "s10", "order": 10, "title": "Hybrid Edge: Outposts & Local Zones",
            "narration": "Need single-digit millisecond latency for manufacturing or finance? AWS Local Zones bring compute directly into major cities, while AWS Outposts lets you roll native AWS hardware straight into your on-premises server room.",
            "card_title": "HYBRID EDGE COMPUTE", "sub": "AWS Outposts & Local Zones",
            "bullets": ["On-Premises 42U Server Racks", "Single-Digit Metro Latency"],
            "archetype": "outpost",
            "ost": "HYBRID ON-PREMISES CLOUD"
        },
        {
            "id": "s11", "order": 11, "title": "The 4-Pillar Region Selection Formula",
            "narration": "When starting any new cloud architecture, choosing the right Region is your first critical decision. You must evaluate four key factors: Compliance, Proximity, Feature Availability, and Cost.",
            "card_title": "REGION SELECTION MATRIX", "sub": "The 4 Critical Architect Pillars",
            "bullets": ["Compliance & Legal Governance", "Latency, Services & Pricing"],
            "archetype": "route53",
            "ost": "THE 4-PILLAR SELECTION FORMULA"
        },
        {
            "id": "s12", "order": 12, "title": "Compliance, Latency & Pricing",
            "narration": "Data sovereignty laws like GDPR dictate where data must reside. Proximity minimizes round-trip latency for customers, while service availability and pricing vary across regions by up to twenty percent.",
            "card_title": "COST & COMPLIANCE", "sub": "GDPR Sovereignty & Tier Pricing",
            "bullets": ["Data Residency Compliance", "Up to 20% Cost Variance"],
            "archetype": "s3",
            "ost": "SOVEREIGNTY & PRICING DYNAMICS"
        },
        {
            "id": "s13", "order": 13, "title": "Architectural Scoping: Global Services",
            "narration": "AWS services fall into two architectural scopes. Global services operate worldwide with a single centralized control plane. Examples include IAM for security identities, Route 53 for DNS, and CloudFront for CDN distribution.",
            "card_title": "GLOBAL SCOPED SERVICES", "sub": "Centralized Worldwide Control Plane",
            "bullets": ["IAM Security, Roles & Policies", "Route 53 DNS & CloudFront CDN"],
            "archetype": "iam",
            "ost": "CENTRALIZED GLOBAL CONTROL"
        },
        {
            "id": "s14", "order": 14, "title": "Architectural Scoping: Regional Services",
            "narration": "In contrast, Regional services are strictly confined to a single Region. Your EC2 virtual instances, RDS databases, and VPC networks reside within that specific geography, providing complete containment and security isolation.",
            "card_title": "REGIONAL SCOPED SERVICES", "sub": "Contained Geographic Enclaves",
            "bullets": ["EC2 Compute & RDS Databases", "VPC Networks & Local S3 Buckets"],
            "archetype": "ec2",
            "ost": "REGIONAL FAULT ENCLAVES"
        },
        {
            "id": "s15", "order": 15, "title": "The 3 Access Gateways",
            "narration": "To manage and deploy these resources, you have three primary gateways: the web-based Management Console for visual administration, the AWS CLI for terminal scripting, and AWS SDKs for programmatic integration in your code.",
            "card_title": "THE 3 ACCESS GATEWAYS", "sub": "Console, CLI & Programmatic SDK",
            "bullets": ["Web GUI, Terminal CLI & Boto3", "Authenticated via IAM & MFA"],
            "archetype": "cli",
            "ost": "CONSOLE · CLI · SDK"
        }
    ]

    sb_scenes = []
    full_script_lines = []
    for s in scenes_data:
        full_script_lines.append(s["narration"])
        sc = Scene(
            id=s["id"],
            order=s["order"],
            estimated_duration=11.5,
            learning_objective=s["title"],
            key_message=s["sub"],
            visual_type="architecture",
            visual_description=f"Motion diagram showcasing {s['card_title']} with official AWS style iconography and kinetic typography.",
            narration_text=s["narration"],
            on_screen_text=[
                OnScreenText(text=s["ost"], at=0.2, duration=10.0, element_id=f"card_{s['id']}")
            ],
            visual_elements=[
                VisualElement(
                    id=f"card_{s['id']}",
                    kind="card",
                    label=s["card_title"],
                    props={
                        "subtitle": s["sub"],
                        "bullets": s["bullets"],
                        "accent": "#FF9900",
                        "archetype": s["archetype"]
                    }
                )
            ],
            animation_sequence=[
                AnimationStep(id=f"anim_{s['id']}", at=0.0, duration=0.8, action="scale", targets=[f"card_{s['id']}"], params={"from": 0.9, "to": 1.0})
            ],
            camera_instructions=[
                CameraInstruction(at=0.0, duration=10.0, move="zoom_in", target=f"card_{s['id']}", amount=1.1)
            ],
            transition=Transition(type="dissolve" if s["order"] > 1 else "cut", duration=0.5 if s["order"] > 1 else 0.0),
            timing=SceneTiming(unit="seconds", scene_relative=True)
        )
        sb_scenes.append(sc)

    # Save script to workspace
    ws.write_script("\n\n".join(full_script_lines))
    print(f"Wrote full 15-scene narration script ({len(full_script_lines)} paragraphs)")

    sb = Storyboard(
        project_id=pid,
        title=title,
        scenes=sb_scenes
    )

    # 3. Synthesize Kokoro Neural Narration for all 15 Scenes
    print("\n--- Synthesizing Kokoro-82M Local Neural Narration ---")
    scene_audios = []
    for sc in sb.scenes:
        print(f"Generating voice for {sc.id} ({sc.learning_objective})...")
        sa = synthesize_scene_narration(
            sc, ws,
            voice="kokoro:am_michael",
            mode="kokoro",
            ffmpeg=settings.ffmpeg,
            ffprobe=settings.ffprobe,
            log=print
        )
        scene_audios.append(sa)
        print(f"  -> {sc.id}: {sa.duration_s:.2f}s ({len(sa.word_timings)} words)")

    audios_dict = {sa.scene_id: sa for sa in scene_audios}

    # 4. Revise Storyboard Timing with exact audio lengths
    sb = revise_storyboard_with_audio(sb, audios_dict)
    captions = build_synchronized_captions(sb, audios_dict)
    tot_dur = sum(s.duration for s in sb.scenes)
    val_report = validate_captions(captions, sb, tot_dur)
    print(f"Generated {len(captions)} synchronized word captions (Total duration: {tot_dur:.2f}s, Validation ok: {val_report.ok})")
    
    ws.write_json("storyboard.json", sb.model_dump())
    sbstore.save(ws.root, sb, bump=False)

    # 5. Render Motion Graphics Scenes with EffectCraft
    print("\n--- Rendering 15 Motion Scenes with SceneRenderer & EffectCraft ---")
    ec_adapter = EffectCraftAdapter(settings.effectcraft_cli, op_timeout=180.0)
    rendered_clips = []
    all_compositions = []
    
    for sc in sb.scenes:
        t0 = time.time()
        print(f"Rendering scene {sc.id} ({sc.duration:.2f}s)...")
        sdir = ws.root / "scenes" / f"{sc.id}_v1"
        sdir.mkdir(parents=True, exist_ok=True)
        sres = render_scene(
            adapter=ec_adapter,
            scene=sc,
            out_dir=sdir,
            width=1920,
            height=1080,
            fps=30.0,
            style="dark-neon",
            ffprobe=settings.ffprobe
        )
        scene_out = sdir / "scene.mp4"
        dt = time.time() - t0
        print(f"  -> Scene {sc.id} rendered in {dt:.1f}s ({sres.mp4.name})")
        rendered_clips.append((sc, scene_out))
        
        # Collect .ecproj composition
        ecproj_path = sdir / "scene.ecproj"
        if ecproj_path.is_file():
            try:
                ec_data = json.loads(ecproj_path.read_text(encoding="utf-8"))
                for comp in ec_data.get("compositions", []):
                    all_compositions.append(comp)
            except Exception as e:
                print(f"  Warning: Could not read ecproj for {sc.id}: {e}")

    # Save unified all_scenes.ecproj
    if all_compositions:
        all_ecproj = {
            "version": 1,
            "project_id": pid,
            "title": title,
            "fps": 30,
            "width": 1920,
            "height": 1080,
            "active_composition": "s01",
            "compositions": all_compositions
        }
        all_ecproj_path = ws.root / "all_scenes.ecproj"
        all_ecproj_path.write_text(json.dumps(all_ecproj, indent=2), encoding="utf-8")
        print(f"Saved unified EffectCraft workspace with {len(all_compositions)} tabs at: {all_ecproj_path}")

    # 6. Timeline Assembly with FilmCraft
    print("\n--- Assembling Multi-Track Timeline with FilmCraft ---")
    fc = FilmCraftAdapter(cli=settings.filmcraft_cli, timeout=300.0)
    fcproj_path = ws.root / "assembly" / "project.fcproj"
    final_mp4 = ws.root / "renders" / "final.mp4"
    
    # Build manifest
    clips = []
    audio_clips = []
    current_time = 0.0
    for sc, clip_mp4 in rendered_clips:
        rel_path = clip_mp4.relative_to(ws.root)
        clips.append(ClipPlacement(
            scene_id=sc.id,
            source_path=str(rel_path),
            track="V1",
            start_s=current_time,
            duration_s=sc.duration,
            source_in_s=0.0,
            include_audio=False,
            transition_in="dissolve" if current_time > 0 else "cut",
            transition_duration_s=0.5 if current_time > 0 else 0.0
        ))
        
        wav_file = ws.root / "narration" / f"{sc.id}.wav"
        if wav_file.is_file():
            audio_clips.append(AudioPlacement(
                id=f"voice_{sc.id}",
                source_path=str(wav_file.relative_to(ws.root)),
                track="A1",
                start_s=current_time,
                duration_s=sc.duration
            ))
            
        current_time += sc.duration

    manifest = TimelineManifest(
        version=1,
        project_id=pid,
        title=title,
        width=1920,
        height=1080,
        fps=30.0,
        sample_rate=48000,
        clips=clips,
        audio_clips=audio_clips,
        captions=captions,
        burn_captions=True,
        caption_font_size=38
    )

    asm_res = fc.assemble(manifest, ws.root, final_mp4, fcproj_path)
    print(f"Assembly completed: {final_mp4} ({asm_res.facts.duration_s:.2f}s, {asm_res.facts.file_size_bytes / (1024*1024):.1f} MB)")

    # 7. Quality Control Verification
    print("\n--- Running Automated Quality Control ---")
    qc_res = inspect_final_video(
        project_id=pid,
        out_mp4=final_mp4,
        fcproj=fcproj_path,
        ws_root=ws.root,
        sb=sb,
        scene_results=[],
        captions=captions,
        repairs=[],
        width=1920,
        height=1080,
        fps=30.0,
        expect_captions=True,
        ffprobe=settings.ffprobe
    )
    import dataclasses
    ws.write_json("reports/quality_report.json", dataclasses.asdict(qc_res))
    print(f"QC Status: {'PASSED' if qc_res.ok else 'WARNINGS'} | Passed checks: {len(qc_res.passed_checks)} | Failed: {len(qc_res.failed_checks)}")

    print("\n=== PIPELINE COMPLETED SUCCESSFULLY ===")
    print(f"Project ID: {pid}")
    print(f"Web Preview URL: http://localhost:3000/projects/{pid}")
    print(f"Final MP4: {final_mp4}")
    print(f"FilmCraft Project: {fcproj_path}")
    print(f"EffectCraft Workspace: {ws.root / 'all_scenes.ecproj'}")

if __name__ == "__main__":
    main()
