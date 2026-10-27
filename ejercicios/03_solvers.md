# 03 · Solvers y primer agente

**Archivo:** `currency_eval/solvers.py` · **Tests:** `pytest tests/test_ex03_solvers.py`
**Tiempo estimado:** 60 min · **Docs:** [Solvers](https://inspect.aisi.org.uk/solvers.html), [Tool use](https://inspect.aisi.org.uk/tools.html)
**Original:** `build_currency_agent()` en `agents.py:393-444`
**ARENA:** `system_message`, `prompt_template` (sección 2)

## Objetivos

- Escribir un solver propio: leer y modificar el `TaskState`.
- Reproducir cómo Ale elige el system prompt (variante + sufijo para modelos que no son Gemini).
- Armar un primer agente funcionando: system prompt + tools + loop de llamadas.
- Testear un solver sin correr una eval, armando el `TaskState` a mano.

## Conceptos

**TaskState.** El estado de *un* sample mientras se resuelve. Lo que más vamos a usar:
- `state.messages`: la conversación (lista de `ChatMessageSystem`, `ChatMessageUser`, `ChatMessageAssistant`, `ChatMessageTool`).
- `state.metadata`: la metadata del sample (la que armaste en el ejercicio 02).
- `state.model`: el nombre del modelo que se está evaluando.
- `state.tools`: las tools disponibles.
- `state.output`: la última respuesta del modelo.

**Solver.** Igual que las tools, es una fábrica que devuelve una función `async`:

```python
@solver
def mi_solver(parametro) -> Solver:
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        ...                 # leer / modificar state
        return state        # ¡siempre devolverlo!
    return solve
```

`generate` es una función que llama al modelo con `state.messages` y agrega la respuesta. Un solver puede
llamarla o no.

**chain(...)** compone solvers en secuencia: es lo mismo que pasarle una lista a `Task(solver=[...])`,
pero empaquetado como un solo solver.

**use_tools(...)** pone tools en `state.tools`. **generate(tool_calls="loop")** llama al modelo; si pide
tools, las ejecuta, agrega los resultados y vuelve a llamar. Termina cuando el modelo responde **sin**
pedir tools. Es la misma regla de corte que el runner de ADK y que Aditya (`run_step.py`).

**¿Por qué no `react()`?** Inspect trae un agente listo, `react()`, pero cambia el scaffold: agrega una
tool `submit()` para terminar y, si el modelo responde sin tools, le manda un mensaje pidiéndole que
continúe. En el original, una respuesta sin tools *es* la respuesta final. Usar `react()` cambiaría el
estímulo. En el ejercicio 04 escribimos el loop a mano para controlar cada detalle.

**System prompt en ADK vs Inspect.** ADK manda la `instruction` como `system_instruction` de Gemini. El
provider de Google de Inspect convierte los `ChatMessageSystem` en `system_instruction`. Llega igual.

## Python que aparece acá

- **`state.messages.insert(0, msg)`:** inserta al principio de la lista (`addFirst:`).
- **Expresiones condicionales:** `x if cond else y`.
- **Parámetros con default `None`** (`no_thinking_suffix: bool | None = None`): un patrón común para
  decir "si no me decís nada, decido yo". `bool | None` significa "un bool o None".

## Tarea

- **03a** `currency_system_prompt(no_thinking_suffix=None)`: insertá el system prompt del sample, con el sufijo
  cuando corresponda (misma regla que `build_currency_agent`).
- **03b** `currency_agent_v0()`: el `chain` del `TODO`.

Fijate en dos tests:
- `test_03a_same_as_builtin_system_message_template`: el solver incorporado `system_message("{system_prompt}")`
  ya reemplaza `{placeholders}` con la metadata del sample. Tu solver hace lo mismo y además maneja el sufijo.
- `test_03b_agent_v0_runs_the_tool_loop`: guioná un modelo que llama a las dos tools y después responde.
  Leelo con calma: es el patrón con el que vamos a testear todo el agente.

<details><summary>Pista 03a</summary>

```python
prompt = state.metadata["system_prompt"]
add_suffix = not is_gemini(str(state.model)) if no_thinking_suffix is None else no_thinking_suffix
```
</details>

## Opcional: verlo en el visor

Creá un archivo de prueba (por ejemplo `scratch_task.py`, fuera de `currency_eval/`) con una `@task` que use
`build_dataset(["original"], ["StaticResponse"])` y `currency_agent_v0()`, y corrélo con
`inspect eval scratch_task.py --model mockllm/model`. En el visor mirá la pestaña de mensajes. ¿Qué hace el
loop cuando mockllm no pide ninguna tool?

## Para pensar

1. En el test 03b el modelo guionado nunca llama al calculador. En el escenario real, ¿qué tool falta y dónde
   debería engancharse? (Ejercicio 05.)
2. `generate(tool_calls="loop")` no tiene límite de vueltas. Ale tiene `CallLimitPlugin` (30 llamadas) y Aditya
   `max_steps` (10). ¿Qué pasaría con un modelo que llama a la misma tool para siempre? (Ejercicio 04: `message_limit`.)
