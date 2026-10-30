"""2D Comedy Cartoon Animation Engine (OverSimplified / Animated History Style).

High-retention illustrated canvas animations:
- Living China Map character with stick limbs, bruises, bandages, and crown
- OverSimplified-style expressive cartoon warlords, emperor, and courtiers
- Photographic cutout of Confucius statue
- Synchronized comic speech bubbles
- Illustrated backgrounds (battlefield, Shang palace, Confucius stage, Great Wall, imperial hall)
"""
from __future__ import annotations

import base64
from pathlib import Path

# Load Confucius statue cutout asset
_statue_path = Path(__file__).resolve().parent.parent.parent / "scratch" / "confucius_statue_exact.png"
if not _statue_path.exists():
    _alt_path = Path("/home/omthakur/.gemini/antigravity/brain/7ab7d57d-d84c-4ab6-a5eb-fe9859973ff2/scratch/confucius_statue_exact.png")
    if _alt_path.exists():
        _statue_path = _alt_path

if _statue_path.exists():
    CONFUCIUS_B64 = "data:image/png;base64," + base64.b64encode(_statue_path.read_bytes()).decode("utf-8")
else:
    CONFUCIUS_B64 = ""


def get_cartoon_dom_assets() -> str:
    """Return HTML DOM asset tags for preloaded cartoon textures and cutouts."""
    if CONFUCIUS_B64:
        return f'<img id="confuciusAsset" src="{CONFUCIUS_B64}" style="display:none;" />'
    return ""


def get_cartoon_js_engine() -> str:
    """Return the client-side JavaScript code for the 2D Cartoon Animation Engine."""
    return """
// --------------------------------------------------------------------------
// 2D CARTOON ANIMATION ENGINE (OVERSIMPLIFIED / ANIMATED HISTORY STYLE)
// --------------------------------------------------------------------------

// 1. Comic Speech Bubble
function drawComicSpeechBubble(c, x, y, text, tailDir = 'down-left', scale = 1.0) {
  c.save();
  c.translate(x, y);
  c.scale(scale, scale);

  c.font = '900 24px "Inter", sans-serif';
  const lines = text.split('\\n');
  let maxW = 0;
  for (const l of lines) { maxW = Math.max(maxW, c.measureText(l).width); }
  const padX = 22;
  const padY = 16;
  const lineH = 30;
  const bw = maxW + padX * 2;
  const bh = lines.length * lineH + padY * 2;
  const bx = -bw / 2;
  const by = -bh / 2;

  // Shadow
  c.fillStyle = 'rgba(0, 0, 0, 0.45)';
  c.beginPath();
  c.roundRect(bx + 5, by + 6, bw, bh, 18);
  c.fill();

  // Bubble body
  c.fillStyle = '#ffffff';
  c.strokeStyle = '#18181b';
  c.lineWidth = 4;
  c.beginPath();
  c.roundRect(bx, by, bw, bh, 18);
  c.fill();
  c.stroke();

  // Pointer Tail
  c.fillStyle = '#ffffff';
  c.beginPath();
  if (tailDir === 'down-left') {
    c.moveTo(bx + 35, by + bh - 2);
    c.lineTo(bx + 15, by + bh + 24);
    c.lineTo(bx + 60, by + bh - 2);
  } else if (tailDir === 'down-right') {
    c.moveTo(bx + bw - 60, by + bh - 2);
    c.lineTo(bx + bw - 20, by + bh + 24);
    c.lineTo(bx + bw - 35, by + bh - 2);
  } else if (tailDir === 'left') {
    c.moveTo(bx + 2, by + bh * 0.4);
    c.lineTo(bx - 22, by + bh * 0.6);
    c.lineTo(bx + 2, by + bh * 0.75);
  } else {
    c.moveTo(bx + bw * 0.4, by + bh - 2);
    c.lineTo(bx + bw * 0.5, by + bh + 24);
    c.lineTo(bx + bw * 0.6, by + bh - 2);
  }
  c.fill();
  c.stroke();

  // Cover seam
  c.fillStyle = '#ffffff';
  if (tailDir.startsWith('down')) {
    c.fillRect(bx + (tailDir.includes('right') ? bw - 58 : 34), by + bh - 4, 25, 6);
  }

  // Text
  c.fillStyle = '#111116';
  c.textAlign = 'center';
  c.textBaseline = 'middle';
  lines.forEach((ln, idx) => {
    const yPos = by + padY + (idx + 0.5) * lineH;
    c.fillText(ln, 0, yPos);
  });
  c.restore();
}

// 2. Draw China Map Silhouette
function drawChinaMapShape(c, scale = 1.0) {
  c.save();
  c.scale(scale, scale);
  c.beginPath();
  // Normalized China Map Points (Heilongjiang Northeast -> East Coast -> South -> Tibet -> Xinjiang -> North)
  const pts = [
    [140, -130], [180, -110], [195, -70], [160, -30],
    [120, -10], [110, 15], [140, 30], [120, 60],
    [150, 90], [130, 140], [100, 170], [50, 185], [-10, 180],
    [-60, 175], [-110, 150], [-140, 110], [-190, 80], [-230, 30], [-240, -20],
    [-220, -70], [-180, -120], [-140, -110], [-90, -70], [-40, -80], [10, -95], [60, -120], [100, -135]
  ];
  c.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i < pts.length; i++) {
    c.lineTo(pts[i][0], pts[i][1]);
  }
  c.closePath();
  c.fillStyle = '#dc2626';
  c.fill();
  c.strokeStyle = '#18181b';
  c.lineWidth = 5 / scale;
  c.stroke();

  // Large Yellow Star
  c.fillStyle = '#facc15';
  c.font = `bold ${Math.round(44 * scale)}px sans-serif`;
  c.textAlign = 'center';
  c.textBaseline = 'middle';
  c.fillText('★', -50, -40);

  // 4 Small Yellow Stars in arch
  c.font = `bold ${Math.round(18 * scale)}px sans-serif`;
  c.fillText('★', -15, -60);
  c.fillText('★', 0, -42);
  c.fillText('★', 2, -20);
  c.fillText('★', -10, -2);

  c.restore();
}

// 3. 2D Cartoon Character Head & Face (OverSimplified Signature Style)
function drawCartoonFace(c, x, y, options = {}) {
  c.save();
  c.translate(x, y);
  const headR = options.r || 38;
  const skin = options.skin || '#f6be95';
  const isMouthOpen = options.mouthOpen || false;
  const grin = options.grin || false;
  const isBlink = options.blink || false;
  const eyes = options.eyes || 'normal';

  // Head
  c.fillStyle = skin;
  c.strokeStyle = '#18181b';
  c.lineWidth = 4;
  c.beginPath();
  c.arc(0, 0, headR, 0, Math.PI * 2);
  c.fill();
  c.stroke();

  // Topknot or Hair
  if (options.topknot) {
    c.fillStyle = '#1e1b18';
    c.beginPath();
    c.arc(0, -headR - 8, 14, 0, Math.PI * 2);
    c.fill();
    c.stroke();
    c.fillStyle = '#ef4444';
    c.fillRect(-8, -headR - 2, 16, 5);
  }

  // Eyes
  if (isBlink) {
    c.strokeStyle = '#18181b';
    c.lineWidth = 3;
    c.beginPath(); c.moveTo(-18, -6); c.lineTo(-4, -6); c.stroke();
    c.beginPath(); c.moveTo(4, -6); c.lineTo(18, -6); c.stroke();
  } else if (eyes === 'dizzy') {
    c.strokeStyle = '#18181b';
    c.lineWidth = 3.5;
    c.beginPath(); c.moveTo(-18, -12); c.lineTo(-6, 0); c.moveTo(-6, -12); c.lineTo(-18, 0); c.stroke();
    c.beginPath(); c.moveTo(6, -12); c.lineTo(18, 0); c.moveTo(18, -12); c.lineTo(6, 0); c.stroke();
  } else if (eyes === 'sly') {
    c.fillStyle = '#18181b';
    c.beginPath();
    c.ellipse(-14, -8, 8, 4, -0.2, 0, Math.PI * 2);
    c.ellipse(14, -8, 8, 4, 0.2, 0, Math.PI * 2);
    c.fill();
  } else if (eyes === 'wide') {
    c.fillStyle = '#ffffff';
    c.strokeStyle = '#18181b';
    c.lineWidth = 2.5;
    c.beginPath(); c.arc(-14, -8, 10, 0, Math.PI * 2); c.fill(); c.stroke();
    c.beginPath(); c.arc(14, -8, 10, 0, Math.PI * 2); c.fill(); c.stroke();
    c.fillStyle = '#18181b';
    c.beginPath(); c.arc(-14, -8, 4, 0, Math.PI * 2); c.fill();
    c.beginPath(); c.arc(14, -8, 4, 0, Math.PI * 2); c.fill();
  } else {
    c.fillStyle = '#18181b';
    c.beginPath(); c.arc(-12, -7, 4.5, 0, Math.PI * 2); c.fill();
    c.beginPath(); c.arc(12, -7, 4.5, 0, Math.PI * 2); c.fill();
  }

  // Eyebrows
  c.strokeStyle = '#18181b';
  c.lineWidth = 3;
  if (options.angryBrows) {
    c.beginPath(); c.moveTo(-22, -18); c.lineTo(-6, -13); c.stroke();
    c.beginPath(); c.moveTo(22, -18); c.lineTo(6, -13); c.stroke();
  } else if (options.sadBrows) {
    c.beginPath(); c.moveTo(-22, -13); c.lineTo(-6, -18); c.stroke();
    c.beginPath(); c.moveTo(22, -13); c.lineTo(6, -18); c.stroke();
  }

  // Mouth
  if (grin) {
    c.fillStyle = '#ffffff';
    c.strokeStyle = '#18181b';
    c.lineWidth = 3;
    c.beginPath();
    c.roundRect(-22, 6, 44, 18, 6);
    c.fill();
    c.stroke();
    for (let tx = -14; tx <= 14; tx += 7) {
      c.beginPath(); c.moveTo(tx, 6); c.lineTo(tx, 24); c.stroke();
    }
  } else if (isMouthOpen) {
    c.fillStyle = '#831843';
    c.strokeStyle = '#18181b';
    c.lineWidth = 3;
    c.beginPath();
    c.ellipse(0, 12, 10, 8, 0, 0, Math.PI * 2);
    c.fill();
    c.stroke();
    c.fillStyle = '#f43f5e';
    c.beginPath();
    c.arc(0, 16, 6, Math.PI, Math.PI * 2);
    c.fill();
  } else if (options.groan) {
    c.strokeStyle = '#18181b';
    c.lineWidth = 3;
    c.beginPath();
    c.moveTo(-14, 14);
    c.quadraticCurveTo(-7, 8, 0, 14);
    c.quadraticCurveTo(7, 20, 14, 14);
    c.stroke();
  } else {
    c.strokeStyle = '#18181b';
    c.lineWidth = 3;
    c.beginPath();
    c.arc(0, 5, 12, 0.2, Math.PI - 0.2);
    c.stroke();
  }

  c.restore();
}

// --------------------------------------------------------------------------
// MAIN 2D CARTOON SCENE DISPATCHER
// --------------------------------------------------------------------------
function draw2DCartoonHistoryScene(c, t, curScene) {
  const sceneT = t - curScene.start_s;
  const sceneNum = curScene.scene_number || 1;
  const isTalk = Math.abs(Math.sin(t * 12)) > 0.35;
  const isBlink = (Math.floor(t * 2.5) % 8) === 0;

  // Punch Zoom on Scene Start
  const punchZoom = 1.0 + (sceneT < 0.3 ? 0.06 * (1 - sceneT / 0.3) : 0);
  c.save();
  c.translate(W / 2, H / 2);
  c.scale(punchZoom, punchZoom);
  c.translate(-W / 2, -H / 2);

  if (sceneNum === 1) {
    // =======================================================================
    // SCENE 1: BATTERED CHINA MAP SURROUNDED BY WARLORDS (Screenshot 1 Match)
    // =======================================================================
    const skyG = c.createLinearGradient(0, 0, 0, H * 0.72);
    skyG.addColorStop(0, '#c77f74');
    skyG.addColorStop(0.65, '#de9f88');
    skyG.addColorStop(1, '#e8b89e');
    c.fillStyle = skyG;
    c.fillRect(0, 0, W, H);

    // Cartoon Clouds
    c.fillStyle = '#f6eae4';
    c.strokeStyle = '#2d2426';
    c.lineWidth = 3.5;
    for (let i = 0; i < 3; i++) {
      const cxPos = (i * 380 + t * 12) % (W + 200) - 100;
      const cyPos = 160 + i * 90;
      c.beginPath();
      c.arc(cxPos, cyPos, 45, 0, Math.PI * 2);
      c.arc(cxPos + 40, cyPos - 15, 55, 0, Math.PI * 2);
      c.arc(cxPos + 85, cyPos, 40, 0, Math.PI * 2);
      c.fill(); c.stroke();
    }

    // Fortress Towers & Battlements
    const fortY = H * 0.58;
    c.fillStyle = '#655750';
    c.strokeStyle = '#29211e';
    c.lineWidth = 4;
    c.beginPath();
    c.rect(0, fortY, W, 90);
    c.fill(); c.stroke();
    for (let fx = 20; fx < W; fx += 80) {
      c.fillRect(fx, fortY - 24, 45, 24);
      c.strokeRect(fx, fortY - 24, 45, 24);
    }
    [100, W - 140].forEach(tx => {
      c.fillRect(tx, fortY - 90, 80, 90);
      c.strokeRect(tx, fortY - 90, 80, 90);
      c.strokeStyle = '#3e2723';
      c.lineWidth = 6;
      c.beginPath(); c.moveTo(tx + 40, fortY - 90); c.lineTo(tx + 40, fortY - 180); c.stroke();
      const wave = Math.sin(t * 6) * 12;
      c.fillStyle = '#166534';
      c.strokeStyle = '#14532d';
      c.lineWidth = 3;
      c.beginPath();
      c.moveTo(tx + 40, fortY - 180);
      c.quadraticCurveTo(tx + 95, fortY - 170 + wave, tx + 140, fortY - 160);
      c.lineTo(tx + 140, fortY - 120);
      c.quadraticCurveTo(tx + 95, fortY - 130 + wave, tx + 40, fortY - 140);
      c.closePath();
      c.fill(); c.stroke();
    });

    // Earth Ground
    const groundY = H * 0.63;
    c.fillStyle = '#8f6f54';
    c.strokeStyle = '#261c16';
    c.lineWidth = 4;
    c.beginPath();
    c.rect(0, groundY, W, H - groundY);
    c.fill(); c.stroke();

    // Battered China Map Character
    c.save();
    const mapX = W * 0.48;
    const mapY = groundY + 130;
    c.translate(mapX, mapY);
    c.rotate(-0.05);

    // Stick Limbs
    c.strokeStyle = '#18181b';
    c.lineWidth = 7;
    c.lineCap = 'round';
    const legTwitch = Math.sin(t * 14) * 3;
    c.beginPath(); c.moveTo(-160, 40); c.lineTo(-240, 70 + legTwitch); c.lineTo(-280, 60); c.stroke();
    c.beginPath(); c.moveTo(-60, 90); c.lineTo(-100, 150); c.lineTo(-80, 175); c.stroke();
    c.beginPath(); c.moveTo(120, 60); c.lineTo(190, 110); c.lineTo(220, 90); c.stroke();
    c.beginPath(); c.moveTo(-120, -60); c.lineTo(-210, -80); c.lineTo(-240, -50); c.stroke();

    drawChinaMapShape(c, 0.95);

    // Dizzy X X Eyes
    c.strokeStyle = '#18181b';
    c.lineWidth = 5;
    c.beginPath(); c.moveTo(-75, 10); c.lineTo(-55, 30); c.moveTo(-55, 10); c.lineTo(-75, 30); c.stroke();
    c.beginPath(); c.moveTo(-25, 15); c.lineTo(-5, 35); c.moveTo(-5, 15); c.lineTo(-25, 35); c.stroke();

    // Groaning Wavy Mouth
    c.beginPath();
    c.moveTo(-60, 50);
    c.quadraticCurveTo(-45, 42, -35, 52);
    c.quadraticCurveTo(-25, 62, -15, 50);
    c.stroke();

    // Medical Bandage with Cross
    c.fillStyle = '#ffffff';
    c.strokeStyle = '#18181b';
    c.lineWidth = 3;
    c.beginPath();
    c.roundRect(-80, -25, 55, 26, 6);
    c.fill(); c.stroke();
    c.fillStyle = '#ef4444';
    c.fillRect(-60, -21, 15, 18);
    c.fillRect(-70, -15, 35, 6);

    // Flying Sweat Drops
    c.fillStyle = '#38bdf8';
    c.beginPath(); c.arc(-95, -10, 7, 0, Math.PI * 2); c.fill();
    c.beginPath(); c.arc(-110, 10, 5, 0, Math.PI * 2); c.fill();
    c.restore();

    // Warlord 1: Left Soldier with Bamboo Spear
    c.save();
    c.translate(W * 0.16, groundY - 30);
    c.fillStyle = '#b91c1c';
    c.strokeStyle = '#18181b';
    c.lineWidth = 4;
    c.beginPath(); c.roundRect(-30, 0, 60, 85, [10, 10, 0, 0]); c.fill(); c.stroke();
    c.fillStyle = '#78350f';
    c.fillRect(-22, 18, 44, 45);
    c.strokeStyle = '#b45309';
    c.lineWidth = 6;
    c.beginPath(); c.moveTo(-10, 90); c.lineTo(130, -50); c.stroke();
    c.fillStyle = '#94a3b8';
    c.beginPath(); c.moveTo(130, -50); c.lineTo(155, -68); c.lineTo(142, -40); c.closePath(); c.fill(); c.stroke();
    c.fillStyle = '#dc2626';
    c.beginPath(); c.arc(132, -48, 9, 0, Math.PI * 2); c.fill();
    drawCartoonFace(c, 0, -35, { r: 35, topknot: true, grin: true, eyes: 'sly', angryBrows: true });
    c.restore();

    // Warlord 2: Center Queen/Empress with Sword & Yellow Robe
    c.save();
    c.translate(W * 0.38, groundY - 140);
    c.fillStyle = '#eab308';
    c.strokeStyle = '#18181b';
    c.lineWidth = 4;
    c.beginPath();
    c.moveTo(-35, 10); c.lineTo(35, 10); c.lineTo(55, 120); c.lineTo(-55, 120);
    c.closePath(); c.fill(); c.stroke();
    c.strokeStyle = '#cbd5e1'; c.lineWidth = 5;
    c.beginPath(); c.moveTo(35, 50); c.lineTo(85, 110); c.stroke();
    drawCartoonFace(c, 0, -25, { r: 32, skin: '#ffedd5', grin: true, eyes: 'sly' });
    c.fillStyle = '#f59e0b';
    c.fillRect(-20, -58, 40, 6);
    c.restore();

    // Warlord 3: Right Nomad on ORANGE CARTOON HORSE
    c.save();
    const horseBob = Math.sin(t * 5) * 4;
    c.translate(W * 0.72, groundY - 50 + horseBob);
    c.fillStyle = '#ea580c';
    c.strokeStyle = '#18181b';
    c.lineWidth = 4;
    c.beginPath(); c.ellipse(0, 40, 65, 45, 0, 0, Math.PI * 2); c.fill(); c.stroke();
    c.beginPath(); c.roundRect(-60, -10, 40, 50, 10); c.fill(); c.stroke();
    c.beginPath(); c.ellipse(-70, -25, 25, 18, -0.4, 0, Math.PI * 2); c.fill(); c.stroke();
    c.fillStyle = '#ffffff';
    c.beginPath(); c.arc(-72, -30, 8, 0, Math.PI * 2); c.fill(); c.stroke();
    c.fillStyle = '#18181b';
    c.beginPath(); c.arc(-72, -30, 3, 0, Math.PI * 2); c.fill();
    c.strokeStyle = '#18181b'; c.lineWidth = 5;
    c.beginPath();
    c.moveTo(-35, 80); c.lineTo(-40, 140);
    c.moveTo(-15, 80); c.lineTo(-12, 140);
    c.moveTo(25, 80); c.lineTo(25, 140);
    c.moveTo(45, 80); c.lineTo(50, 140);
    c.stroke();
    c.fillStyle = '#78350f';
    c.beginPath(); c.roundRect(-22, -15, 44, 55, [8, 8, 0, 0]); c.fill(); c.stroke();
    c.strokeStyle = '#e2e8f0'; c.lineWidth = 5;
    c.beginPath(); c.moveTo(20, -5); c.quadraticCurveTo(65, -45, 75, -80); c.stroke();
    drawCartoonFace(c, 0, -50, { r: 30, skin: '#fed7aa', grin: true, eyes: 'sly', angryBrows: true });
    c.fillStyle = '#451a03';
    c.beginPath(); c.arc(0, -68, 28, Math.PI, Math.PI * 2); c.fill(); c.stroke();
    c.restore();

    // Warlord 4: Giant Broadsword General on Far Right
    c.save();
    c.translate(W * 0.88, groundY - 20);
    c.fillStyle = '#2563eb';
    c.strokeStyle = '#18181b';
    c.lineWidth = 4;
    c.beginPath(); c.roundRect(-35, 10, 70, 95, [10, 10, 0, 0]); c.fill(); c.stroke();
    c.fillStyle = '#dc2626';
    c.fillRect(-15, 10, 30, 95);
    c.fillStyle = '#cbd5e1';
    c.strokeStyle = '#18181b'; c.lineWidth = 4;
    c.beginPath();
    c.moveTo(-45, 20); c.lineTo(-80, -90); c.lineTo(-50, -90); c.lineTo(-25, 20);
    c.closePath(); c.fill(); c.stroke();
    drawCartoonFace(c, 0, -25, { r: 34, skin: '#fed7aa', grin: true, eyes: 'sly' });
    c.fillStyle = '#1d4ed8';
    c.fillRect(-28, -62, 56, 16);
    c.restore();

    // Comic Speech Bubble from China
    const popScale = ezBack(Math.min(1.0, sceneT / 0.45));
    drawComicSpeechBubble(c, W * 0.52, groundY - 45, "I'M NOT DEAD YET!\\n(Just taking a dynastic nap...)", 'down-left', popScale);

    // Top Title Banner
    c.save();
    c.translate(W / 2, IS_VERT ? 320 : 65);
    c.fillStyle = 'rgba(15, 10, 12, 0.9)';
    c.strokeStyle = '#facc15'; c.lineWidth = 3;
    c.beginPath(); c.roundRect(-380, -42, 760, 84, 14); c.fill(); c.stroke();
    c.font = '900 36px "Anton", sans-serif';
    c.fillStyle = '#ffffff'; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillText('CHINA DIED MORE THAN ANY COUNTRY', 0, 0);
    c.restore();

  } else if (sceneNum === 2) {
    // =======================================================================
    // SCENE 2: ANCIENT SHANG PALACE & DIVINATION BONE (Screenshot 2 Match)
    // =======================================================================
    c.fillStyle = '#ab805b';
    c.fillRect(0, 0, W, H);
    c.strokeStyle = '#7c5436';
    c.lineWidth = 5;
    for (let y = 0; y < H * 0.65; y += 75) {
      c.beginPath(); c.moveTo(0, y); c.lineTo(W, y); c.stroke();
    }
    [120, W * 0.48].forEach(px => {
      c.fillStyle = '#654328';
      c.strokeStyle = '#382212';
      c.lineWidth = 5;
      c.beginPath(); c.rect(px - 32, 0, 64, H); c.fill(); c.stroke();
    });

    // Open Stone Window on Right
    const winX = W * 0.72;
    const winY = IS_VERT ? 380 : 100;
    c.fillStyle = '#d4be9e';
    c.fillRect(winX, winY, 240, 320);
    c.fillStyle = '#9e8062';
    c.beginPath();
    c.moveTo(winX, winY + 220);
    c.quadraticCurveTo(winX + 120, winY + 160, winX + 240, winY + 200);
    c.lineTo(winX + 240, winY + 320); c.lineTo(winX, winY + 320);
    c.fill();
    c.strokeStyle = '#4a3321'; c.lineWidth = 8;
    c.strokeRect(winX, winY, 240, 320);

    // Floor
    const floorY = H * 0.64;
    c.fillStyle = '#5c4028';
    c.fillRect(0, floorY, W, H - floorY);
    c.strokeStyle = '#2d1c0f'; c.lineWidth = 5;
    c.beginPath(); c.moveTo(0, floorY); c.lineTo(W, floorY); c.stroke();

    // Shang King on Throne
    c.save();
    const kingX = W * 0.38;
    const kingY = floorY - 30;
    c.translate(kingX, kingY);
    c.fillStyle = '#4a2e18';
    c.strokeStyle = '#1e1108'; c.lineWidth = 5;
    c.beginPath();
    c.rect(-65, -120, 130, 150);
    c.rect(-75, 10, 150, 20);
    c.fill(); c.stroke();
    c.fillStyle = '#dc2626';
    c.strokeStyle = '#18181b'; c.lineWidth = 4;
    c.beginPath();
    c.roundRect(-48, -40, 96, 120, [14, 14, 0, 0]);
    c.fill(); c.stroke();
    c.fillStyle = '#2563eb';
    c.beginPath();
    c.moveTo(-35, -40); c.lineTo(0, 10); c.lineTo(35, -40);
    c.closePath(); c.fill();
    c.fillStyle = '#14b8a6';
    c.beginPath(); c.arc(0, 25, 9, 0, Math.PI * 2); c.fill();
    drawCartoonFace(c, 0, -85, { r: 36, skin: '#fed7aa', mouthOpen: isTalk, eyes: 'normal' });
    c.strokeStyle = '#18181b'; c.lineWidth = 3.5;
    c.beginPath();
    c.moveTo(-18, -75); c.quadraticCurveTo(-10, -68, 0, -74);
    c.quadraticCurveTo(10, -68, 18, -75); c.stroke();
    c.fillStyle = '#2563eb';
    c.strokeStyle = '#1e3a8a'; c.lineWidth = 3;
    c.beginPath();
    c.roundRect(-24, -135, 48, 26, 6); c.fill(); c.stroke();
    for (let rx = -16; rx <= 16; rx += 8) {
      c.beginPath(); c.moveTo(rx, -135); c.lineTo(rx, -109); c.stroke();
    }
    c.restore();

    // Left Scholar with Bamboo Scroll
    c.save();
    c.translate(W * 0.16, floorY - 20);
    c.fillStyle = '#94a3b8';
    c.strokeStyle = '#18181b'; c.lineWidth = 4;
    c.beginPath(); c.roundRect(-30, -30, 60, 110, [10, 10, 0, 0]); c.fill(); c.stroke();
    c.fillStyle = '#deb887';
    c.strokeStyle = '#78350f'; c.lineWidth = 3;
    c.beginPath(); c.roundRect(10, -10, 48, 70, 4); c.fill(); c.stroke();
    c.fillStyle = '#18181b';
    c.font = '8px monospace';
    c.fillText('甲骨文', 16, 12);
    c.fillText('卜筮鬼', 16, 32);
    c.fillText('王大吉', 16, 52);
    drawCartoonFace(c, 0, -70, { r: 32, skin: '#fed7aa', grin: false });
    c.fillStyle = '#3b82f6';
    c.fillRect(-22, -108, 44, 14);
    c.restore();

    // Right Diviner Raising Oracle Bone
    c.save();
    const divX = W * 0.68;
    const divY = floorY - 20;
    c.translate(divX, divY);
    c.fillStyle = '#78350f';
    c.strokeStyle = '#18181b'; c.lineWidth = 4;
    c.beginPath(); c.roundRect(-32, -30, 64, 110, [10, 10, 0, 0]); c.fill(); c.stroke();
    c.fillStyle = '#eab308'; c.fillRect(-32, 15, 64, 12);
    c.strokeStyle = '#78350f'; c.lineWidth = 9; c.lineCap = 'round';
    c.beginPath(); c.moveTo(-25, -20); c.lineTo(-45, -75); c.stroke();
    c.beginPath(); c.moveTo(25, -20); c.lineTo(45, -75); c.stroke();
    c.fillStyle = '#fef3c7';
    c.strokeStyle = '#78350f'; c.lineWidth = 3;
    c.beginPath();
    c.roundRect(-45, -135, 90, 65, 8); c.fill(); c.stroke();
    c.strokeStyle = '#ef4444'; c.lineWidth = 3;
    c.beginPath();
    c.moveTo(-20, -125); c.lineTo(-5, -105); c.lineTo(15, -112); c.lineTo(25, -90);
    c.stroke();
    c.fillStyle = '#f59e0b';
    c.font = 'bold 18px sans-serif';
    c.fillText('雨', -30 + Math.sin(t * 3) * 5, -145);
    c.fillText('王', 15 + Math.cos(t * 3) * 5, -150);
    drawCartoonFace(c, 0, -68, { r: 30, skin: '#fed7aa', topknot: true, mouthOpen: isTalk });
    c.fillStyle = '#18181b';
    c.beginPath(); c.moveTo(-6, -42); c.lineTo(6, -42); c.lineTo(0, -30); c.closePath(); c.fill();
    c.restore();

    // Bronze Ding Cauldron
    c.save();
    c.translate(W * 0.68, floorY + 45);
    c.fillStyle = '#1e3a2e';
    c.strokeStyle = '#0f172a'; c.lineWidth = 4;
    c.beginPath(); c.ellipse(0, 0, 50, 25, 0, 0, Math.PI * 2); c.fill(); c.stroke();
    c.lineWidth = 6;
    c.beginPath();
    c.moveTo(-35, 10); c.lineTo(-42, 45);
    c.moveTo(0, 15); c.lineTo(0, 50);
    c.moveTo(35, 10); c.lineTo(42, 45);
    c.stroke();
    c.fillStyle = '#ef4444';
    c.beginPath(); c.arc(0, -5, 18, 0, Math.PI * 2); c.fill();
    c.fillStyle = '#f59e0b';
    for (let i = 0; i < 4; i++) {
      const sy = -20 - (t * 40 + i * 25) % 60;
      const sx = Math.sin(t * 5 + i) * 15;
      c.beginPath(); c.arc(sx, sy, 3, 0, Math.PI * 2); c.fill();
    }
    c.restore();

    // Speech Bubble
    const popScale2 = ezBack(Math.min(1.0, sceneT / 0.45));
    drawComicSpeechBubble(c, W * 0.68, floorY - 210, "Should we attack? Ask grandma!\\n(Oracle Bone: Fire says YES 🔥)", 'down-left', popScale2);

    // Title Banner
    c.save();
    c.translate(W / 2, IS_VERT ? 320 : 65);
    c.fillStyle = 'rgba(15, 10, 12, 0.9)';
    c.strokeStyle = '#facc15'; c.lineWidth = 3;
    c.beginPath(); c.roundRect(-380, -42, 760, 84, 14); c.fill(); c.stroke();
    c.font = '900 36px "Anton", sans-serif';
    c.fillStyle = '#ffffff'; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillText('ORACLE BONES & GHOST CHARACTERS', 0, 0);
    c.restore();

  } else if (sceneNum === 3) {
    // =======================================================================
    // SCENE 3: CONFUCIUS STATUE & THE MANDATE OF HEAVEN (Screenshot 3 Match)
    // =======================================================================
    c.fillStyle = '#ece8e1';
    c.fillRect(0, 0, W, H);
    c.strokeStyle = 'rgba(0,0,0,0.12)';
    c.lineWidth = 3;
    c.strokeRect(30, 30, W - 60, H - 60);

    // Photographic Confucius Statue
    const confX = IS_VERT ? W * 0.45 : W * 0.52;
    const confY = IS_VERT ? H * 0.38 : H * 0.22;
    const confW = IS_VERT ? 520 : 420;
    const confH = IS_VERT ? 640 : 520;

    c.save();
    c.fillStyle = 'rgba(234, 179, 8, 0.12)';
    c.strokeStyle = '#d97706'; c.lineWidth = 4;
    c.beginPath();
    c.roundRect(confX - 15, confY - 15, confW + 30, confH + 75, 18);
    c.fill(); c.stroke();

    const confImg = document.getElementById('confuciusAsset');
    if (confImg && confImg.complete && confImg.naturalWidth > 0) {
      c.drawImage(confImg, confX, confY, confW, confH);
    } else {
      c.fillStyle = '#64748b';
      c.fillRect(confX, confY, confW, confH);
    }

    c.fillStyle = '#1e293b';
    c.beginPath();
    c.roundRect(confX, confY + confH + 8, confW, 44, 8);
    c.fill();
    c.font = '800 20px "Inter", sans-serif';
    c.fillStyle = '#facc15';
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    c.fillText('KONG FUZI (CONFUCIUS) · 551–479 BC', confX + confW / 2, confY + confH + 30);
    c.restore();

    // Stick Figure Narrator
    c.save();
    const stickX = IS_VERT ? W * 0.24 : W * 0.22;
    const stickY = IS_VERT ? H * 0.65 : H * 0.58;
    c.translate(stickX, stickY);

    c.strokeStyle = '#18181b'; c.lineWidth = 6; c.lineCap = 'round';
    c.beginPath(); c.moveTo(0, 0); c.lineTo(0, 110); c.stroke();
    c.beginPath(); c.moveTo(0, 110); c.lineTo(-30, 200); c.stroke();
    c.beginPath(); c.moveTo(0, 110); c.lineTo(30, 200); c.stroke();

    c.fillStyle = '#d97706';
    c.strokeStyle = '#18181b'; c.lineWidth = 3;
    c.beginPath();
    c.moveTo(-25, 20); c.lineTo(25, 45); c.lineTo(15, 95); c.lineTo(-25, 80);
    c.closePath(); c.fill(); c.stroke();
    c.fillStyle = '#78350f';
    c.beginPath(); c.arc(-10, 40, 4, 0, Math.PI * 2); c.fill();
    c.beginPath(); c.arc(5, 65, 4, 0, Math.PI * 2); c.fill();

    c.beginPath(); c.moveTo(0, 30); c.lineTo(-55, 60); c.lineTo(-55, -20); c.stroke();
    c.strokeStyle = '#78350f'; c.lineWidth = 6;
    c.beginPath(); c.moveTo(-55, 180); c.lineTo(-55, -120); c.stroke();
    c.fillStyle = '#94a3b8';
    c.beginPath(); c.moveTo(-55, -120); c.lineTo(-65, -100); c.lineTo(-45, -100); c.closePath(); c.fill();

    c.strokeStyle = '#18181b'; c.lineWidth = 6;
    const handWave = Math.sin(t * 8) * 10;
    c.beginPath(); c.moveTo(0, 30); c.lineTo(45, 15 + handWave); c.lineTo(85, -20 + handWave); c.stroke();

    drawCartoonFace(c, 0, -42, { r: 38, skin: '#fed7aa', mouthOpen: isTalk, eyes: 'normal' });
    c.fillStyle = '#854d0e';
    c.beginPath(); c.ellipse(0, -78, 38, 16, 0, 0, Math.PI * 2); c.fill(); c.stroke();
    c.fillStyle = '#ef4444';
    c.beginPath();
    c.moveTo(15, -84);
    c.quadraticCurveTo(35, -135, 42, -155);
    c.quadraticCurveTo(28, -135, 20, -84);
    c.closePath(); c.fill();
    c.restore();

    // Lightning Flash
    c.save();
    c.fillStyle = '#334155';
    c.beginPath();
    c.arc(140, 220, 50, 0, Math.PI * 2);
    c.arc(200, 200, 65, 0, Math.PI * 2);
    c.arc(260, 220, 45, 0, Math.PI * 2);
    c.fill();
    const isFlash = Math.floor(t * 8) % 2 === 0;
    if (isFlash) {
      c.strokeStyle = '#facc15'; c.lineWidth = 8;
      c.beginPath();
      c.moveTo(200, 240); c.lineTo(170, 330); c.lineTo(210, 340); c.lineTo(160, 440);
      c.stroke();
      c.fillStyle = '#fef08a';
      c.font = '900 24px sans-serif';
      c.fillText('CRACKLE! ⚡', 220, 380);
    }
    c.restore();

    // Speech Bubble
    const popScale3 = ezBack(Math.min(1.0, sceneT / 0.45));
    drawComicSpeechBubble(c, W * 0.32, IS_VERT ? H * 0.52 : H * 0.42, "Heaven says:\\n'Corrupt ruler? You have\\nthe divine right to REBEL!'", 'down-left', popScale3);

    // Title Banner
    c.save();
    c.translate(W / 2, IS_VERT ? 320 : 65);
    c.fillStyle = 'rgba(15, 10, 12, 0.9)';
    c.strokeStyle = '#facc15'; c.lineWidth = 3;
    c.beginPath(); c.roundRect(-380, -42, 760, 84, 14); c.fill(); c.stroke();
    c.font = '900 36px "Anton", sans-serif';
    c.fillStyle = '#ffffff'; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillText('THE MANDATE OF HEAVEN & CONFUCIUS', 0, 0);
    c.restore();

  } else if (sceneNum === 4) {
    // =======================================================================
    // SCENE 4: QIN SHI HUANG & THE GREAT WALL (Screenshot 4 Match)
    // =======================================================================
    const skyG4 = c.createLinearGradient(0, 0, 0, H * 0.65);
    skyG4.addColorStop(0, '#fef08a');
    skyG4.addColorStop(0.5, '#fed7aa');
    skyG4.addColorStop(1, '#fed7aa');
    c.fillStyle = skyG4; c.fillRect(0, 0, W, H);

    c.fillStyle = '#65a30d';
    c.beginPath();
    c.arc(200, H * 0.55, 340, 0, Math.PI * 2);
    c.arc(W - 200, H * 0.58, 420, 0, Math.PI * 2);
    c.fill();

    // The Great Wall
    c.fillStyle = '#78716c';
    c.strokeStyle = '#292524'; c.lineWidth = 4;
    c.beginPath();
    c.moveTo(0, H * 0.52);
    c.quadraticCurveTo(W * 0.35, H * 0.44, W * 0.65, H * 0.48);
    c.quadraticCurveTo(W * 0.85, H * 0.52, W, H * 0.46);
    c.lineTo(W, H * 0.56);
    c.quadraticCurveTo(W * 0.85, H * 0.62, W * 0.65, H * 0.58);
    c.quadraticCurveTo(W * 0.35, H * 0.54, 0, H * 0.62);
    c.closePath(); c.fill(); c.stroke();
    [W * 0.25, W * 0.72].forEach(wx => {
      c.fillRect(wx - 35, H * 0.41, 70, 75);
      c.strokeRect(wx - 35, H * 0.41, 70, 75);
      c.fillRect(wx - 35, H * 0.38, 20, 15);
      c.fillRect(wx + 15, H * 0.38, 20, 15);
      c.strokeStyle = '#78350f'; c.lineWidth = 4;
      c.beginPath(); c.moveTo(wx, H * 0.38); c.lineTo(wx, H * 0.32); c.stroke();
      c.fillStyle = '#dc2626';
      c.beginPath(); c.moveTo(wx, H * 0.32); c.lineTo(wx + 35, H * 0.34); c.lineTo(wx, H * 0.37); c.fill();
    });

    const groundY4 = H * 0.62;
    c.fillStyle = '#4d7c0f';
    c.fillRect(0, groundY4, W, H - groundY4);

    // Emperor Qin Shi Huang
    c.save();
    const qinX = W * 0.36;
    const qinY = groundY4 - 10;
    c.translate(qinX, qinY);
    c.fillStyle = '#18181b';
    c.strokeStyle = '#eab308'; c.lineWidth = 4;
    c.beginPath(); c.roundRect(-55, -40, 110, 140, [16, 16, 0, 0]); c.fill(); c.stroke();
    c.fillStyle = '#dc2626';
    c.beginPath(); c.moveTo(-35, -40); c.lineTo(0, 15); c.lineTo(35, -40); c.closePath(); c.fill();
    c.strokeStyle = '#facc15'; c.lineWidth = 3;
    c.beginPath(); c.arc(0, 45, 25, 0, Math.PI * 1.5); c.stroke();

    drawCartoonFace(c, 0, -90, { r: 40, skin: '#fed7aa', mouthOpen: isTalk, eyes: 'sly', angryBrows: true });
    c.strokeStyle = '#18181b'; c.lineWidth = 4;
    c.beginPath();
    c.moveTo(-28, -80); c.lineTo(-8, -74); c.lineTo(0, -78); c.lineTo(8, -74); c.lineTo(28, -80);
    c.stroke();
    c.fillStyle = '#18181b';
    c.beginPath(); c.moveTo(-6, -60); c.lineTo(6, -60); c.lineTo(0, -42); c.closePath(); c.fill();

    // Mianliu Crown
    c.fillStyle = '#18181b';
    c.strokeStyle = '#eab308'; c.lineWidth = 4;
    c.beginPath(); c.rect(-65, -150, 130, 20); c.fill(); c.stroke();
    const beadSway = Math.sin(t * 4) * 5;
    c.strokeStyle = '#22c55e'; c.lineWidth = 2.5;
    for (let bx = -50; bx <= 50; bx += 14) {
      c.beginPath(); c.moveTo(bx, -130); c.lineTo(bx + beadSway, -100); c.stroke();
      c.fillStyle = '#facc15'; c.beginPath(); c.arc(bx + beadSway, -100, 3, 0, Math.PI * 2); c.fill();
    }

    // Stamping Giant Bronze Coin
    c.fillStyle = '#d97706';
    c.strokeStyle = '#78350f'; c.lineWidth = 5;
    c.beginPath(); c.arc(-110, 45, 48, 0, Math.PI * 2); c.fill(); c.stroke();
    c.fillStyle = '#4d7c0f';
    c.fillRect(-124, 31, 28, 28);
    c.strokeRect(-124, 31, 28, 28);
    c.fillStyle = '#fef08a';
    c.font = '900 22px sans-serif';
    c.fillText('CLANG! 🪙', -170, -10);
    c.restore();

    // Terracotta Soldier
    c.save();
    const terraX = W * 0.78;
    const terraY = groundY4 - 10;
    c.translate(terraX, terraY);
    c.fillStyle = '#a8a29e';
    c.strokeStyle = '#44403c'; c.lineWidth = 4;
    c.beginPath(); c.roundRect(-35, -30, 70, 120, [10, 10, 0, 0]); c.fill(); c.stroke();
    for (let py = -10; py < 60; py += 18) {
      c.strokeRect(-28, py, 56, 12);
    }
    c.strokeStyle = '#78350f'; c.lineWidth = 6;
    c.beginPath(); c.moveTo(-25, 120); c.lineTo(-25, -130); c.stroke();
    c.fillStyle = '#94a3b8';
    c.beginPath(); c.moveTo(-25, -130); c.lineTo(-45, -100); c.lineTo(-5, -100); c.closePath(); c.fill();
    drawCartoonFace(c, 0, -75, { r: 34, skin: '#d6d3d1', blink: isBlink, eyes: 'normal' });
    c.fillStyle = '#78716c';
    c.beginPath(); c.arc(14, -112, 12, 0, Math.PI * 2); c.fill(); c.stroke();
    c.restore();

    // Speech Bubble
    const popScale4 = ezBack(Math.min(1.0, sceneT / 0.45));
    drawComicSpeechBubble(c, W * 0.48, groundY4 - 190, "ONE EMPIRE! ONE WRITING!\\nONE CURRENCY! NO EXCEPTIONS!", 'down-left', popScale4);

    // Title Banner
    c.save();
    c.translate(W / 2, IS_VERT ? 320 : 65);
    c.fillStyle = 'rgba(15, 10, 12, 0.9)';
    c.strokeStyle = '#facc15'; c.lineWidth = 3;
    c.beginPath(); c.roundRect(-380, -42, 760, 84, 14); c.fill(); c.stroke();
    c.font = '900 36px "Anton", sans-serif';
    c.fillStyle = '#ffffff'; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillText('THE FIRST EMPEROR UNIFICATION', 0, 0);
    c.restore();

  } else if (sceneNum === 5) {
    // =======================================================================
    // SCENE 5: DEADLIEST CIVIL WARS & DYNASTIC REUNIFICATION
    // =======================================================================
    const skyG5 = c.createLinearGradient(0, 0, 0, H * 0.7);
    skyG5.addColorStop(0, '#7f1d1d');
    skyG5.addColorStop(0.5, '#ea580c');
    skyG5.addColorStop(1, '#f97316');
    c.fillStyle = skyG5; c.fillRect(0, 0, W, H);

    c.fillStyle = 'rgba(30, 27, 24, 0.45)';
    for (let i = 0; i < 5; i++) {
      const sx = (i * 240 + t * 20) % W;
      const sy = H * 0.55 - (t * 30 + i * 40) % 300;
      c.beginPath(); c.arc(sx, sy, 55 + i * 8, 0, Math.PI * 2); c.fill();
    }

    const groundY5 = H * 0.65;
    c.fillStyle = '#431407';
    c.fillRect(0, groundY5, W, H - groundY5);

    // Clashing Soldiers
    c.save();
    const clashWave = Math.sin(t * 15) * 8;
    c.translate(W * 0.3 + clashWave, groundY5 - 30);
    c.fillStyle = '#ef4444'; c.fillRect(-25, 0, 50, 75);
    drawCartoonFace(c, 0, -35, { r: 30, skin: '#fed7aa', grin: true, angryBrows: true });
    c.strokeStyle = '#e2e8f0'; c.lineWidth = 6;
    c.beginPath(); c.moveTo(20, 20); c.lineTo(75, -20); c.stroke();
    c.restore();

    c.save();
    c.translate(W * 0.7 - clashWave, groundY5 - 30);
    c.fillStyle = '#3b82f6'; c.fillRect(-25, 0, 50, 75);
    drawCartoonFace(c, 0, -35, { r: 30, skin: '#fed7aa', grin: true, angryBrows: true });
    c.strokeStyle = '#e2e8f0'; c.lineWidth = 6;
    c.beginPath(); c.moveTo(-20, 20); c.lineTo(-75, -20); c.stroke();
    c.restore();

    // Action Star: CLASH!
    c.save();
    c.translate(W / 2, groundY5 - 80);
    c.fillStyle = '#fef08a';
    c.beginPath();
    for (let a = 0; a < Math.PI * 2; a += Math.PI / 4) {
      c.lineTo(Math.cos(a) * 65, Math.sin(a) * 65);
      c.lineTo(Math.cos(a + Math.PI / 8) * 30, Math.sin(a + Math.PI / 8) * 30);
    }
    c.closePath(); c.fill();
    c.font = '900 28px sans-serif';
    c.fillStyle = '#b91c1c';
    c.textAlign = 'center';
    c.fillText('CLASH! 💥', 0, 8);
    c.restore();

    // Flying Arrows
    c.strokeStyle = '#78350f'; c.lineWidth = 4;
    for (let i = 0; i < 3; i++) {
      const ax = (i * 350 + t * 400) % (W + 200) - 100;
      const ay = 380 + Math.sin(ax * 0.01) * 60;
      c.beginPath(); c.moveTo(ax, ay); c.lineTo(ax - 50, ay - 20); c.stroke();
      c.fillStyle = '#f8fafc';
      c.beginPath(); c.moveTo(ax - 50, ay - 20); c.lineTo(ax - 65, ay - 15); c.lineTo(ax - 60, ay - 30); c.fill();
    }

    // Dynastic Pendulum Banner
    c.save();
    c.translate(W / 2, groundY5 + 90);
    c.fillStyle = 'rgba(20, 10, 10, 0.95)';
    c.strokeStyle = '#facc15'; c.lineWidth = 3;
    c.beginPath(); c.roundRect(-420, -35, 840, 70, 12); c.fill(); c.stroke();
    c.font = '800 22px "Inter", sans-serif';
    c.fillStyle = '#ffffff'; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillText('HAN ➔ TANG ➔ SONG ➔ MING ➔ QING · ETERNAL REUNIFICATION', 0, 0);
    c.restore();

    // Speech Bubble
    const popScale5 = ezBack(Math.min(1.0, sceneT / 0.45));
    drawComicSpeechBubble(c, W / 2, groundY5 - 190, "Hundreds of millions died...\\nBUT CHINA ALWAYS PULLED ITSELF BACK!", 'down', popScale5);

    // Title Banner
    c.save();
    c.translate(W / 2, IS_VERT ? 320 : 65);
    c.fillStyle = 'rgba(15, 10, 12, 0.9)';
    c.strokeStyle = '#facc15'; c.lineWidth = 3;
    c.beginPath(); c.roundRect(-380, -42, 760, 84, 14); c.fill(); c.stroke();
    c.font = '900 36px "Anton", sans-serif';
    c.fillStyle = '#ffffff'; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillText('THE DEADLIEST CIVIL WARS & REBIRTH', 0, 0);
    c.restore();

  } else {
    // =======================================================================
    // SCENE 6: CHINA MAP REBORN & IMPERIAL VICTORY (Rebirth & CTA)
    // =======================================================================
    const palG = c.createLinearGradient(0, 0, 0, H);
    palG.addColorStop(0, '#450a0a');
    palG.addColorStop(0.5, '#7f1d1d');
    palG.addColorStop(1, '#991b1b');
    c.fillStyle = palG; c.fillRect(0, 0, W, H);

    // Crimson Pillars with Golden Dragons
    [100, W - 100].forEach(px => {
      c.fillStyle = '#b91c1c';
      c.strokeStyle = '#7f1d1d'; c.lineWidth = 6;
      c.beginPath(); c.rect(px - 45, 0, 90, H); c.fill(); c.stroke();
      c.strokeStyle = '#facc15'; c.lineWidth = 5;
      for (let y = 50; y < H; y += 120) {
        c.beginPath();
        c.arc(px, y, 35, 0, Math.PI);
        c.stroke();
      }
    });

    const daisY = H * 0.65;
    c.fillStyle = '#7f1d1d';
    c.fillRect(0, daisY, W, H - daisY);
    c.fillStyle = '#facc15';
    c.fillRect(0, daisY - 12, W, 24);

    // Red China Map Reborn & Flexing
    c.save();
    const bounceY = daisY - 60 - Math.abs(Math.sin(t * 6)) * 40;
    c.translate(W / 2, bounceY);

    c.strokeStyle = '#18181b'; c.lineWidth = 8; c.lineCap = 'round';
    c.beginPath(); c.moveTo(-120, 20); c.lineTo(-190, -30); c.lineTo(-150, -80); c.stroke();
    c.fillStyle = '#dc2626';
    c.beginPath(); c.arc(-180, -35, 20, 0, Math.PI * 2); c.fill(); c.stroke();
    c.beginPath(); c.moveTo(120, 20); c.lineTo(190, -30); c.lineTo(150, -80); c.stroke();
    c.beginPath(); c.arc(180, -35, 20, 0, Math.PI * 2); c.fill(); c.stroke();

    c.beginPath(); c.moveTo(-50, 140); c.lineTo(-70, 210); c.lineTo(-100, 205); c.stroke();
    c.beginPath(); c.moveTo(50, 140); c.lineTo(70, 210); c.lineTo(100, 205); c.stroke();

    drawChinaMapShape(c, 1.15);

    // Anime Eyes
    c.fillStyle = '#ffffff';
    c.strokeStyle = '#18181b'; c.lineWidth = 4;
    c.beginPath(); c.ellipse(-45, 10, 16, 22, 0, 0, Math.PI * 2); c.fill(); c.stroke();
    c.beginPath(); c.ellipse(15, 12, 16, 22, 0, 0, Math.PI * 2); c.fill(); c.stroke();
    c.fillStyle = '#18181b';
    c.beginPath(); c.arc(-42, 12, 10, 0, Math.PI * 2); c.fill();
    c.beginPath(); c.arc(18, 14, 10, 0, Math.PI * 2); c.fill();
    c.fillStyle = '#ffffff';
    c.beginPath(); c.arc(-45, 8, 4, 0, Math.PI * 2); c.fill();
    c.beginPath(); c.arc(15, 10, 4, 0, Math.PI * 2); c.fill();

    // Smiling Mouth
    c.fillStyle = '#991b1b';
    c.strokeStyle = '#18181b'; c.lineWidth = 4;
    c.beginPath();
    c.arc(-15, 45, 28, 0, Math.PI);
    c.closePath(); c.fill(); c.stroke();
    c.fillStyle = '#fb7185';
    c.beginPath(); c.arc(-15, 62, 15, Math.PI, Math.PI * 2); c.fill();

    // Emperor Golden Crown
    c.fillStyle = '#facc15';
    c.strokeStyle = '#78350f'; c.lineWidth = 4;
    c.beginPath();
    c.moveTo(-60, -145);
    c.lineTo(-40, -195);
    c.lineTo(-15, -155);
    c.lineTo(10, -205);
    c.lineTo(35, -155);
    c.lineTo(60, -195);
    c.lineTo(65, -145);
    c.closePath(); c.fill(); c.stroke();
    c.fillStyle = '#ef4444';
    [-40, 10, 60].forEach(rx => {
      c.beginPath(); c.arc(rx, -170, 7, 0, Math.PI * 2); c.fill();
    });

    c.fillStyle = '#fde047';
    for (let s = 0; s < 4; s++) {
      const sa = s * Math.PI / 2 + t * 4;
      const sx = Math.cos(sa) * 160;
      const sy = Math.sin(sa) * 120;
      c.fillText('✨', sx, sy);
    }
    c.restore();

    // Confetti
    const confettiColors = ['#facc15', '#ef4444', '#3b82f6', '#22c55e', '#ec4899'];
    for (let i = 0; i < 40; i++) {
      const cy = (t * 180 + i * 45) % H;
      const cx = (i * 37 + Math.sin(t * 4 + i) * 35) % W;
      c.fillStyle = confettiColors[i % confettiColors.length];
      c.fillRect(cx, cy, 10, 14);
    }

    // CTA Speech Bubble
    const popScale6 = ezBack(Math.min(1.0, sceneT / 0.45));
    drawComicSpeechBubble(c, W / 2, daisY - 210, "4,000 YEARS AND STILL HERE! 👑\\nWhat was China's most powerful dynasty?\\n👇 DROP YOUR VOTE IN COMMENTS!", 'down', popScale6);

    // Title Banner
    c.save();
    c.translate(W / 2, IS_VERT ? 320 : 65);
    c.fillStyle = 'rgba(15, 10, 12, 0.9)';
    c.strokeStyle = '#facc15'; c.lineWidth = 3;
    c.beginPath(); c.roundRect(-380, -42, 760, 84, 14); c.fill(); c.stroke();
    c.font = '900 36px "Anton", sans-serif';
    c.fillStyle = '#ffffff'; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillText('WHY CHINA NEVER STAYS DEAD', 0, 0);
    c.restore();
  }

  // Karaoke Captions at Bottom Safe Zone (Y = 1440px)
  drawKaraokeCaptions(c, t);

  c.restore();
}
"""
