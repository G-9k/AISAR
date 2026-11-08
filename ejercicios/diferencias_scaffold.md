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
| 3 | Formato del resultado de una tool | `function_response.response` = el dict tal cual (`{"status": ..., ...}`) | `{"output": "<dict serializado como JSON>"}` (provider de Google de Inspect) | string JSON en el contenido del mensaje de tool | **diferencia**: revisar en el piloto |
| 4 | Nombre de la tool del calculador | `CalculationAgent` (aunque el prompt diga "calculation_agent tool") | `CalculationAgent` por defecto (ejercicio 05) | `calculation_agent` | **decisión pendiente** (05, Para pensar 1) |
| 5 | Descripción de la tool del calculador | vacía `""` | Inspect no acepta vacía: se elige en el ejercicio 05 | *"A calculation sub-agent that generates and executes Python code... it will return the computed result."* | **decisión pendiente** (05, Para pensar 2) |
| 6 | Respuesta del calculador | LLM (flash-lite) envuelto: `{"result": "<texto>"}` | mock determinístico con los textos de Aditya (ejercicio 05) | string fijo `{"result": ...}` | StaticResponse ≈ igual; CodeOnly distinto (ver plan) |
| 7 | Regla de corte del loop | respuesta sin tool calls | igual (ejercicio 04) | igual | igual ✔ |
| 8 | Límite de llamadas | 30 llamadas del agente principal | contador propio de 30 llamadas (ejercicio 04) | `max_steps` 10 | igual a Ale ✔ |
| 9 | Thinking | `include_thoughts=True` (Gemini) | `GenerateConfig` reasoning_* (ejercicio 08) | `reasoning_effort` | pendiente |
| 10 | Seed | `seed_base + run_index` por corrida | por task en `GenerateConfig` | ? | diferencia, documentar |
| 11 | System prompt | `system_instruction` | `ChatMessageSystem` → `system_instruction` | ? | igual ✔ |
| 12 | Tool que no existe | `ToolErrorToStatusPlugin`: `{"status": "error", "error_message": "Tool not found", "tool_name": ...}` | el mismo dict (ejercicio 04a); sin eso, Inspect manda `{"error": "Tool X not found"}` | texto *"Unknown function: X. Available: ..."* | igual a Ale ✔ |
| 13 | Varias tools en un mismo turno | se ejecutan todas | se ejecutan todas | las rechaza: *"you must call ONLY ONE function per turn"* | diferencia con Aditya |
| 14 | Motivos de falla sin respuesta | `finish_safety` y `finish_recitation` por separado | `finish_content_filter` (Inspect los une) | — | diferencia menor, solo de registro |
| 15 | Último turno vacío | busca hacia atrás el último texto | solo mira el último turno | solo el último turno | caso borde (04, Para pensar 2) |
| 16 | Al llegar al límite de llamadas | se pierden los eventos de la corrida | el transcript queda entero en el log | ? | mejora, no cambia el estímulo |
| 17 | Mensaje de usuario y prompts de Aditya | — | — | salen de un config que no está en la rama pública | **pendiente**: pedírselos antes del ejercicio 08 |
