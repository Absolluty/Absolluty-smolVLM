## 📦 Dependencia externa: llama.cpp

Este proyecto requiere [`llama.cpp`](https://github.com/ggerganov/llama.cpp) como dependencia para funcionar, pero **no se incluye directamente en este repositorio**.

> 🔧 **Para compilar y configurar `llama.cpp`, seguí las instrucciones detalladas en su repositorio oficial:**  
> 👉 [https://github.com/ggerganov/llama.cpp](https://github.com/ggerganov/llama.cpp)

Podés ubicar `llama.cpp` en la misma carpeta raíz que este proyecto, o ajustar los paths en tu entorno si lo colocás en otra ubicación.

### 📁 Estructura sugerida

```text
/
├── Absolluty-smolVLM/
├── llama.cpp/



## 🚀 Cómo usar este proyecto

Este proyecto permite analizar una imagen con una persona y extraer una descripción estructurada de sus atributos visuales (ropa, edad, género, accesorios, etc.) utilizando el modelo visual `smolVLM`.

### 📌 Pasos para ejecutar

1. **Iniciar el servidor de llama.cpp**

   Asegurate de tener compilado `llama.cpp` y ejecutá el servidor:

   ```bash
   ./llama-server -hf ggml-org/SmolVLM-500M-Instruct-GGUF
