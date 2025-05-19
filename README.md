## 🚀 Cómo usar este proyecto

Este proyecto permite analizar una imagen con una persona y extraer una descripción estructurada de sus atributos visuales (ropa, edad, género, accesorios, etc.) utilizando el modelo visual `SmolVLM`.

---

### 📦 Requisitos

- Python 3.8+
- llama.cpp compilado (ver instrucciones en su [repositorio oficial](https://github.com/ggerganov/llama.cpp))
- Modelo `GGUF` compatible (ver más abajo)

---

### 🧠 Modelos compatibles

Podés usar cualquiera de estos dos modelos con `llama-server`:

```bash
# ✅ Recomendado (rápido y liviano)
.\build\bin\Release\llama-server.exe -hf ggml-org/SmolVLM-500M-Instruct-GGUF

# ⚠️ Más preciso pero pesado (2.2B)
.\build\bin\Release\llama-server.exe -hf ggml-org/SmolVLM2-2.2B-Instruct-GGUF

