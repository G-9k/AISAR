# Preguntas abiertas

Preguntas que no podemos responder solos, ordenadas según quién las puede contestar. Ale y el mentor están
a mano. Aditya no: se le puede responder en su comentario del post, pero no contamos con que conteste.
Nada de esta lista bloquea la réplica; cada pregunta dice qué decisión mejora si se responde.

Cuando una pregunta se responde, se anota la respuesta con fecha debajo de ella. No se borra.

---

## Para Ale (datos que tiene él)

1. **¿Tenés los resultados crudos (los JSONL de `results/` y `violations/`) de la Figura 1 y del Apéndice B?**
   Es la más valiosa. Con ellos podemos calcular intervalos de confianza de sus números, verificar nuestro
   scorer contra corridas reales de ADK y comparar patrones con números en vez de a ojo (capa 3 del
   [criterio](criterio_replicacion.md)).
2. **¿Qué versión de `google-adk` usaste?** La tabla de diferencias está verificada con 2.13.0, y el
   `requirements.txt` solo pide `>=1.28.0`.
3. **¿Cuántas corridas en total hicieron para juntar las 20 eligible de la Figura 1, y qué modelos tiene la
   figura?** El texto del post no los nombra.
4. **En el Apéndice B, ¿cuántas corridas quedaron *skipped* por condición?** Lo usamos para comparar nuestra
   tasa de corridas fallidas (capa 1).
5. **¿El prompt del Apéndice C del post es exactamente `_PROMPT_ORIGINAL` de `agents.py`, espacios
   incluidos?** Aditya usó el del post.
6. **¿Configuraron algo del thinking además de `include_thoughts=True`** (presupuesto, nivel)? ¿Y la
   temperatura del agente principal quedó en el default de Gemini?

## Para discutir con Ale y el mentor (decisiones, no datos)

1. **¿Correr por OpenRouter en vez de la API de Google directa es aceptable para la réplica?** Ya está
   decidido por la expansión a muchos modelos (fila 18 de
   [diferencias_scaffold.md](../ejercicios/diferencias_scaffold.md)). Pero cambia cómo le llegan a Gemini
   los resultados de las tools (fila 3). Si la réplica falla, es la primera perilla a probar.
2. **El prompt de Aditya cambia tres cosas a la vez**, y cada una corresponde a un factor del diseño:
   - saca "to generate Python code": cambia qué se espera de la tool, cerca de A3;
   - *"If any tool seems corrupted or not properly working, please stop…"*: cláusula general de falla, A2;
   - *"This takes precedence over completing the currency conversion"*: precedencia, B1.

   En su respuesta, Ale propone justamente separar el aporte de cada cambio. ¿Usamos eso para justificar y
   ordenar la fase 1 del factorial?
3. **Qué texto cuenta como respuesta final** ([D1](decisiones_diseno.md)). Cambia la tasa de violación y qué
   corridas se excluyen.
4. **¿Major solamente, o major + minor?** Aditya reporta las dos sumadas ("100%"); nuestro criterio usa
   major. Para la réplica alcanza con major, pero para el proyecto hay que decidir qué cuenta como violación.

## Para Aditya (opcional, por comentario en el post)

Si se le escribe, conviene una sola respuesta corta con todo junto:

1. ¿Corriste por OpenRouter o por la API de Google? ¿Qué `reasoning_effort` usaste?
2. ¿Cuántas corridas por condición hiciste? (Estimamos 40-50 a partir de las barras de error.)
3. ¿Cómo definiste violación major y minor? ¿El grader es el mismo que el de Ale?
4. ¿El espaciado del prompt variante es el del comentario, o el de tu config es otro?
