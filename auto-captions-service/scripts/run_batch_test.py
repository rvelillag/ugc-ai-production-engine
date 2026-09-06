"""
Script para enviar lotes de videos al endpoint POST /caption y monitorear su progreso.
"""

import sys
import time
import httpx
from pathlib import Path

BASE_URL = "http://localhost:8000"

def submit_and_wait(video_path: Path, template: str = "hype_yellow"):
    print(f"\n[+] Enviando {video_path.name} con plantilla '{template}'...")
    with open(video_path, "rb") as f:
        files = {"file": (video_path.name, f, "video/mp4")}
        data = {"template": template, "language": "es", "auto_emoji": "true"}
        resp = httpx.post(f"{BASE_URL}/caption", data=data, files=files, timeout=30.0)

    if resp.status_code != 202:
        print(f"[-] Error enviando video: {resp.text}")
        return

    job_id = resp.json()["job_id"]
    print(f"[+] Job encolado: {job_id}. Esperando finalización...")

    for _ in range(60):
        status_resp = httpx.get(f"{BASE_URL}/caption/{job_id}", timeout=10.0)
        job_info = status_resp.json()
        status = job_info.get("status")
        progress = job_info.get("progress_percentage", 0)
        stage = job_info.get("stage", "")

        print(f"    - Estado: {status} ({progress}%) - {stage}")

        if status == "completed":
            print(f"[✓] Job completado! Output URL: {job_info.get('output_video_url')}")
            return job_info
        elif status == "failed":
            print(f"[X] Job falló: {job_info.get('error_message')}")
            return job_info

        time.sleep(2)

    print("[-] Timeout esperando job.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python run_batch_test.py <ruta_a_video1.mp4> [video2.mp4 ...]")
    else:
        for v in sys.argv[1:]:
            submit_and_wait(Path(v))
