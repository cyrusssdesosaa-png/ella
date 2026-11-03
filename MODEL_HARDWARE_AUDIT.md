# Ella Local Model Inventory & Hardware Compatibility Audit

**Audit date:** 2026-11-04
**Scope:** Read-only inspection of this Windows PC, the already-running local Ollama service, and local Ollama model metadata.
**No inference or benchmark was run.** Ella was not started. Ollama was already listening; it was not started or stopped. No configuration, source code, environment file, or runtime data was modified. No model was downloaded, installed, removed, or changed.

## Executive recommendation

- **Best currently installed text model for capability:** `qwen2.5:7b` (Q4_K_M), with a short context and after reducing competing memory/GPU pressure. It is the strongest installed general/coding assistant model by size and published model-family strengths, but is not the safest always-on choice under this snapshot's low available system RAM.
- **Best everyday model and recommended Local default:** `llama3.2:3b` (Q4_K_M), start at **4,096 context tokens**. Its stored weights are substantially smaller and should leave more room for Windows, the UI, and other local tasks. This is a hardware-fit recommendation, not a measured quality or speed result.
- **Vision model:** `moondream:latest` is locally present and `ollama show` resolves it, but it is not a general-purpose chat/coding model. It should be treated as an on-demand vision specialist, not loaded alongside another model unless resource behavior is verified.
- **Upgrade:** no immediate upgrade is justified. The installed Qwen 7B already offers a higher-capability option, while RAM availability is currently constrained. A later, optional `qwen3:4b` evaluation could be interesting; a Qwen 3 8B-class model is a VRAM-tight stretch on this PC. Nothing was downloaded.

## 1. Verified hardware inventory

| Component | Read-only result | Notes |
|---|---|---|
| CPU | AMD Ryzen 5 5600G with Radeon Graphics; **6 cores / 12 logical processors** | Matches the project-owner specification. |
| Physical memory | **16.64 million KiB visible** (about 15.87 GiB, marketed as 16 GB); **1,658 MiB available** at the sample; Win32 free-physical counter was about **1,469 MiB** | This is the main present constraint. Available memory changes over time. Do not infer the model's peak memory use from this idle snapshot. |
| GPU | NVIDIA GeForce RTX 3050 | Verified by `nvidia-smi`. |
| Dedicated GPU memory | **8,192 MiB total**; approximately **2,020 MiB in use / 6,172 MiB free** in the detailed sample | A separate earlier query measured about 5,971 MiB free; allocation varies. Ollama had no model loaded in `ollama ps`. GPU utilization was 42% and temperature 52°C in the detailed sample, so the GPU was not idle. |
| NVIDIA driver | **616.92** | `nvidia-smi` driver and KMD versions matched. |
| CUDA | NVIDIA driver reported **CUDA UMD 13.4**; GPU compute capability **8.6**. `nvcc` was not found on PATH. | This verifies driver-side CUDA compatibility reporting, not a separately installed CUDA Toolkit. Ollama can use its packaged/runtime backend; no inference was tested. |
| Ollama model storage | `D:\AIStoryStudio\ollama-models` | Discovered from the current `OLLAMA_MODELS` process environment; only the path was read. |
| Storage volume | D: NTFS, about **931.5 GiB total / 157.73 GiB free** | Consistent with a marketed 1 TB volume. |

**Important resource observation:** the machine had only about 1.6 GiB of available system RAM while desktop applications were active. The 8 GB GPU also had roughly 2 GB already allocated and showed 42% utilization. Therefore, a model that fits its weight file on the GPU may still cause memory pressure once context/KV cache, inference buffers, Whisper, and ordinary applications are considered.

## 2. Installed local model inventory

`ollama list` reported two models. The Ollama model directory also contains a `moondream:latest` manifest, and `ollama show moondream:latest` succeeded; however, moondream was absent from the `ollama list` output. Treat that list/manifest discrepancy as a registry/inventory inconsistency to resolve later, not proof of a usable vision run. No model was resident according to `ollama ps` at the inspection time.

Stored layer totals below are filesystem sizes read from local manifests and blobs; Ollama's human-readable sizes are included as shown by `ollama list` or the official library. **Neither number is peak inference VRAM.**

| Model/tag | Ollama metadata | Stored size | Intended role / finding |
|---|---|---:|---|
| `qwen2.5:7b` | Architecture `qwen2`; **7.6156B parameters**; **32,768** context in this installed model; embedding 3,584; **Q4_K_M**; completion and tools capabilities. | Ollama list: **4.7 GB**; local model layers: **4.36 GiB**. | Best capability candidate among installed general text models; coding, math, structured output and instruction following are strengths described by Qwen's model documentation. Higher resource demand; not advisable at a very long context on this machine. |
| `llama3.2:3b` | Architecture `llama`; **3.2127B parameters**; **131,072** context metadata; embedding 3,072; **Q4_K_M**; completion and tools capabilities. | Ollama list: **2.0 GB**; local model layers: **1.88 GiB**. | Best everyday fit among installed general text models. Smaller weights and adequate assistant/summarization/tool-use role; complex reasoning and coding depth are expected to trail the 7B model. |
| `moondream:latest` | Architecture `phi2`; **1B** language parameters plus a **454.45M** CLIP vision projector; context **2,048**; embedding 2,048; **Q4_0**; completion and vision capabilities. | Local model layers: **1.62 GiB**. | Vision specialist, not a strong general assistant. Use on demand and avoid concurrent loading with chat/Whisper until memory behavior is measured. `ollama show` resolves it, despite omission from `ollama list`. |

The Qwen 2.5 family page advertises broader maximum context for the family, but the **installed tag's local metadata says 32,768**; this report uses the installed model's metadata. A model's maximum context is not a recommendation to allocate that much on this PC.

## 3. Compatibility analysis

### `llama3.2:3b`

- At 1.88 GiB stored quantized layers, it has the most comfortable GPU footprint of the installed text LLMs. Actual runtime use will be higher due to cache and working buffers, but a **full-GPU load at a 4K context is the most plausible starting target** among these models.
- It also reduces host-memory pressure compared with Qwen 7B, important given only about 1.6 GiB was available at the snapshot.
- Ollama metadata advertises a very large context limit, but Ella's current code uses 4,096 context. Keep that modest limit; a large context can raise KV-cache and RAM/VRAM usage substantially.
- Likely the most reliable continuous model for chat and routines on the observed machine. No measured latency or output-quality benchmark was performed.

### `qwen2.5:7b`

- Its 4.36 GiB layer files are a significant fraction of the 8 GiB VRAM. With about 6 GiB free in the sample, a full-GPU load may be possible at a modest context **when the GPU remains similarly available**, but runtime buffers and KV cache consume additional memory. This cannot be guaranteed from file size alone.
- With 32K context metadata, using the full context could materially increase memory demand. Start at 4K if evaluating it later; raise context only after monitoring VRAM and system memory.
- If GPU memory is insufficient, Ollama may offload layers, but CPU offload can increase RAM pressure and reduce responsiveness. Given the low available RAM snapshot, freeing system memory and GPU allocations is preferable to assuming partial offload will be harmless.
- Best for more demanding coding, technical explanations and multi-step problem solving of the installed text models, but likely less comfortable for always-on use than the 3B option.

### `moondream:latest`

- Smaller vision model, but still uses separate vision-projector weights and a working context. Vision requests can add memory beyond the language model's stored layers.
- Do not assume it can coexist with Qwen 7B plus Whisper inside 8 GB VRAM. An on-demand model swap/queue is the safer future design.
- It has only 2,048 context metadata and should be selected for image understanding, not general conversation/code assistance.

### Context and model concurrency

A model's advertised maximum context does not equal a safe context for this PC. KV cache scales with context and inference settings. For any future manual validation, begin at 4K context, measure available VRAM/RAM, run one large model at a time, and avoid concurrent vision/Whisper GPU loads. This audit intentionally did not load models to measure those figures.

## 4. Ranked recommendations

The ranking is qualitative, based on installed metadata, model size, vendor-published model-family descriptions, and the measured hardware snapshot. No local benchmark or prompt evaluation was done.

| Rank | Model | Recommended use | Trade-off |
|---:|---|---|---|
| 1 | `qwen2.5:7b` | Best installed general text model when quality is prioritized and resource headroom is available. | Better expected coding/reasoning depth, but its larger footprint is a poor match for current low free RAM and shared GPU headroom. |
| 2 | `llama3.2:3b` | Everyday chat, concise assistance, summarization and routines; recommended default. | More modest reasoning/coding capability than the 7B model, but smaller resource cost should improve continuous-use reliability. |
| Specialist | `moondream:latest` | On-demand image/vision analysis only. | Not a general assistant, short context, and model inventory list discrepancy. |

## 5. Three model recommendations

### A. Best currently installed model

**`qwen2.5:7b` Q4_K_M**, conditionally: strongest practical installed general text model for quality-oriented work, but use a 4K context and only when resource headroom is available. Under the measured 1.6 GiB available system RAM, it is not the best continuously loaded choice today.

### B. Best everyday model

**`llama3.2:3b` Q4_K_M.** Its 2.0 GB Ollama package / 1.88 GiB local layer size is much smaller than the 7B option. It is a reasonable always-available balance for the existing assistant workload, especially chat, summaries and simple routine/tool-oriented instructions. Expect weaker performance on difficult code/reasoning tasks; no speed claim is made.

### C. Best future upgrade candidates (not installed)

1. **`qwen3:4b` Q4_K_M — cautious future evaluation.** The official Ollama library currently lists about **2.5 GB** and 4.02B parameters. This offers a newer small-model family and remains much closer to the 3B footprint than the 8B class. Its actual context/KV and performance must be checked after installation; no upgrade is needed before addressing current RAM pressure.
2. **`qwen3:8b` Q4_K_M — quality-oriented stretch option.** The official Ollama library lists about **5.2 GB** and 8.19B parameters. That leaves little gross capacity on an 8 GB card, especially with about 2 GB already in use at this snapshot; context cache/working buffers may require partial CPU/GPU offload and could compete with 16 GB system RAM. Consider only if there is measured free memory, other GPU workloads are closed, and a short-context test is approved.

These are suggestions only. No download, pull, install, or configuration change was made. Published family claims are not a benchmark of Ella or this PC.

## 6. Recommended Ella Local default

**Recommendation: `llama3.2:3b`, Q4_K_M, with a 4,096-token starting context.**

Why:

- It is already installed and its quantized files occupy about 1.88 GiB on disk, versus 4.36 GiB for Qwen 7B.
- It should be the easiest installed general model to keep resident while leaving headroom for Windows, Ella's interface, and local voice components.
- It lowers the risk of GPU exhaustion or RAM pressure on the observed 16 GB machine with only about 1.6 GiB currently available.
- A 4K context is a conservative starting point and is consistent with Ella's present server-side `num_ctx` setting; the model's 131K metadata context should not be treated as a target.

**Placement:** aim for full-GPU placement for this 3B quantized model if Ollama reports that it can do so. Do not force GPU layers or alter configuration as part of this audit. If VRAM is tight, first unload competing models/reduce concurrent GPU use and keep context modest. CPU/partial offload is a fallback to assess manually, not the default recommendation given limited available RAM. Serialize Whisper/vision/model use where possible.

**Strengths:** small relative footprint, suitable general conversation/summarization and tool-oriented workflows.
**Weaknesses:** less capable than the 7B Qwen option for difficult reasoning, coding and instruction-heavy tasks; exact quality and speed are unmeasured.

This is a recommendation only. The active runtime model setting was not changed.

## 7. Limitations and unverified information

- Hardware readings are point-in-time. Available RAM, GPU utilization and VRAM use vary with running applications.
- `ollama ps` was empty at inspection, so no inference placement, active context allocation or GPU offload behavior was verified.
- `ollama show` metadata and quantization describe model packages, not complete runtime requirements. Disk layer size is not equal to VRAM use.
- No inference, speed/quality benchmark, voice/STT test, Ollama model launch, Ella launch or application test was performed.
- `ollama list` showed two models while the local directory contained a moondream manifest and `ollama show moondream:latest` succeeded. The discrepancy was not repaired or investigated destructively.
- CUDA Toolkit compiler `nvcc` was not found on PATH; driver CUDA reporting is not proof of a particular Ollama backend or library configuration.
- Windows memory counters reported different free/available figures by definition and sample; both are included to convey pressure, not a stable capacity guarantee.
- Only installed models and metadata were audited. Suggested future tags are not installed and their compatibility is an estimate based on official package sizes plus this system snapshot.

## 8. Sources and read-only commands

### Local inspection commands used

- `Get-CimInstance Win32_Processor` — processor name/core/thread counts.
- `Get-CimInstance Win32_OperatingSystem` and `Win32_PerfFormattedData_PerfOS_Memory` — total/free/available RAM.
- `Get-CimInstance Win32_VideoController`, `nvidia-smi`, and `nvidia-smi --query-gpu=name,memory.total,memory.free,driver_version --format=csv` — GPU, driver, memory and runtime snapshot.
- `nvidia-smi --query-gpu=compute_cap --format=csv` — compute capability.
- `Get-CimInstance Win32_LogicalDisk` and read-only inspection of `OLLAMA_MODELS` manifests/blob file sizes — model volume and local model file footprint.
- `Test-NetConnection 127.0.0.1 -Port 11434` — determine whether Ollama was already listening before querying it.
- `ollama list`, `ollama ps`, `ollama show qwen2.5:7b --verbose`, `ollama show llama3.2:3b --verbose`, and `ollama show moondream:latest` — installed tags, loaded status and model metadata. No `ollama run` or generation endpoint was called.
- Checked `nvcc` availability; it was not present on PATH.

### Public model references

Accessed 2026-11-04; official Ollama model library pages:

- [Qwen2.5 7B](https://ollama.com/library/qwen2.5:7b) — package size, quantization and Qwen2.5 family capabilities.
- [Llama 3.2 3B](https://ollama.com/library/llama3.2:3b) — package size and intended dialogue/summarization/tool-use cases.
- [Qwen3 4B](https://ollama.com/library/qwen3:4b) — suggested, not-installed future candidate and package size.
- [Qwen3 8B](https://ollama.com/library/qwen3:8b) — suggested, not-installed future candidate and package size.

## Final status

Hardware specifications were verified; Ollama was already running and reported two listed models plus a separately resolvable local moondream tag. The strongest installed general model is `qwen2.5:7b`; the best everyday fit and recommended Ella Local default is `llama3.2:3b` at a conservative 4K context. An upgrade is not urgent. No configuration was changed; wait for Cyrus to review and approve before changing Ella's default.
