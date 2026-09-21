import os
import sys
import re
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

base_dtc = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dtc))

from tools.schemas.production_package import ProductionPackage
from tools.project_state import record_gates
from tools.ledger import LEDGER_FILE, fidelity, ledger_hash, load_ledger, tokenize
from tools.prompt_compiler import time_marker

class HarnessGateResult:
    def __init__(self, gate_id: str, name: str, passed: bool, message: str, details: Optional[List[str]] = None):
        self.gate_id = gate_id
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
            "details": self.details
        }

class UGCHarness:
    """
    UGC Production & QA Harness.
    Supervisa y audita automáticamente cada fase del proceso contra los 8 Quality Gates (GATE_8 solo si hay ledger de referencia).
    """

    # Marcas comerciales terceras no autorizadas en el guion del video
    THIRD_PARTY_BRANDS = [
        "rhode", "laneige", "elf", "e.l.f.", "nyx", "l'oreal", "loreal",
        "maybelline", "fenty", "sephora", "ulta", "dior", "chanel", "cerave", "the ordinary"
    ]

    MAX_CLIP_DURATION_S = 10

    # Términos sensibles que activan filtros de moderación/spam
    PROHIBITED_TERMS = [
        r"\bages?\b", r"\bedad(?:es)?\b",
        r"(?<![\w'’])d[\s.\-_]?ms?\b",  # DM, DMs, D.M, D M, d-m
        r"\bdirect messages?\b", r"\bmensajes? directos?\b",
    ]

    # Afirmaciones médicas que disparan moderación (lista conservadora; ampliar según plataforma)
    MEDICAL_CLAIM_TERMS = [
        r"\bcures?\b", r"\bcura(?:r|n|s)?\b", r"\bdiagnos\w*", r"\bdiagnóstic\w*",
        r"\bprescri\w*", r"\breceta médica\b", r"\bclinically proven\b", r"\bcl[ií]nicamente\b",
    ]

    @staticmethod
    def audit_package_json(json_path: Path) -> List[HarnessGateResult]:
        results = []
        if not json_path.exists():
            return [HarnessGateResult("GATE_1", "Schema & Anatomy", False, f"Archivo JSON no encontrado: {json_path}")]

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
        except Exception as e:
            return [HarnessGateResult("GATE_1", "Schema & Anatomy", False, f"Error al parsear JSON: {str(e)}")]

        # ============================================================
        # GATE 1: Schema & Anatomy Validation (Pydantic + Headline)
        # ============================================================
        gate1_passed = True
        gate1_details = []
        try:
            pkg = ProductionPackage(**raw_data)
            gate1_details.append(f"Pydantic validation: SUCCESS ({len(pkg.chunks)} chunks)")
            
            # Audit cover headline length (max 7 words)
            cover_hl = raw_data.get("post_copy", {}).get("cover_headline", "")
            words_hl = [w for w in cover_hl.strip().split() if w]
            if not cover_hl:
                gate1_passed = False
                gate1_details.append("Error: 'cover_headline' está vacío en post_copy.")
            elif len(words_hl) > 7:
                gate1_passed = False
                gate1_details.append(f"Error: 'cover_headline' excede el límite ({len(words_hl)} palabras > máx 7): '{cover_hl}'")
            else:
                gate1_details.append(f"Cover headline verificado: '{cover_hl}' ({len(words_hl)} palabras <= 7)")

            # Check anatomy audit in each chunk
            for ch in pkg.chunks:
                if not ch.composition_audit.left_subject.character_id:
                    gate1_passed = False
                    gate1_details.append(f"Chunk {ch.chunk_id}: falta character_id en left_subject")

        except Exception as e:
            gate1_passed = False
            gate1_details.append(f"Error en validación de Pydantic: {str(e)}")

        results.append(HarnessGateResult(
            "GATE_1", "Schema & Anatomy Audit", gate1_passed,
            "Schema Pydantic y anatomía 100% conformes" if gate1_passed else "Fallo en validación de Schema",
            gate1_details
        ))

        # ============================================================
        # GATE 2: Timing & Cadence Audit (WPS and Word Count Limits)
        # ============================================================
        gate2_passed = True
        gate2_details = []
        chunks = raw_data.get("chunks", [])
        
        for ch in chunks:
            cid = ch.get("chunk_id", 0)
            text = ch.get("voiceover_clean_tts", "")
            dur_s = ch.get("recommended_duration_s", 8)
            words = [w for w in text.split() if w]
            w_count = len(words)
            wps = round(w_count / dur_s, 2) if dur_s > 0 else 0.0

            if dur_s > UGCHarness.MAX_CLIP_DURATION_S:
                gate2_passed = False
                gate2_details.append(f"Chunk {cid}: duración {dur_s}s excede el máximo de {UGCHarness.MAX_CLIP_DURATION_S}s por clip IA (Veo3/Kling).")
            declared_wc = ch.get("word_count")
            if declared_wc is not None and declared_wc != w_count:
                gate2_passed = False
                gate2_details.append(f"Chunk {cid}: word_count declarado ({declared_wc}) no coincide con el texto real ({w_count}).")

            # Max allowed words per chunk based on duration:
            max_words = int(dur_s * 2.4)
            if w_count > max_words:
                gate2_passed = False
                gate2_details.append(f"Chunk {cid} ({dur_s}s): {w_count} palabras excede el límite máximo de {max_words} palabras ({wps} WPS > 2.4 WPS).")
            else:
                margin = round(dur_s - (w_count / 2.3), 1)
                gate2_details.append(f"Chunk {cid} ({dur_s}s): {w_count} palabras ({wps} WPS) -> Margen libre: +{margin}s")

        results.append(HarnessGateResult(
            "GATE_2", "Timing & Cadence Audit", gate2_passed,
            "Todas las duraciones respetan la constante de locución (<= 2.4 WPS)" if gate2_passed else "Exceso de palabras detectado en locución",
            gate2_details
        ))

        # ============================================================
        # GATE 3: Safety & Anti-Filter Moderation Audit
        # ============================================================
        gate3_passed = True
        gate3_details = []
        
        # Check all voiceover text and prompts (not post caption which may mention age for comments)
        all_texts_to_scan = []
        for ch in chunks:
            all_texts_to_scan.append((f"Chunk {ch.get('chunk_id')} Voiceover", ch.get("voiceover_clean_tts", "")))
            all_texts_to_scan.append((f"Chunk {ch.get('chunk_id')} Video Prompt", ch.get("video_motion_prompt_i2v", "")))
            all_texts_to_scan.append((f"Chunk {ch.get('chunk_id')} Image Prompt", ch.get("midjourney_prompt_9_16", "")))

        for source_name, txt in all_texts_to_scan:
            for pattern in UGCHarness.PROHIBITED_TERMS:
                m = re.search(pattern, txt, flags=re.IGNORECASE)
                if m:
                    gate3_passed = False
                    gate3_details.append(f"Infracción en {source_name}: detectado término prohibido '{m.group(0)}' (Filtro anti-spam/edad).")
            for pattern in UGCHarness.MEDICAL_CLAIM_TERMS:
                m = re.search(pattern, txt, flags=re.IGNORECASE)
                if m:
                    gate3_passed = False
                    gate3_details.append(f"Infracción en {source_name}: posible afirmación médica '{m.group(0)}'.")

        if gate3_passed:
            gate3_details.append("Escaneo de moderación limpio: cero términos censurados ('age', 'DM') ni afirmaciones médicas en guiones de video.")

        results.append(HarnessGateResult(
            "GATE_3", "Safety & Anti-Filter Moderation", gate3_passed,
            "Guion y video 100% conformes con políticas anti-filtros" if gate3_passed else "Términos sensibles detectados en guion",
            gate3_details
        ))

        # ============================================================
        # GATE 4: Brand Protection & Decoupling Audit
        # ============================================================
        gate4_passed = True
        gate4_details = []

        keyword = (raw_data.get("post_copy", {}).get("manychat_keyword") or "").strip()
        if not keyword:
            gate4_passed = False
            gate4_details.append("Falta 'manychat_keyword' en post_copy: la conversión de marca depende 100% de ManyChat.")

        own_brand = (raw_data.get("brand") or "").strip().lower()
        for ch in chunks:
            cid = ch.get("chunk_id")
            vo = ch.get("voiceover_clean_tts", "").lower()
            if own_brand and re.search(r'\b' + re.escape(own_brand) + r'\b', vo):
                gate4_passed = False
                gate4_details.append(f"Chunk {cid}: la marca propia '{own_brand}' aparece en el diálogo (debe convertirse solo vía ManyChat).")
            for brand in UGCHarness.THIRD_PARTY_BRANDS:
                if re.search(r'\b' + re.escape(brand) + r'\b', vo):
                    gate4_passed = False
                    gate4_details.append(f"Chunk {cid}: mención no autorizada de marca comercial '{brand}' en diálogo.")

        if gate4_passed:
            gate4_details.append("Desacoplamiento de marca perfecto: solo términos genéricos/educativos en video.")

        results.append(HarnessGateResult(
            "GATE_4", "Brand Decoupling Audit", gate4_passed,
            "Cero marcas comerciales en el diálogo del video" if gate4_passed else "Marcas terceras detectadas en guion",
            gate4_details
        ))

        return results

    MIN_CLIP_BITRATE = 500_000

    @staticmethod
    def _probe_clip(ffprobe_bin: str, clip: Path) -> List[str]:
        """Devuelve la lista de problemas del clip (vacía si es válido)."""
        cmd = [ffprobe_bin, "-v", "error", "-show_entries",
               "stream=codec_type,width,height:format=duration,bit_rate", "-of", "json", str(clip)]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            info = json.loads(res.stdout)
        except Exception as e:
            return [f"no se pudo analizar con ffprobe ({e})"]

        problems = []
        streams = info.get("streams", [])
        video = next((s for s in streams if s.get("codec_type") == "video"), None)
        audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
        fmt = info.get("format", {})

        if not video:
            problems.append("sin stream de video")
        else:
            w, h = int(video.get("width", 0)), int(video.get("height", 0))
            if h <= w:
                problems.append(f"no es vertical 9:16 ({w}x{h})")
            elif abs((w / h) - (9 / 16)) > 0.02:
                problems.append(f"relación de aspecto {w}x{h} se desvía de 9:16")
        if not audio:
            problems.append("sin stream de audio")
        try:
            duration = float(fmt.get("duration", 0))
            if duration <= 0:
                problems.append("duración inválida")
            elif duration > UGCHarness.MAX_CLIP_DURATION_S + 0.5:
                problems.append(f"duración {duration:.1f}s excede el máximo de {UGCHarness.MAX_CLIP_DURATION_S}s")
        except (TypeError, ValueError):
            problems.append("duración ilegible")
        try:
            if int(fmt.get("bit_rate", 0)) < UGCHarness.MIN_CLIP_BITRATE:
                problems.append(f"bitrate demasiado bajo ({fmt.get('bit_rate', 0)} bps < {UGCHarness.MIN_CLIP_BITRATE})")
        except (TypeError, ValueError):
            problems.append("bitrate ilegible")
        return problems

    @staticmethod
    def audit_raw_clips(raw_dir: Path, expected_count: int = 6) -> HarnessGateResult:
        if not raw_dir.exists():
            return HarnessGateResult("GATE_5", "Raw Clips Integrity", False, f"Carpeta no encontrada: {raw_dir}")

        sys.path.insert(0, str(base_dtc / "auto-captions-service"))
        try:
            from app.core.ffmpeg_utils import FFmpegLocator
            _, ffprobe_bin = FFmpegLocator.get_binaries()
        except Exception:
            ffprobe_bin = "ffprobe"

        passed = True
        details = []
        found_clips = 0

        for i in range(1, expected_count + 1):
            clip = raw_dir / f"{i}.mp4"
            if not clip.exists():
                passed = False
                details.append(f"Clip faltante: {i}.mp4")
                continue
            
            found_clips += 1
            problems = UGCHarness._probe_clip(ffprobe_bin, clip)
            if problems:
                passed = False
                details.extend(f"Clip {i}.mp4: {p}" for p in problems)
            else:
                details.append(f"Clip {i}.mp4: válido ({clip.stat().st_size} bytes)")

        if found_clips < expected_count:
            passed = False

        return HarnessGateResult(
            "GATE_5", "Raw Clips Integrity", passed,
            f"Todos los {expected_count} clips presentes y válidos" if passed else f"Incompletitud en clips ({found_clips}/{expected_count})",
            details
        )

    @staticmethod
    def audit_deliverables(deliverables_dir: Path, project_id: str) -> HarnessGateResult:
        if not deliverables_dir.exists():
            return HarnessGateResult("GATE_6", "Canonical Deliverables Governance", False, f"Carpeta de entregables no encontrada: {deliverables_dir}")

        passed = True
        details = []

        files = list(deliverables_dir.glob("*"))
        file_names = [f.name for f in files if f.is_file()]

        expected = {
            "video": lambda f: f.endswith("_Final_1080x1920.mp4"),
            "subtitles": lambda f: f.endswith("_Subtitles.srt"),
            "cover": lambda f: f.endswith("_Cover.jpg"),
            "copy": lambda f: f == "post_copy_title_and_caption.txt",
        }
        labels = {
            "video": f"[ID]_Final_1080x1920.mp4",
            "subtitles": "[ID]_Subtitles.srt",
            "cover": "[ID]_Cover.jpg",
            "copy": "post_copy_title_and_caption.txt",
        }
        matched = set()
        for key, check in expected.items():
            hits = [f for f in file_names if check(f)]
            if len(hits) == 1:
                matched.add(hits[0])
                details.append(f"{labels[key]} presente ({hits[0]}).")
            elif not hits:
                passed = False
                details.append(f"Falta {labels[key]}")
            else:
                passed = False
                details.append(f"Múltiples archivos para {labels[key]}: {hits}")

        extras = [f for f in file_names if f not in matched]
        if extras:
            passed = False
            details.append(f"Archivos no canónicos (deben ser exactamente 4): {extras}")

        copy_file = deliverables_dir / "post_copy_title_and_caption.txt"
        if copy_file.exists() and "HEADLINE DE PORTADA" not in copy_file.read_text(encoding="utf-8"):
            passed = False
            details.append("post_copy_title_and_caption.txt no contiene 'HEADLINE DE PORTADA'.")

        return HarnessGateResult(
            "GATE_6", "Canonical Deliverables Governance", passed,
            "Entrega canónica 100% conforme (4/4 archivos válidos)" if passed else "Entregables incompletos o no conformes",
            details
        )

    @staticmethod
    def audit_checkpoint1(json_path: Path, project_dir: Path):
        """Devuelve (passed, details): checkpoint1.json existe, está confirmado y coincide con el paquete."""
        cp_path = project_dir / "checkpoint1.json"
        if not cp_path.exists():
            return False, ["Falta checkpoint1.json: el Checkpoint 1 no quedó registrado (tools/checkpoint1.py)."]
        try:
            cp = json.loads(cp_path.read_text(encoding="utf-8"))
            pkg = json.loads(Path(json_path).read_text(encoding="utf-8"))
        except Exception as e:
            return False, [f"No se pudo leer checkpoint1.json o el paquete: {e}"]

        passed, details = True, []
        missing = [k for k in ("scene_mode", "outfit", "manychat_keyword", "cover_headline") if not str(cp.get(k, "")).strip()]
        if missing:
            passed = False
            details.append(f"checkpoint1.json incompleto, faltan: {missing}")
        if cp.get("confirmed_by_user") is not True:
            passed = False
            details.append("checkpoint1.json no está marcado como confirmado por el usuario.")

        post = pkg.get("post_copy", {})
        for cp_key, pkg_val, label in (
            ("manychat_keyword", post.get("manychat_keyword", ""), "manychat_keyword"),
            ("cover_headline", post.get("cover_headline", ""), "cover_headline"),
        ):
            if str(cp.get(cp_key, "")).strip().lower() != str(pkg_val).strip().lower():
                passed = False
                details.append(f"'{label}' del paquete ('{pkg_val}') no coincide con el confirmado en Checkpoint 1 ('{cp.get(cp_key, '')}').")
        if passed:
            details.append("Checkpoint 1 registrado, confirmado y coherente con el paquete (keyword y headline).")
        return passed, details

    LENGTH_TOLERANCE = 0.10
    MIN_CONTENT_OVERLAP = 0.50
    MIN_DIALOGUE_FIDELITY = 0.85
    TIME_TOLERANCE_S = 0.05
    STOPWORDS = set(
        "a an the and or but of to in on at for with your you i my me it its is are was be this that "
        "these those just so then than as if by from into up out not no do does did have has had will "
        "would can could very really "
        "el la los las un una unos unas y o pero de del al en con por para tu tus mi mis yo me te se su sus "
        "es son era ser esto esta este estos estas eso solo así entonces que como si no lo le les muy más ya "
        "tiene tienen hay fue ha han".split()
    )

    @staticmethod
    def _words(text: str) -> List[str]:
        return re.findall(r"[a-záéíóúñü']+", text.lower())

    @staticmethod
    def _extract_reference_text(reference_dir: Path) -> Optional[str]:
        files = sorted(reference_dir.glob("script_beats_*.txt")) if reference_dir.exists() else []
        if not files:
            return None
        raw = files[0].read_text(encoding="utf-8", errors="replace")
        m = re.search(r"TRANSCRIPCI[^\n]*\n=+\n(.*?)\n=+\n", raw, re.S)
        if m:
            return m.group(1)
        quoted = re.findall(r'Voiceover Original:\s*"([^"]*)"', raw)
        return " ".join(quoted) if quoted else None

    @staticmethod
    def audit_reference_fidelity(json_path: Path, reference_dir: Path) -> HarnessGateResult:
        """Regla 70/30: el guion nuevo conserva la extensión y el núcleo semántico de la referencia."""
        name = "Reference Fidelity (70/30)"
        ref_text = UGCHarness._extract_reference_text(reference_dir)
        if not ref_text:
            return HarnessGateResult("GATE_7", name, False,
                                     "No se pudo leer el guion de referencia (script_beats_*.txt) en 01_Reference/")
        try:
            data = json.loads(Path(json_path).read_text(encoding="utf-8"))
            gen_text = " ".join(c.get("voiceover_clean_tts", "") for c in data.get("chunks", []))
        except Exception as e:
            return HarnessGateResult("GATE_7", name, False, f"No se pudo leer el paquete JSON: {e}")

        ref_words, gen_words = UGCHarness._words(ref_text), UGCHarness._words(gen_text)
        if not ref_words or not gen_words:
            return HarnessGateResult("GATE_7", name, False, "Guion de referencia o generado vacío")

        passed, details = True, []
        ratio = len(gen_words) / len(ref_words)
        lo, hi = 1 - UGCHarness.LENGTH_TOLERANCE, 1 + UGCHarness.LENGTH_TOLERANCE
        details.append(f"Extensión: {len(gen_words)} palabras vs {len(ref_words)} de la referencia (ratio {ratio:.2f}, rango {lo:.2f}-{hi:.2f})")
        if not lo <= ratio <= hi:
            passed = False
            details.append("Error: la extensión del guion se desvía de la referencia.")

        def content(ws):
            return {w for w in ws if w not in UGCHarness.STOPWORDS and len(w) > 2}
        ref_c, gen_c = content(ref_words), content(gen_words)
        overlap = len(ref_c & gen_c) / len(ref_c) if ref_c else 0.0
        details.append(f"Núcleo semántico: {overlap:.2f} de las palabras de contenido de la referencia se conservan (mínimo {UGCHarness.MIN_CONTENT_OVERLAP:.2f})")
        if overlap < UGCHarness.MIN_CONTENT_OVERLAP:
            passed = False
            details.append("Error: el guion se aleja demasiado del contenido de la referencia.")
        details.append("Nota: el solapamiento léxico es una heurística; la equivalencia de sentido requiere revisión humana.")

        return HarnessGateResult(
            "GATE_7", name, passed,
            "Extensión y núcleo de la referencia conservados" if passed else "El guion no respeta la extensión/sentido de la referencia",
            details
        )

    @staticmethod
    def ledger_active(project_dir: Path) -> bool:
        """True si el proyecto usa ledger de referencia (archivo presente o hash registrado en checkpoint1.json)."""
        if (Path(project_dir) / "01_Reference" / LEDGER_FILE).exists():
            return True
        try:
            cp = json.loads((Path(project_dir) / "checkpoint1.json").read_text(encoding="utf-8"))
            return bool(cp.get("ledger_hash"))
        except Exception:
            return False

    @staticmethod
    def audit_ledger_dialogue(json_path: Path, project_dir: Path) -> HarnessGateResult:
        """GATE_7 con ledger: cada fila (salvo CTA) conserva >= 85% de sus palabras en los pasos que la replican."""
        name = "Reference Fidelity (Ledger, dialogue verbatim)"
        try:
            ledger = load_ledger(Path(project_dir) / "01_Reference" / LEDGER_FILE)
            chunks = json.loads(Path(json_path).read_text(encoding="utf-8")).get("chunks", [])
            if not isinstance(chunks, list):
                raise ValueError("'chunks' no es una lista")
        except Exception as e:
            return HarnessGateResult("GATE_7", name, False, f"No se pudo leer el ledger o el paquete: {e}")
        errors, details = [], []
        for row in ledger.rows:
            if row.is_cta or not tokenize(row.dialogue_verbatim):
                continue
            gen = " ".join(
                str(s.get("dialogue") or "")
                for ch in chunks if isinstance(ch, dict) and isinstance(ch.get("action_timeline"), list)
                for s in ch["action_timeline"] if isinstance(s, dict) and s.get("ledger_row") == row.id)
            score = fidelity(row.dialogue_verbatim, gen)
            details.append(f"{row.id}: {score:.2f} de las palabras conservadas (mínimo {UGCHarness.MIN_DIALOGUE_FIDELITY:.2f})")
            if score < UGCHarness.MIN_DIALOGUE_FIDELITY:
                errors.append(f"Error: {row.id} se aleja del diálogo literal de la referencia.")
        passed = not errors
        return HarnessGateResult(
            "GATE_7", name, passed,
            "Diálogo fiel a la referencia" if passed else "El diálogo se aleja de la referencia",
            details + errors)

    @staticmethod
    def audit_action_coverage(json_path: Path, project_dir: Path) -> HarnessGateResult:
        """GATE_8: cada fila del ledger está cubierta, en orden, con timeline contiguo y reflejada en el prompt."""
        name = "Action Coverage (Ledger)"
        project_dir = Path(project_dir)
        ledger_path = project_dir / "01_Reference" / LEDGER_FILE
        try:
            ledger = load_ledger(ledger_path)
            pkg = json.loads(Path(json_path).read_text(encoding="utf-8"))
            cp = json.loads((project_dir / "checkpoint1.json").read_text(encoding="utf-8"))
        except Exception as e:
            return HarnessGateResult("GATE_8", name, False, f"No se pudo leer ledger, paquete o checkpoint1.json: {e}")

        tol = UGCHarness.TIME_TOLERANCE_S
        errors = []
        confirmed = cp.get("ledger_hash")
        if not confirmed:
            errors.append("El ledger no está confirmado en Checkpoint 1 (falta ledger_hash; usa --ledger-confirmed).")
        elif confirmed != ledger_hash(ledger_path):
            errors.append("El ledger cambió después de confirmarlo en Checkpoint 1; vuelve a confirmarlo.")

        order = {r.id: n for n, r in enumerate(ledger.rows)}
        covered, last_order = set(), -1
        chunk_list = pkg.get("chunks", []) if isinstance(pkg, dict) else []
        if not isinstance(chunk_list, list):
            errors.append("'chunks' no es una lista.")
            chunk_list = []
        for ch in chunk_list:
            if not isinstance(ch, dict):
                errors.append("Chunk con datos malformados (no es un objeto).")
                continue
            cid = ch.get("chunk_id")
            try:
                rows, steps = ch.get("ledger_rows", []), ch.get("action_timeline", [])
                if not rows or not steps:
                    errors.append(f"Chunk {cid}: falta ledger_rows o action_timeline.")
                    continue
                if not isinstance(rows, list) or not isinstance(steps, list):
                    errors.append(f"Chunk {cid}: datos malformados (ledger_rows y action_timeline deben ser listas).")
                    continue
                is_num = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
                dur = ch.get("recommended_duration_s")
                if not is_num(dur):
                    errors.append(f"Chunk {cid}: recommended_duration_s ausente o no numérico.")
                    continue
                for rid in rows:
                    if rid not in order:
                        errors.append(f"Chunk {cid}: ledger_rows contiene '{rid}', que no existe en el ledger.")
                prompt = str(ch.get("video_motion_prompt_i2v") or "")
                prev_t1, step_rows = 0.0, set()
                for s in steps:
                    if not isinstance(s, dict):
                        errors.append(f"Chunk {cid}: paso con datos malformados (no es un objeto).")
                        continue
                    t0, t1, rid = s.get("t0"), s.get("t1"), s.get("ledger_row")
                    if not (is_num(t0) and is_num(t1)):
                        errors.append(f"Chunk {cid}: paso {rid} sin t0/t1 numéricos.")
                        continue
                    if t1 <= t0:
                        errors.append(f"Chunk {cid}: paso {rid} con t1 <= t0.")
                    if abs(t0 - prev_t1) > tol:
                        errors.append(f"Chunk {cid}: hueco o solape en el timeline ({prev_t1:g}s -> {t0:g}s).")
                    prev_t1 = t1
                    if rid not in rows or rid not in order:
                        errors.append(f"Chunk {cid}: el paso '{rid}' no está en los ledger_rows del chunk/ledger.")
                        continue
                    step_rows.add(rid)
                    covered.add(rid)
                    if order[rid] < last_order:
                        errors.append(f"Chunk {cid}: pasos fuera de orden respecto al ledger ({rid}).")
                    last_order = max(last_order, order[rid])
                    if not str(s.get("action", "")).strip():
                        errors.append(f"Chunk {cid}: paso {rid} sin acción.")
                    if time_marker(t0, t1) not in prompt:
                        errors.append(f"Chunk {cid}: el prompt no contiene el marcador {time_marker(t0, t1)} (recompila con tools/prompt_compiler.py).")
                    if s.get("dialogue") and str(s["dialogue"]) not in prompt:
                        errors.append(f"Chunk {cid}: el prompt no contiene el diálogo del paso {rid}.")
                if prev_t1 > dur + tol:
                    errors.append(f"Chunk {cid}: el timeline termina en {prev_t1:g}s, más allá de la duración del clip.")
                for rid in set(rows) - step_rows:
                    errors.append(f"Chunk {cid}: la fila {rid} está en ledger_rows pero ningún paso la replica.")
            except (TypeError, ValueError, AttributeError, KeyError) as e:
                errors.append(f"Chunk {cid}: datos malformados ({e}).")

        missing = [r.id for r in ledger.rows if r.id not in covered]
        if missing:
            errors.append(f"Filas del ledger sin cubrir: {missing}")
        passed = not errors
        details = errors or [f"Las {len(ledger.rows)} filas del ledger están cubiertas, en orden y con timeline contiguo."]
        return HarnessGateResult(
            "GATE_8", name, passed,
            "Todas las acciones de la referencia están cubiertas" if passed else "Acciones de la referencia sin cubrir o timeline inválido",
            details)

    @classmethod
    def run_full_project_audit(cls, base_brand_dir: Path, prod_folder_name: str, deliverable_name: Optional[str] = None, precheck: bool = False) -> Dict[str, Any]:
        prod_dir = base_brand_dir / "04_IN_PRODUCTION" / prod_folder_name
        name_parts = prod_folder_name.split("_")
        if len(name_parts) < 2 or not name_parts[1]:
            raise ValueError(f"Nombre de proyecto inválido '{prod_folder_name}': se espera PROD_[XXX]_[referencia]")
        json_path = prod_dir / "02_First_Frames" / f"production_package_{name_parts[0]}_{name_parts[1]}.json"
        
        # Fallback search for json
        if not json_path.exists():
            found = list((prod_dir / "02_First_Frames").glob("*.json"))
            if found:
                json_path = found[0]

        raw_clips_dir = prod_dir / "03_Raw_Clips"
        
        deliv_id = deliverable_name or name_parts[1]
        deliverables_dir = base_brand_dir / "05_PROCESSED_DELIVERABLES" / deliv_id

        expected_chunks = None
        if json_path and json_path.exists():
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    expected_chunks = len(json.load(f).get("chunks", [])) or None
            except Exception:
                expected_chunks = None

        all_gates = []
        # Gates 1 to 4
        all_gates.extend(cls.audit_package_json(json_path))

        cp_passed, cp_details = cls.audit_checkpoint1(json_path, prod_dir)
        if all_gates and all_gates[0].gate_id == "GATE_1":
            all_gates[0].details.extend(cp_details)
            if not cp_passed:
                all_gates[0].passed = False
                all_gates[0].message = "Fallo en validación de Schema o Checkpoint 1"
        
        # Gate 5 (omitido en precheck: aún no hay clips)
        if not precheck:
            if expected_chunks is None:
                all_gates.append(HarnessGateResult("GATE_5", "Raw Clips Integrity", False,
                                                   "No se puede determinar el nº de clips: paquete JSON ausente o sin chunks"))
            else:
                all_gates.append(cls.audit_raw_clips(raw_clips_dir, expected_count=expected_chunks))

            # Gate 6
            all_gates.append(cls.audit_deliverables(deliverables_dir, deliv_id))

        # Gate 7 (+ Gate 8 con ledger): fidelidad a la referencia
        if cls.ledger_active(prod_dir):
            all_gates.append(cls.audit_ledger_dialogue(json_path, prod_dir))
            all_gates.append(cls.audit_action_coverage(json_path, prod_dir))
        else:
            all_gates.append(cls.audit_reference_fidelity(json_path, prod_dir / "01_Reference"))

        total_gates = len(all_gates)
        passed_gates = sum(1 for g in all_gates if g.passed)
        is_compliant = (passed_gates == total_gates)

        if prod_dir.exists():
            record_gates(prod_dir, [g.to_dict() for g in all_gates], precheck=precheck)

        return {
            "project_name": prod_folder_name,
            "deliverable_id": deliv_id,
            "is_compliant": is_compliant,
            "precheck": precheck,
            "score": f"{passed_gates}/{total_gates}",
            "gates": [g.to_dict() for g in all_gates]
        }

    @staticmethod
    def print_scorecard(report: Dict[str, Any]):
        print("\n" + "=" * 75)
        print(f"  [QA HARNESS] SCORECARD: {report['project_name']}")
        print("=" * 75)
        
        for g in report["gates"]:
            status_icon = "[PASS]" if g["passed"] else "[FAIL]"
            print(f"{status_icon} {g['gate_id']}: {g['name']}")
            print(f"       Resumen: {g['message']}")
            for d in g["details"]:
                print(f"       * {d}")
            print("-" * 75)
        
        if report["is_compliant"]:
            if report.get("precheck"):
                print(f"RESULTADO PRECHECK: {report['score']} GATES APROBADOS -- OK para generar clips (no es certificación final)")
            else:
                print(f"RESULTADO: {report['score']} GATES APROBADOS -- CALIDAD DE AGENCIA CERTIFICADA")
        else:
            print(f"RESULTADO: {report['score']} GATES APROBADOS -- REQUIERE CORRECCION")
        print("=" * 75 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UGC Production & QA Harness")
    parser.add_argument("--json", help="Path to production_package_PROD_XXX.json to audit Gates 1-4")
    parser.add_argument("--project", help="Name of project folder in 04_IN_PRODUCTION (e.g. PROD_001_cuenta_1)")
    parser.add_argument("--brand", default=None, help="Brand directory name (optional, auto-detected if omitted)")
    parser.add_argument("--precheck", action="store_true",
                        help="Corre solo los gates 1-4, 7 y 8 (sin clips ni entregables) antes de gastar en generación de video")
    parser.add_argument("--deliverable", help="Deliverable folder name (optional, auto-detected if omitted)")
    args = parser.parse_args()

    harness = UGCHarness()

    if args.json:
        results = harness.audit_package_json(Path(args.json))
        report = {
            "project_name": Path(args.json).stem,
            "is_compliant": all(r.passed for r in results),
            "score": f"{sum(1 for r in results if r.passed)}/{len(results)}",
            "gates": [r.to_dict() for r in results]
        }
        harness.print_scorecard(report)
    elif args.project:
        if args.brand:
            brand_path = base_dtc / args.brand
        else:
            # Auto-detect brand directory containing this project
            found = list(base_dtc.glob(f"*/04_IN_PRODUCTION/{args.project}"))
            if found:
                brand_path = found[0].parent.parent
            else:
                candidates = [d for d in base_dtc.iterdir() if d.is_dir() and (d / "04_IN_PRODUCTION").exists()]
                brand_path = candidates[0] if candidates else base_dtc

        report = harness.run_full_project_audit(brand_path, args.project, args.deliverable, precheck=args.precheck)
        harness.print_scorecard(report)
    else:
        print("UGC Production & QA Harness listo. Usa --help para ver los comandos.")
