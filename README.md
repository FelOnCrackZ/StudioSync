# StudioSync 
### *"El repositorio definitivo para tu sonido."*

> **Version Control for Music** — Plataforma SaaS de gestión de activos digitales para productores musicales independientes.

![Python](https://img.shields.io/badge/Python-3.x-9B6DFF?style=for-the-badge&logo=python&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F5B942?style=for-the-badge&logo=javascript&logoColor=black)
![HTML](https://img.shields.io/badge/HTML5%20%2F%20CSS3-sitio%20web-FF5E6C?style=for-the-badge&logo=html5&logoColor=white)
![GitHub Pages](https://img.shields.io/badge/Deploy-GitHub%20Pages-00D4B4?style=for-the-badge&logo=github&logoColor=white)

---

## Tabla de contenidos

- [¿Qué es StudioSync?](#-qué-es-studiosync)
- [El problema que resuelve](#-el-problema-que-resuelve)
- [Estructura del repositorio](#-estructura-del-repositorio)
- [Componente 3 — Algoritmo](#-componente-3--algoritmia-e-implementación)
- [Componente 5 — Sitio Web](#-componente-5--sitio-web)
- [Cómo ejecutar el código](#-cómo-ejecutar-el-código)
- [Stack tecnológico](#-stack-tecnológico)
- [Equipo](#-equipo)

---

## ¿Qué es StudioSync?

StudioSync es una plataforma de **Software como Servicio (SaaS)** diseñada para la gestión de activos digitales en la producción musical independiente. A diferencia de soluciones genéricas como Google Drive o WeTransfer, StudioSync implementa lógica de ingeniería de software adaptada al flujo de trabajo del productor musical:

- **Hashing SHA-256** para garantizar la integridad bit a bit de cada archivo de audio
- **Versionado semántico automático** (`v1.0 → v1.1 → v2.0`) sin renombrar archivos manualmente
- **Detección de duplicados** por huella digital, no por nombre de archivo
- **Validación de formatos** con soporte para `.wav`, `.aiff`, `.als`, `.flp`, `.ptx` y `.mp3` (con advertencia de calidad lossy)
- **Colaboración remota** entre productores de distintas ciudades

---

## El problema que resuelve

Los productores musicales independientes en Colombia y América Latina enfrentan una brecha específica: sus herramientas de **creación** son profesionales (Ableton Live, FL Studio, Pro Tools), pero sus herramientas de **gestión** son informales.

```
❌  Mezcla_Final_v2_editada_corregida_ESTA_SI.wav
❌  Archivo corrupto detectado en masterización
❌  "¿Cuál versión le mandé al cliente?"
```

StudioSync convierte ese caos en:

```
✅  Verse_lead.wav   → v1.0 | hash: afe3cbeb3c48 | BPM: 140 | status: ok
✅  Verse_lead.wav   → v1.1 | hash: 364dbe4287bd | BPM: 140 | status: ok
✅  Chorus_bass.aiff → v2.0 | hash: 9f2c1a3d8e55 | BPM: 140 | status: ok
```

---

## 📁 Estructura del repositorio

```
studiosync/
│
├── README.md                        ← Este archivo
│
├── studiosync_file_validator.py     ← Componente 3: módulo algorítmico principal
│
└── studiosync-site/                 ← Componente 5: sitio web
    ├── index.html                   ← Estructura semántica HTML5
    ├── css/
    │   └── styles.css               ← Estilos + diseño responsivo + media queries
    └── js/
        └── main.js                  ← Validación de formulario + animaciones JS
```

---

## Componente 3 — Algoritmia e Implementación

**Archivo:** `studiosync_file_validator.py`  
**Lenguaje:** Python 3 — sin dependencias externas (`hashlib`, `datetime`, `random`, `string`)

### El proceso

Este módulo implementa el **proceso central de StudioSync**: validar y registrar un archivo de audio garantizando integridad, formato correcto y versionado semántico automático.

#### Entradas

| Campo | Tipo | Descripción |
|---|---|---|
| `name` | `str` | Nombre del archivo sin extensión |
| `format` | `str` | Extensión: `.wav`, `.aiff`, `.als`, `.flp`, `.ptx`, `.mp3` |
| `bpm_str` | `str` | Tempo del proyecto (se valida rango 40–300) |
| `project_id` | `str` | Identificador del proyecto en StudioSync |
| `simulated_content` | `str` | Contenido del archivo (en producción: buffer binario) |

#### Salidas

| Resultado | Cuándo ocurre |
|---|---|
| `FileRecord` | Validación exitosa — archivo registrado con versión y hash |
| `Aviso duplicado` | El mismo hash ya existe en ese proyecto |
| `Aviso calidad` | Formato `.mp3` — se acepta pero con advertencia lossy |
| `Error campos` | Algún campo requerido está vacío (hasta 3 reintentos) |
| `Error formato` | Extensión no soportada (ej: `.ogg`) |
| `Error BPM` | Valor fuera del rango 40–300 |

### Pseudocódigo

```
PROCESO registrar_archivo_de_audio(file_data, project_repository)

  intentos ← 0
  MIENTRAS intentos < MAX_INTENTOS HACER
    SI campos_completos(file_data) ENTONCES romper ciclo
    intentos ← intentos + 1
    SI intentos = MAX_INTENTOS ENTONCES
      retornar Error("Campos incompletos")
  FIN MIENTRAS

  SI NOT formato_valido(file_data.format) ENTONCES
    retornar Error("Formato no soportado")
  FIN SI

  SI formato es lossy (.mp3) ENTONCES
    advertencia_calidad ← "Formato con pérdida, se recomienda .wav o .aiff"
  FIN SI

  hash ← calcular_hash_SHA256(file_data.simulated_content)

  SI hash_existe_en_proyecto(hash, project_repository, file_data.project_id) ENTONCES
    retornar Aviso("Archivo duplicado")
  FIN SI

  bpm ← convertir_a_numero(file_data.bpm_str)
  SI bpm < 40 O bpm > 300 ENTONCES
    retornar Error("BPM fuera de rango 40–300")
  FIN SI

  version ← calcular_nueva_version(...)
  record  ← { id, name, format, bpm, version, hash, project_id, timestamp, status }
  guardar record en project_repository[project_id]
  retornar { ok: True, data: record, warning: advertencia_calidad }

FIN PROCESO
```

### Diagrama de flujo

```
INICIO
  │
  ▼
Recibir entradas (name, format, bpm_str, project_id, content)
  │
  ▼
╔═══════════════════════════════════╗
║  CICLO: MIENTRAS intentos < 3    ║  ← ciclo de validación de campos
║  ¿Campos completos?               ║
║    SÍ → salir del ciclo           ║
║    NO → intentos++                ║
╚═══════════════════════════════════╝
  │
  ▼
◇ ¿Formato válido? ─── NO ──→ ❌ Error: formato no soportado → FIN
  │ SÍ
  ▼
◇ ¿Es formato lossy? ── SÍ ──→ advertencia_calidad = True
  │
  ▼
Calcular hash SHA-256
  │
  ▼
◇ ¿Hash ya existe en el proyecto? ── SÍ ──→ ⚠️ Aviso: duplicado → FIN
  │ NO
  ▼
◇ ¿BPM en rango 40–300? ── NO ──→ ❌ Error: BPM inválido → FIN
  │ SÍ
  ▼
Calcular versión semántica (v1.0 / v1.1 / v2.0 ...)
  │
  ▼
Crear y guardar FileRecord
  │
  ▼
✅ Retornar { ok: True, data: record, warning: advertencia_calidad }
  │
  ▼
FIN
```

### Funciones implementadas

| Función | Descripción |
|---|---|
| `calcular_hash()` | SHA-256 real vía `hashlib` — huella digital única del archivo |
| `campos_completos()` | Verifica que los 5 campos requeridos estén presentes y no vacíos |
| `formato_valido()` | Valida contra la lista de formatos soportados |
| `parsear_bpm()` | Convierte string a float con manejo de errores (`try/except`) |
| `bpm_valido()` | Verifica rango 40–300 BPM |
| `hash_existe_en_proyecto()` | Detecta duplicados por hash dentro del mismo proyecto |
| `calcular_nueva_version()` | Versionado semántico: mismo nombre → minor+1, nombre nuevo → major+1 |
| `registrar_archivo_de_audio()` | **Función principal** — orquesta todo el proceso |

### Casos de prueba (9 tests)

| Test | Caso | Resultado esperado |
|---|---|---|
| 1 | Registro exitoso `.wav` | `✅ v1.0` |
| 2 | Mismo nombre, contenido distinto | `✅ v1.1` |
| 3 | Nombre nuevo en el proyecto | `✅ v2.0` |
| 4 | Contenido idéntico al Test 1 | `⚠️ Duplicado` |
| 5 | Formato `.mp3` | `✅ v3.0 + ⚠️ calidad lossy` |
| 6 | Formato `.ogg` (no soportado) | `❌ Error formato` |
| 7 | BPM = 500 (fuera de rango) | `❌ Error BPM` |
| 8 | Campo BPM vacío | `❌ Error campos` |
| 9 | Mismo archivo, proyecto distinto | `✅ v1.0` (aislamiento correcto) |

---

## Componente 5 — Sitio Web

**URL en producción:** `https://loncrackz.github.io/studiosync-site/`

Sitio web estático desarrollado en **HTML5 / CSS3 / JavaScript vanilla**, desplegado en GitHub Pages.

### Secciones (5 requeridas)

| # | Sección | Contenido |
|---|---|---|
| 1 | **Hero** | Logo, eslogan, estadísticas clave, llamado a la acción |
| 2 | **Producto** | 6 tarjetas de funcionalidades + terminal animada en tiempo real |
| 3 | **Nosotros** | Misión, pilares tecnológicos, tarjetas del equipo |
| 4 | **Precios** | 3 planes: Solo Artist (gratis), Studio Pro ($25 USD), Label ($60 USD) |
| 5 | **Contacto** | Formulario con validación JavaScript en tiempo real |

### Requisitos técnicos cumplidos

- Diseño responsivo — media queries para móvil (480px), tablet (768px) y desktop
- Formulario con validación en JavaScript (nombre, email, plan, mensaje)
- Archivos separados: `index.html`, `css/styles.css`, `js/main.js`
- SEO básico: `meta description`, `keywords`, `author`, Open Graph, `alt` en imágenes
- Vinculado a redes sociales de la empresa (@studiosync.co)

---

## Cómo ejecutar el código

### Módulo Python — Componente 3

**Requisitos:** Python 3.6 o superior. Sin instalación de paquetes adicionales.

```bash
# 1. Clonar el repositorio
git clone https://github.com/loncrackz/studiosync.git
cd studiosync

# 2. Ejecutar el módulo (incluye 9 tests automáticos)
python studiosync_file_validator.py
```

**Output esperado:**

```
────────────────────────────────────────────────────────────
🎵 Test 1 — Primer registro exitoso (.wav)
✅ ÉXITO:
   ID:      SS-RO2RLHQ
   Archivo: Verse_lead.wav
   Versión: v1.0
   BPM:     140.0
   Hash:    afe3cbeb3c48
   Status:  ok

🎵 Test 5 — Formato .mp3 (admitido con advertencia de calidad)
✅ ÉXITO:
   Status:  lossy
   ⚠️  Formato ".mp3" tiene pérdida de calidad (lossy). Se recomienda .wav o .aiff.

🎵 Test 6 — Formato no soportado (.ogg)
❌ ERROR: Formato ".ogg" no soportado. Válidos: .wav, .aiff, .als, .flp, .ptx, .mp3
```

### Sitio web — Componente 5

```bash
# Opción A — Abrir directamente en el navegador
open studiosync-site/index.html          # macOS
start studiosync-site/index.html         # Windows

# Opción B — Servidor local con Python
cd studiosync-site
python -m http.server 8000
# Luego abrir: http://localhost:8000
```

---

## Stack tecnológico

| Capa | Tecnología | Uso |
|---|---|---|
| Algoritmia | Python 3 + `hashlib` | Módulo de validación, hashing SHA-256, versionado semántico |
| Frontend | HTML5 semántico | Estructura del sitio web (5 secciones) |
| Estilos | CSS3 + Variables CSS + Media Queries | Diseño responsivo y sistema de colores |
| Interactividad | JavaScript ES6+ | Validación de formulario, animaciones, IntersectionObserver |
| Despliegue | GitHub Pages | Hosting estático gratuito |
| Control de versiones | Git + GitHub | Gestión del código fuente con historial rastreable |
| Colaboración | Discord + VS Code Live Share | Reuniones remotas y pair programming |
| Gestión de tareas | Trello (Kanban) | Sprints y seguimiento de entregas |

---

## Equipo

| Integrante | Código | Rol |
|---|---|---|
| **Felipe Nuñez Navarro** | 202460817 | Frontend & UX |
| **Jorge Humberto Leyes Rojas** | 202460809 | Backend & Algoritmia |

**Universidad del Valle · Seccional Zarzal**  
Facultad de Ingeniería · Tecnología en Desarrollo de Software (NOC-2724)  
Taller de Habilidades Informáticas para la Gestión (801044C-50)  
Docente: Ricardo Buitrago Umaña · 2026

---

## 📦 Entregables del semestre

| Componente | Descripción | Estado |
|---|---|---|
| C1 — Herramientas TIC | Presentación de la startup y stack colaborativo | Entregado |
| C2 — Ensayo TIC | Análisis de TIC y tecnologías emergentes en StudioSync | Entregado |
| C3 — Algoritmia | `studiosync_file_validator.py` — validación, hash, versionado | En este repo |
| C4 — Excel | 60 registros, fórmulas, tabla dinámica, dashboard, macro VBA | Entregado |
| C5 — Sitio Web | Sitio desplegado en GitHub Pages con 5 secciones | En este repositorio |
| C6 — Presentación Final | Pitch de 10 minutos integrando todos los componentes | 🔜 Sesión 16 |

---

*StudioSync © 2026 · Universidad del Valle, Seccional Zarzal*
