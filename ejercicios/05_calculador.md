# 05 · El calculador

**Archivos:** `currency_eval/calculator.py` (05a, 05b) y `currency_eval/agent.py` (05c) · **Tests:** `pytest tests/test_ex05_calculator.py`
**Tiempo estimado:** 45-60 min · **Docs:** [Custom tools](https://inspect.aisi.org.uk/tools-custom.html)
**Original:** `CalculatorVariant` y `build_calculation_agent()` en `agents.py:97-176` y `366-390`;
`CALCULATOR_RESPONSES` en `run_step.py` de Aditya

## Objetivos

- Escribir una tool cuya fábrica **recibe configuración**: la variante de falla.
- Fijar explícitamente el nombre que ve el modelo (`@tool(name=...)`).
- Elegir las tools **por sample**, leyendo la metadata, con un solver propio.
- Tomar (y anotar) una decisión de fidelidad: la descripción del calculador. La otra, el nombre, ya está
  tomada (decisión D2).

## Conceptos

**El calculador en cada versión.**

| | Qué es | Qué devuelve |
|---|---|---|
| Ale (ADK) | Un sub-agente: otro LLM (gemini-2.5-flash-lite) con su propio prompt, envuelto como tool por `AgentTool` | El texto que genera ese LLM, envuelto por ADK como `{"result": "<texto>"}` |
| Aditya | Un string fijo en el código | `{"result": "<texto fijo>"}` |
| Este port | Un texto fijo por variante, leído de `data/calculator_responses/` | `{"result": "<texto fijo>"}`, serializado con `json.dumps()` |

Usamos un mock fijo como el de Aditya por tres razones: Aditya es el punto de comparación de la réplica,
`CLAUDE.md` pide tools mockeadas determinísticas, y no cuesta nada. Los textos están copiados byte a byte
de su código (`tests/test_data.py` lo verifica). La versión fiel a Ale, con un LLM de verdad como
sub-agente, queda para el ejercicio bonus B1.

**La fábrica con configuración.** Acá se ve para qué sirve el patrón de `@tool` que charlamos en el
ejercicio 01. La variante (`"StaticResponse"` o `"CodeOnly"`) la elegís vos como experimentador: es un
parámetro de la **fábrica**. El modelo solo ve el parámetro de la función interna, `request`, que es el
pedido que le escribe al calculador. Para el modelo, las dos variantes son la misma tool.

**Fallar temprano.** Si la variante no existe, la fábrica tiene que lanzar `ValueError` **al construir la
tool**, no cuando el modelo la llame. Un error de tipeo en el nombre de la variante tiene que explotar
cuando armás el agente, no en el medio de una corrida paga.

**El nombre de la tool: `@tool(name="calculation_agent")`.** Por defecto, el nombre que ve el modelo es el
de la fábrica. Acá coinciden, pero el stub lo fija explícitamente porque **el nombre es parte del estímulo**:
si mañana alguien renombra la función de Python, el modelo no tiene que enterarse. Además es una
diferencia deliberada con Ale. ADK le manda a Gemini `CalculationAgent` (el nombre del sub-agente; está
en `tests/fixtures/adk_tool_declarations.json`), mientras el prompt dice *"use the calculation_agent tool"*.
Usamos el nombre del prompt, igual que Aditya: el porqué está en la decisión D2 de
[`docs/decisiones_diseno.md`](../docs/decisiones_diseno.md).

Fijate que `@tool` sin paréntesis y `@tool(name=...)` con paréntesis son dos formas válidas: la segunda
primero llama a `tool` con la configuración y usa lo que devuelve como decorador. Otra vez, la diferencia
entre la fábrica y lo que fabrica.

**Tools por sample.** `use_tools(...)` fija las tools para **todos** los samples de la task. Pero el
calculador depende de la metadata de cada sample. Por eso va en un solver propio que lee
`state.metadata["calculator_variant"]` y agrega la tool a `state.tools`. Igual que `state.messages`,
`state.tools` devuelve la lista interna del `TaskState`, así que un `append` la modifica directamente.

**El orden importa.** El modelo recibe las tools en el orden de `state.tools`. En Ale el orden es fee,
tasa de cambio y calculador (`agents.py:437-441`). `test_05c_model_sees_the_three_tools_in_adk_order` lo
verifica leyendo el log: en `sample.events`, cada llamada al modelo queda registrada con las tools que vio.

## Python que aparece acá

- **Decorador con argumentos:** `@tool(name="X")` equivale a `calculation_agent = tool(name="X")(calculation_agent)`.
- **`!r` en un f-string:** `f"variant {variant!r}"` inserta `repr(variant)`, es decir, con comillas:
  `variant 'Origial'`. Útil en mensajes de error, porque se ven los espacios o las mayúsculas de más.
- **`json.dumps` con texto de varias líneas:** el texto de `CodeOnly` tiene saltos de línea y comillas.
  `json.dumps` los escapa (`\n`, `\"`) y produce JSON válido. Es lo que recibe el modelo:
  `{"result": "```python\n# Currency conversion calculation\n..."}`. Armarlo a mano con un f-string se
  rompería, como vimos en el ejercicio 01.

## Tarea

- **05a** `calculation_agent(variant)`: la tool. Leé la respuesta en la fábrica, no en `execute`.
- **05b** `add_calculator()`: el solver que agrega el calculador del sample.
- **05c** `currency_agent()` (en `agent.py`): el agente completo. Es el agente con el que vamos a replicar.

<details><summary>Pista 05a: la estructura</summary>

```python
@tool(name="calculation_agent")
def calculation_agent(variant: str) -> Tool:
    ...                          # en la fábrica: buscar el archivo, validar, preparar la respuesta

    async def execute(request: str) -> str:
        """..."""
        ...                      # acá solo devolver la respuesta preparada

    return execute
```
</details>

## Para pensar

1. **El nombre (ya decidido, D2).** Con el nombre de Ale, un modelo que obedece al prompt pide
   `calculation_agent`, una tool que no existe, y recibe `{"status": "error", "error_message": "Tool not
   found", ...}` (ejercicio 04). Por eso elegimos el nombre del prompt. Si algún día querés medir cuánto
   importaba esa diferencia, `tool_with(calculation_agent(variante), name="CalculationAgent")` recupera el
   nombre de Ale sin tocar la tool.
2. **La descripción.** ADK manda una descripción **vacía** (el sub-agente de Ale no tiene `description`).
   Inspect no acepta tools sin descripción: lo probé y lanza `ValueError`. Aditya usa una descripción larga
   que **promete un resultado**: *"...it will return the computed result"*. Una descripción mínima cambia
   menos el estímulo respecto de Ale. La de Aditya, en cambio, puede hacer más evidente que la tool falló.
   Elegí una, escribila en el docstring y anotá la decisión en la fila 5 de `diferencias_scaffold.md`.
3. **CodeOnly no es igual en Ale.** El código de Aditya es fijo y trae los valores correctos. El de Ale lo
   escribía flash-lite a partir del pedido del agente principal: si el agente pasaba un valor mal, el código
   lo heredaba. ¿Cuál de las dos versiones hace más tentador "terminar la cuenta a mano"?
