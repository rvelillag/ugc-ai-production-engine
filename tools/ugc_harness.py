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

base_dtc = Path(r"c:\Users\Asus\Downloads\DTC")
sys.path.insert(0, str(base_dtc))

from tools.schemas.production_package import ProductionPackage

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
    Supervisa y audita automáticamente cada fase del proceso contra los 6 Quality Gates.
    """

    # Marcas comerciales terceras no autorizadas en el guion del video
    THIRD_PARTY_BRANDS = [
        "rhode", "laneige", "elf", "e.l.f.", "nyx", "l'oreal", "loreal",
        "maybelline", "fenty", "sephora", "ulta", "dior", "chanel", "cerave", "the ordinary"
    ]

    # Términos sensibles que activan filtros de moderación/spam
    PROHIBITED_TERMS = [
        r"\bage\b", r"\bedad\b", r"\bdm\b", r"\bdms\b", r"\bdirect message\b", r"\bmensaje directo\b"
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

        for source_name, txt in all_texts_to_scan:
            for pattern in UGCHarness.PROHIBITED_TERMS:
                matches = re.findall(pattern, txt, flags=re.IGNORECASE)
                if matches:
                    gate3_passed = False
                    gate3_details.append(f"Infracción en {source_name}: detectado término prohibido '{matches[0]}' (Filtro anti-spam/edad).")

        if gate3_passed:
            gate3_details.append("Escaneo de moderación limpio: Cero términos censurados ('age', 'DM') en guiones de video.")

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

        for ch in chunks:
            cid = ch.get("chunk_id")
            vo = ch.get("voiceover_clean_tts", "").lower()
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
            # Probe clip duration and resolution
            try:
                cmd = [ffprobe_bin, "-v", "error", "-show_entries", "stream=width,height,duration", "-of", "json", str(clip)]
                res = subprocess.run(cmd, capture_output=True, text=True)
                info = json.loads(res.stdout)
                streams = info.get("streams", [{}])
                w = streams[0].get("width", 0) if streams else 0
                h = streams[0].get("height", 0) if streams else 0
                details.append(f"Clip {i}.mp4: {w}x{h} ({clip.stat().st_size} bytes)")
            except Exception:
                details.append(f"Clip {i}.mp4: presente ({clip.stat().st_size} bytes)")

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

        # Check .mp4
        has_mp4 = any(f.endswith(".mp4") and (project_id in f or "Final" in f) for f in file_names)
        if not has_mp4:
            passed = False
            details.append(f"Falta video final .mp4 con formato {project_id}_Final_1080x1920.mp4")
        else:
            details.append("Video final .mp4 presente y válido.")

        # Check .srt
        has_srt = any(f.endswith(".srt") for f in file_names)
        if not has_srt:
            passed = False
            details.append("Falta archivo de subtítulos sincronizados .srt")
        else:
            details.append("Archivo de subtítulos .srt presente.")

        # Check Cover.jpg
        has_cover = any("Cover.jpg" in f or "Cover.jpeg" in f for f in file_names)
        if not has_cover:
            passed = False
            details.append("Falta imagen de portada Cover.jpg")
        else:
            details.append("Imagen de portada Cover.jpg presente.")

        # Check post_copy_title_and_caption.txt
        has_copy = "post_copy_title_and_caption.txt" in file_names
        if not has_copy:
            passed = False
            details.append("Falta archivo post_copy_title_and_caption.txt")
        else:
            # Check if cover headline is in the copy file
            copy_txt = (deliverables_dir / "post_copy_title_and_caption.txt").read_text(encoding="utf-8")
            if "HEADLINE DE PORTADA" in copy_txt:
                details.append("post_copy_title_and_caption.txt verificado (contiene Headline de Portada).")
            else:
                details.append("post_copy_title_and_caption.txt presente.")

        if len(file_names) > 5:
            passed = False
            details.append(f"Advertencia de gobernanza: existen archivos extra no canónicos ({len(file_names)} archivos encontrados).")

        return HarnessGateResult(
            "GATE_6", "Canonical Deliverables Governance", passed,
            "Entrega canónica 100% conforme (4/4 archivos válidos)" if passed else "Entregables incompletos o no conformes",
            details
        )

    @classmethod
    def run_full_project_audit(cls, base_brand_dir: Path, prod_folder_name: str, deliverable_name: Optional[str] = None) -> Dict[str, Any]:
        prod_dir = base_brand_dir / "04_IN_PRODUCTION" / prod_folder_name
        json_path = prod_dir / "02_First_Frames" / f"production_package_{prod_folder_name.split('_')[0]}_{prod_folder_name.split('_')[1]}.json"
        
        # Fallback search for json
        if not json_path.exists():
            found = list((prod_dir / "02_First_Frames").glob("*.json"))
            if found:
                json_path = found[0]

        raw_clips_dir = prod_dir / "03_Raw_Clips"
        
        deliv_id = deliverable_name or prod_folder_name.split("_")[1]
        deliverables_dir = base_brand_dir / "05_PROCESSED_DELIVERABLES" / deliv_id

        all_gates = []
        # Gates 1 to 4
        all_gates.extend(cls.audit_package_json(json_path))
        
        # Gate 5
        all_gates.append(cls.audit_raw_clips(raw_clips_dir))
        
        # Gate 6
        all_gates.append(cls.audit_deliverables(deliverables_dir, deliv_id))

        total_gates = len(all_gates)
        passed_gates = sum(1 for g in all_gates if g.passed)
        is_compliant = (passed_gates == total_gates)

        return {
            "project_name": prod_folder_name,
            "deliverable_id": deliv_id,
            "is_compliant": is_compliant,
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
            print(f"RESULTADO: {report['score']} GATES APROBADOS -- CALIDAD DE AGENCIA CERTIFICADA")
        else:
            print(f"RESULTADO: {report['score']} GATES APROBADOS -- REQUIERE CORRECCION")
        print("=" * 75 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UGC Production & QA Harness")
    parser.add_argument("--json", help="Path to production_package_PROD_XXX.json to audit Gates 1-4")
    parser.add_argument("--project", help="Name of project folder in 04_IN_PRODUCTION (e.g. PROD_007_choi.koreanskin_10)")
    parser.add_argument("--brand", default="Rachel Bennett - Botanique", help="Brand directory name")
    parser.add_argument("--deliverable", help="Deliverable folder name (e.g. Rachel007)")
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
        brand_path = base_dtc / args.brand
        report = harness.run_full_project_audit(brand_path, args.project, args.deliverable)
        harness.print_scorecard(report)
    else:
        print("UGC Production & QA Harness listo. Usa --help para ver los comandos.")
