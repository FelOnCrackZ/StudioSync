"""
StudioSync — Módulo de Validación y Registro de Archivos de Audio
Proceso central: valida, hashea y versiona archivos de audio en un proyecto.

ENTRADAS:
- file_data: dict con name, format, bpm_str, project_id, simulated_content
- project_repository: dict en memoria que simula la base de datos

SALIDAS:
- FileRecord (dict) con id, name, version, hash, bpm, format, project_id, timestamp, status
- Error descriptivo si alguna validación falla

PSEUDOCÓDIGO:
──────────────────────────────────────────────────────────
PROCESO registrar_archivo_de_audio(file_data, project_repository)

intentos ← 0
MIENTRAS intentos < MAX_INTENTOS:
    SI campos_completos(file_data) ENTONCES romper ciclo
    intentos ← intentos + 1
    SI intentos = MAX_INTENTOS ENTONCES retornar Error("Campos incompletos")

SI NOT formato_valido(file_data["format"]) ENTONCES
    retornar Error("Formato no soportado")

hash ← calcular_hash(file_data["simulated_content"])

SI hash_existe_en_proyecto(hash, project_repository, file_data["project_id"]) ENTONCES
    retornar Aviso("Archivo duplicado")

bpm ← parsear_bpm(file_data["bpm_str"])
SI NOT bpm_valido(bpm) ENTONCES retornar Error("BPM fuera de rango 40–300")

version ← calcular_nueva_version(project_repository, file_data["project_id"], file_data["name"])
record  ← crear_registro(file_data, hash, bpm, version)

guardar_en_repositorio(record, project_repository)
retornar record

FIN PROCESO
──────────────────────────────────────────────────────────
"""

import hashlib
import random
import string
from datetime import datetime

# ── Constantes ─────────────────────────────────────────────────────────────

FORMATOS_SOPORTADOS = [".wav", ".aiff", ".als", ".flp", ".ptx"]
MAX_INTENTOS = 3
BPM_MIN = 40
BPM_MAX = 300

# ── Utilidades ──────────────────────────────────────────────────────────────

def calcular_hash(contenido: str) -> str:
    """SHA-256 real usando la librería estándar de Python."""
    return hashlib.sha256(contenido.encode()).hexdigest()[:12]

def campos_completos(file_data: dict) -> bool:
    requeridos = ["name", "format", "bpm_str", "project_id", "simulated_content"]
    return all(file_data.get(k, "") != "" for k in requeridos)

def formato_valido(formato: str) -> bool:
    return formato.lower() in FORMATOS_SOPORTADOS

def parsear_bpm(bpm_str: str):
    try:
        return float(bpm_str)
    except (ValueError, TypeError):
        return None

def bpm_valido(bpm) -> bool:
    return bpm is not None and BPM_MIN <= bpm <= BPM_MAX

def hash_existe_en_proyecto(hash_val: str, repo: dict, project_id: str) -> bool:
    archivos = repo.get(project_id, [])
    return any(r["hash"] == hash_val for r in archivos)

def calcular_nueva_version(repo: dict, project_id: str, nombre: str) -> str:
    archivos = repo.get(project_id, [])
    mismo_nombre = [r for r in archivos if r["name"] == nombre]

    if not mismo_nombre:
        # Primer archivo con este nombre → nueva versión mayor
        max_major = max(
            (int(r["version"].lstrip("v").split(".")[0]) for r in archivos),
            default=0
        )
        return f"v{max_major + 1}.0"

    # Mismo nombre → incrementar minor
    ultima = mismo_nombre[-1]["version"].lstrip("v").split(".")
    major, minor = int(ultima[0]), int(ultima[1])
    return f"v{major}.{minor + 1}"

def generar_id() -> str:
    chars = random.choices(string.ascii_uppercase + string.digits, k=7)
    return "SS-" + "".join(chars)

# ── Proceso principal ───────────────────────────────────────────────────────

def registrar_archivo_de_audio(file_data: dict, project_repository: dict) -> dict:
    """
    Valida y registra un archivo de audio en StudioSync.
    Retorna un dict con: ok (bool), data, warning o error.
    """

    # ── Ciclo de validación de campos ──────────────────────────────────────
    intentos = 0
    while intentos < MAX_INTENTOS:
        if campos_completos(file_data):
            break
        intentos += 1
        if intentos == MAX_INTENTOS:
            return {
                "ok": False,
                "error": f"Campos incompletos tras {MAX_INTENTOS} intentos. "
                        f"Requeridos: name, format, bpm_str, project_id, simulated_content."
            }

    # ── Validación de formato ───────────────────────────────────────────────
    if not formato_valido(file_data["format"]):
        return {
            "ok": False,
            "error": f"Formato \"{file_data['format']}\" no soportado. "
                    f"Válidos: {', '.join(FORMATOS_SOPORTADOS)}"
        }

    # ── Hash de integridad ──────────────────────────────────────────────────
    hash_val = calcular_hash(file_data["simulated_content"])

    # ── Detección de duplicado ──────────────────────────────────────────────
    if hash_existe_en_proyecto(hash_val, project_repository, file_data["project_id"]):
        return {
            "ok": False,
            "warning": f"Archivo duplicado: ya existe un registro con hash {hash_val} "
                    f"en el proyecto \"{file_data['project_id']}\". No se registró."
        }

    # ── Validación de BPM ───────────────────────────────────────────────────
    bpm = parsear_bpm(file_data["bpm_str"])
    if not bpm_valido(bpm):
        return {
            "ok": False,
            "error": f"BPM inválido: \"{file_data['bpm_str']}\". "
                    f"Debe ser un número entre {BPM_MIN} y {BPM_MAX}."
        }

    # ── Versionado y registro ───────────────────────────────────────────────
    version = calcular_nueva_version(project_repository, file_data["project_id"], file_data["name"])

    record = {
        "id":         generar_id(),
        "name":       file_data["name"],
        "format":     file_data["format"],
        "bpm":        bpm,
        "version":    version,
        "hash":       hash_val,
        "project_id": file_data["project_id"],
        "timestamp":  datetime.now().isoformat(),
        "status":     "ok"
    }

    project_repository.setdefault(file_data["project_id"], []).append(record)
    return {"ok": True, "data": record}


# ── Tests ───────────────────────────────────────────────────────────────────

def log(titulo: str, resultado: dict):
    print(f"\n{'─' * 60}")
    print(f"🎵 {titulo}")
    if resultado.get("ok"):
        d = resultado["data"]
        print(f"✅ ÉXITO:")
        print(f"   ID:      {d['id']}")
        print(f"   Archivo: {d['name']}{d['format']}")
        print(f"   Versión: {d['version']}")
        print(f"   BPM:     {d['bpm']}")
        print(f"   Hash:    {d['hash']}")
        print(f"   Proyecto:{d['project_id']}")
    elif "warning" in resultado:
        print(f"⚠️  AVISO: {resultado['warning']}")
    else:
        print(f"❌ ERROR: {resultado['error']}")


if __name__ == "__main__":

    repo = {}  # Repositorio compartido (simula la base de datos)

    # Test 1 — Registro exitoso
    log("Test 1 — Primer registro exitoso",
        registrar_archivo_de_audio(
            {"name": "Verse_lead", "format": ".wav", "bpm_str": "140",
            "project_id": "PROJ-001", "simulated_content": "abc123contenidoOriginal"},
            repo
        ))

    # Test 2 — Segunda versión del mismo archivo (v1.1)
    log("Test 2 — Segunda versión del mismo archivo (v1.1)",
        registrar_archivo_de_audio(
            {"name": "Verse_lead", "format": ".wav", "bpm_str": "140",
            "project_id": "PROJ-001", "simulated_content": "abc123contenidoV2distinto"},
            repo
        ))

    # Test 3 — Nombre nuevo → versión mayor (v2.0)
    log("Test 3 — Nuevo archivo, versión mayor (v2.0)",
        registrar_archivo_de_audio(
            {"name": "Chorus_bass", "format": ".aiff", "bpm_str": "140",
            "project_id": "PROJ-001", "simulated_content": "xyzBaseDrum999"},
            repo
        ))

    # Test 4 — Duplicado (mismo contenido que Test 1)
    log("Test 4 — Intento de duplicado (mismo hash)",
        registrar_archivo_de_audio(
            {"name": "Verse_lead_copy", "format": ".wav", "bpm_str": "140",
            "project_id": "PROJ-001", "simulated_content": "abc123contenidoOriginal"},
            repo
        ))

    # Test 5 — Formato inválido
    log("Test 5 — Formato no soportado (.mp3)",
        registrar_archivo_de_audio(
            {"name": "Bounce_final", "format": ".mp3", "bpm_str": "128",
            "project_id": "PROJ-001", "simulated_content": "mp3contenido"},
            repo
        ))

    # Test 6 — BPM fuera de rango
    log("Test 6 — BPM fuera de rango (500)",
        registrar_archivo_de_audio(
            {"name": "Drop_kick", "format": ".wav", "bpm_str": "500",
            "project_id": "PROJ-001", "simulated_content": "kickDrum888"},
            repo
        ))

    # Test 7 — Campo vacío
    log("Test 7 — Campos incompletos (sin BPM)",
        registrar_archivo_de_audio(
            {"name": "Hook_synth", "format": ".wav", "bpm_str": "",
            "project_id": "PROJ-001", "simulated_content": "hookSynth"},
            repo
        ))

    # Test 8 — Mismo contenido, proyecto distinto → debe aceptarse
    log("Test 8 — Mismo archivo en proyecto distinto (debe aceptarse)",
        registrar_archivo_de_audio(
            {"name": "Verse_lead", "format": ".wav", "bpm_str": "140",
            "project_id": "PROJ-002", "simulated_content": "abc123contenidoOriginal"},
            repo
        ))

    # Estado final del repositorio
    print(f"\n{'═' * 60}")
    print("📦 Estado final del repositorio StudioSync:")
    for proj, archivos in repo.items():
        print(f"\n  Proyecto: {proj} ({len(archivos)} archivo(s))")
        for r in archivos:
            print(f"    • [{r['version']}] {r['name']}{r['format']} | BPM:{r['bpm']} | hash:{r['hash']} | id:{r['id']}")
