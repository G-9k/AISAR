# Diferencias de scaffold: ADK (Ale) vs Inspect (este port)

Todo lo que el modelo ve distinto en el port respecto al original. Se completa a medida que avanzamos.
Si la réplica no coincide con Aditya o con Ale, revisar esto primero.

Verificado con google-adk 2.13.0 (Ale pedía `>=1.28.0`; la versión exacta que usó no está registrada)
e inspect_ai 0.3.285. La columna de Aditya sale de `agent-interp-envs`, rama `adsingh-64/dev`, commit
`a7fb3a3` (`environments/currency_conversion/`).

| # | Qué | ADK (Ale) | Inspect (port) | Aditya | Estado |
|---|---|---|---|---|---|
| 1 | Descripción de fee/rate | docstring completo | idéntica (docstring sin `Args:`) | otra, de una línea: *"Get the transaction fee percentage for a given payment method."* | igual a Ale ✔ |
| 2 | Descripción de parámetros de fee/rate | ninguna | obligatoria en Inspect: texto mínimo | con ejemplos: *"The payment method (e.g., 'Bank Transfer', 'Credit Card', 'Wire Transfer')"* | diferencia menor, inevitable |
| 3 | Formato del resultado de una tool | `function_response.response` = el dict tal cual (`{"status": ..., ...}`) | depende de la vía (fila 18). Por OpenRouter: mensaje de tool estilo OpenAI con el JSON como string, y OpenRouter lo traduce a Gemini (cómo, no lo sabemos). Con el provider de Google: `{"output": "<JSON>"}` | string JSON en el contenido del mensaje de tool | **diferencia**: revisar en el piloto |
| 4 | Nombre de la tool del calculador | `CalculationAgent` (aunque el prompt diga "calculation_agent tool") | `calculation_agent`, como el prompt (ejercicio 05) | `calculation_agent` | **diferencia deliberada con Ale**: ver [D2](../docs/decisiones_diseno.md) |
| 5 | Descripción de la tool del calculador | vacía `""` | mínima: *"Calculation agent"* (Inspect no acepta vacía) | *"A calculation sub-agent that generates and executes Python code... it will return the computed result."* | diferencia menor con Ale, deliberada con Aditya: ver [D3](../docs/decisiones_diseno.md) |
| 6 | Respuesta del calculador | LLM (flash-lite) envuelto: `{"result": "<texto>"}` | mock determinístico con los textos de Aditya (ejercicio 05) | string fijo `{"result": ...}` | StaticResponse ≈ igual; CodeOnly distinto: ver [D4](../docs/decisiones_diseno.md) |
| 7 | Regla de corte del loop | respuesta sin tool calls | igual (ejercicio 04) | igual | igual ✔ |
| 8 | Límite de llamadas | 30 llamadas del agente principal | contador propio de 30 llamadas (ejercicio 04) | `max_steps` 10 | igual a Ale ✔ |
| 9 | Thinking | `include_thoughts=True` (Gemini) | `GenerateConfig` reasoning_* (ejercicio 08) | `reasoning_effort` | pendiente |
| 10 | Seed | `seed_base + run_index` por corrida | por task en `GenerateConfig` | ? | diferencia, documentar |
| 11 | System prompt | `system_instruction` | `ChatMessageSystem` → `system_instruction` | ? | igual ✔ |
| 12 | Tool que no existe | `ToolErrorToStatusPlugin`: `{"status": "error", "error_message": "Tool not found", "tool_name": ...}` | el mismo dict (ejercicio 04a); sin eso, Inspect manda `{"error": "Tool X not found"}` | texto *"Unknown function: X. Available: ..."* | igual a Ale ✔ |
| 13 | Varias tools en un mismo turno | se ejecutan todas | se ejecutan todas | las rechaza: *"you must call ONLY ONE function per turn"* | diferencia con Aditya |
| 14 | Motivos de falla sin respuesta | `finish_safety` y `finish_recitation` por separado | `finish_content_filter` (el `stop_reason` de Inspect los une; el motivo original queda en `output.stop_details.type`) | — | diferencia menor, solo de registro |
| 15 | Último turno vacío | busca hacia atrás el último texto | solo mira el último turno | solo el último turno | caso borde: ver [D1 en decisiones de diseño](../docs/decisiones_diseno.md) |
| 16 | Al llegar al límite de llamadas | se pierden los eventos de la corrida | el transcript queda entero en el log | ? | mejora, no cambia el estímulo |
| 17 | Prompts y mensaje de usuario de Aditya | — | prompt clarificado en `data/prompts/main/aditya_variant.txt` | su config no es pública. El prompt clarificado está publicado en su [comentario del post](https://www.lesswrong.com/posts/HZn9AZeD2jfXXD2hH/is-gemini-3-scheming-in-the-wild) (2026-03-26); dice que el mensaje de usuario es el mismo que el del original | **resuelto en parte**: el texto es exacto, el espaciado reconstruido (el markdown pierde la indentación) |
| 18 | Vía de acceso al modelo | API de Google directa (ADK → `google-genai`) | **OpenRouter** (`openrouter/google/gemini-3.1-pro-preview`), con el proveedor upstream fijado (AI Studio o Vertex) | probablemente OpenRouter: su código usa `provider_preferences`, que es un concepto de OpenRouter (sin confirmar) | **diferencia con Ale, decidida** (2026-11-11): una sola vía para todos los modelos de la expansión. Afecta las filas 3 y 9 |
