# 04 · El loop del agente, escrito a mano

**Archivo:** `currency_eval/agent.py` · **Tests:** `pytest tests/test_ex04_agent_loop.py`
**Tiempo estimado:** 60-75 min · **Docs:** [Custom agents](https://inspect.aisi.org.uk/agent-custom.html), [Errors and limits](https://inspect.aisi.org.uk/errors-and-limits.html)
**Original:** `run_single()`, `CallLimitPlugin`, `ToolErrorToStatusPlugin` y `_derive_run_outcome()` en `runner.py`

## Objetivos

- Reemplazar `generate(tool_calls="loop")` por un loop propio, con las dos piezas que usa por dentro:
  `model.generate()` y `execute_tools()`.
- Portar los dos plugins de ADK que usa Ale: el límite de 30 llamadas y la conversión de errores de tools.
- Registrar cómo terminó cada corrida (`run_status`), como hace Ale. El scorer del ejercicio 06 lo necesita.
- Conocer `state.store` y la diferencia entre los límites de Inspect y un contador propio.

## Conceptos

**¿Por qué escribir el loop a mano, si `generate(tool_calls="loop")` ya anda?** Por tres detalles del
original que el loop de Inspect no reproduce:

1. **El límite de Ale cuenta llamadas al modelo** (`CallLimitPlugin`, 30 por corrida). Inspect tiene
   `message_limit`, pero cuenta *mensajes*: cada turno agrega un mensaje del assistant y uno por cada tool
   pedida, así que "30 llamadas" no equivale a ningún número fijo de mensajes. Con un contador propio, es exacto.
2. **Los errores de tools llegan distinto.** Si el modelo pide una tool que no existe, Inspect le responde
   con un error. Ale instaló `ToolErrorToStatusPlugin` para que, en cambio, el modelo reciba un dict con
   `"status": "error"`, que es justamente lo que el prompt le dice que revise. Es parte del estímulo.
3. **Ale clasifica cada corrida** como `ok` o `failed` (con un motivo) y el análisis excluye las fallidas.
   Hay que guardar esa clasificación en algún lado.

**Las piezas.**
- `get_model()`, sin argumentos y dentro de un solver, devuelve **el modelo que se está evaluando** (el de
  `--model`), con la configuración de la eval: si corrés con `temperature=0.3`, la llamada la usa (lo probé).
- `await model.generate(messages, tools)` le manda la conversación y las tools al modelo y devuelve un
  `ModelOutput`. **No toca el `state`**: a diferencia del `generate` que recibe el solver, no agrega nada a
  `state.messages` ni actualiza `state.output`. Eso lo hacés vos.
- `await execute_tools(messages, tools)` mira el **último** mensaje del assistant, ejecuta las tools que pidió
  y devuelve un resultado cuyo `.messages` son los `ChatMessageTool` nuevos. Tampoco los agrega: los agregás vos.

**Qué pasa cuando el modelo pide una tool que no existe.** Lo probé: `execute_tools` no falla. Devuelve un
`ChatMessageTool` con `content=""` y `error=ToolCallError(type="parsing", message="Tool X not found")`. El
provider de Google se lo manda a Gemini como `{"error": "Tool X not found"}`. Ale, en cambio, le mandaba
`{"status": "error", "error_message": "Tool not found", "tool_name": "X"}`. El ejercicio 04a convierte lo
primero en lo segundo. (Ojo: si una tool lanza una excepción común, como `KeyError`, el sample entero
termina con error. Nuestras tools nunca lanzan, así que no nos afecta.)

**`state.store`.** Un diccionario por sample para guardar lo que *pasa* durante la corrida. Se usa con
`state.store.set("clave", valor)` y `state.store.get("clave")`, y queda en el log en `sample.store`. La
diferencia con `metadata`: la metadata describe la **condición** (la armás antes de correr, ejercicio 02);
el store registra **lo que pasó**. Usamos los mismos nombres que los registros JSONL de Ale
(`run_status`, `run_failure_reason`, `total_calls`), así el scorer del 06 se porta casi literal.

**Límites de Inspect vs contador propio.** Los límites de la eval (`message_limit`, `token_limit`,
`time_limit`) siguen funcionando con tu loop: los chequea `model.generate()`. Si uno se alcanza, Inspect
corta el sample y lo anota en `sample.limit` (tu código no llega a escribir el store). Conviene usarlos
como **red de seguridad para el presupuesto**, y el contador propio para la semántica de Ale. Una mejora
de paso: cuando Ale llegaba al límite perdía todos los eventos de la corrida (`events = []`); acá el
transcript queda entero en el log.

## Python que aparece acá

- **`while True:` + `break`:** un loop que corre hasta que algo adentro lo corta. Es el
  `[...] repeat` de Smalltalk con una salida explícita.
- **Devolver dos valores:** `return "failed", "call_limit_reached"` devuelve una tupla, y
  `status, reason = derive_run_outcome(...)` la desarma en dos variables.
- **`any(...)`:** `any(condición for x in lista)` es `True` si algún elemento cumple. Es el `anySatisfy:`
  de Smalltalk.
- **`x in diccionario`** pregunta si `x` es una de las claves (`includesKey:`).
- **Generator expression en `extend`:** `lista.extend(f(m) for m in otros)` agrega `f(m)` por cada `m`,
  sin armar una lista intermedia. Es como `addAll: (otros collect: [:m | ...])`.
- **Crear vs modificar.** En 04a devolvés un mensaje **nuevo** en vez de cambiar el original. Así nadie que
  tenga una referencia al viejo se lleva una sorpresa (lo mismo que charlamos con `insert`).

## Tarea

- **04a** `tool_error_as_status(message)`: el `ToolErrorToStatusPlugin` de Ale, como función pura.
- **04b** `derive_run_outcome(state, call_limit_reached)`: el `_derive_run_outcome` de Ale, a partir del `state`.
- **04c** `agent_loop(max_calls=30)`: el loop. Al final guarda el resultado en `state.store`.
- **04d** `currency_agent_v1()`: el agente del 03b con tu loop.

Mirá `test_04d_v1_writes_the_same_conversation_as_v0`: es un **test diferencial**. En el caso normal, tu
loop tiene que producir exactamente la misma conversación que el de Inspect. Es una forma barata de ganar
confianza en código que reemplaza algo que ya funciona.

<details><summary>Pista 04b: la respuesta final</summary>

Ale extrae el texto visible de la última respuesta, sin las partes de razonamiento (`thought=True`). En
Inspect eso ya existe: `state.output.completion` (ejercicio 00). El test
`test_04b_thinking_alone_is_not_an_answer` verifica justamente que una respuesta con solo razonamiento
cuenta como vacía.
</details>

<details><summary>Pista 04c: la forma del loop</summary>

```python
model = get_model()
calls = 0
while True:
    if ...:            # ¿ya hice max_calls llamadas?
        ...
        break
    output = await model.generate(...)
    calls += 1
    ...                # actualizar state.output y state.messages
    if ...:            # ¿no pidió tools?
        break
    ...                # ejecutar las tools y agregar sus mensajes
```
</details>

## Opcional: verlo en el visor

En tu archivo de prueba (`scratch_task.py`), armá una task con `currency_agent_v1()` y un modelo guionado
que pida `calculation_agent` (una tool que este agente no tiene). Abrí el log con `inspect view` y mirá qué
recibió el modelo en el mensaje de la tool.

## Para pensar

1. **Llamadas en paralelo.** Un modelo puede pedir dos tools en el mismo turno. ADK y tu loop ejecutan las
   dos. Aditya, en cambio, las rechaza y le responde al modelo *"You called 2 functions, but you must call
   ONLY ONE function per turn"* (`run_step.py`). ¿Puede esa diferencia de scaffold cambiar la tasa de
   violación? Ya está anotada en `diferencias_scaffold.md`.
2. **Un caso borde de la respuesta final.** Ale busca hacia atrás el último evento que tenga texto. Si el
   último turno del modelo vino vacío, pero un turno anterior traía texto junto con un pedido de tool (por
   ejemplo *"Voy a buscar la tasa"*), Ale marca la corrida `ok` con ese texto viejo. Tu versión la marca
   `failed`. ¿Cuál te parece más correcta? ¿Importa para medir violaciones?
3. Como red de seguridad, ¿qué `message_limit` pondrías para que nunca corte antes que tu contador de 30
   llamadas, pero sí frene un loop desbocado?
