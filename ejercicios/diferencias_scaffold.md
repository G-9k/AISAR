# Diferencias de scaffold: ADK (Ale) vs Inspect (este port)

Todo lo que el modelo ve distinto en el port respecto al original. Se completa a medida que avanzamos.
Si la réplica no coincide con Aditya o con Ale, revisar esto primero.

Verificado con google-adk 2.13.0 (Ale pedía `>=1.28.0`; la versión exacta que usó no está registrada)
e inspect_ai 0.3.285.

| # | Qué | ADK (Ale) | Inspect (port) | Aditya | Estado |
|---|---|---|---|---|---|
| 1 | Descripción de fee/rate | docstring completo | idéntica (docstring sin `Args:`) | ? | igual ✔ |
| 2 | Descripción de parámetros de fee/rate | ninguna | obligatoria en Inspect: texto mínimo | ? | diferencia menor, inevitable |
| 3 | Formato del resultado de una tool | `function_response.response` = el dict tal cual (`{"status": ..., ...}`) | `{"output": "<dict serializado como JSON>"}` (provider de Google de Inspect) | string JSON en el contenido del mensaje de tool | **diferencia**: revisar en el piloto |
| 4 | Nombre de la tool del calculador | `CalculationAgent` (aunque el prompt diga "calculation_agent tool") | a decidir en el ejercicio 05 | `calculation_agent` | **decisión pendiente** |
| 5 | Descripción de la tool del calculador | vacía `""` | Inspect no acepta vacía | "generates and executes Python code..." | **decisión pendiente** |
| 6 | Respuesta del calculador | LLM (flash-lite) envuelto: `{"result": "<texto>"}` | mock determinístico (ejercicio 05) | string fijo `{"result": ...}` | StaticResponse ≈ igual; CodeOnly distinto (ver plan) |
| 7 | Regla de corte del loop | respuesta sin tool calls | `generate(tool_calls="loop")`: igual | igual | igual ✔ |
| 8 | Límite de llamadas | 30 llamadas del agente principal | a definir (ejercicio 04) | `max_steps` 10 | pendiente |
| 9 | Thinking | `include_thoughts=True` (Gemini) | `GenerateConfig` reasoning_* (ejercicio 08) | `reasoning_effort` | pendiente |
| 10 | Seed | `seed_base + run_index` por corrida | por task en `GenerateConfig` | ? | diferencia, documentar |
| 11 | System prompt | `system_instruction` | `ChatMessageSystem` → `system_instruction` | ? | igual ✔ |
