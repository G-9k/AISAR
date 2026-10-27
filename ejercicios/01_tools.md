# 01 · Tools

**Archivo:** `currency_eval/tools.py` · **Tests:** `pytest tests/test_ex01_tools.py`
**Tiempo estimado:** 45-60 min · **Docs:** [Custom tools](https://inspect.aisi.org.uk/tools-custom.html), [Tool basics](https://inspect.aisi.org.uk/tools.html)
**Original:** `original_currency_experiment/agents.py:46-93`

## Objetivos

- Definir tools con `@tool` y entender qué parte del código ve el modelo.
- Portar las dos tools de dominio de Ale con el **mismo comportamiento** y la **misma descripción**.
- Distinguir las dos formas de "fallar" de una tool: devolver `{"status": "error"}` o lanzar `ToolError`.

## Conceptos

**Una tool es una función que el modelo puede pedir que se ejecute.** El modelo nunca corre código:
responde algo como "llamá a `get_exchange_rate` con `base_currency="USD"`"; Inspect ejecuta la función y
le devuelve el resultado como un mensaje más (`ChatMessageTool`).

**Qué ve el modelo.** Inspect no le manda tu código al modelo. Le manda solo:
- el **nombre** de la tool,
- una **descripción**: el docstring, sin la sección `Args:`,
- los **parámetros**: nombre, tipo (de los type hints) y descripción (de la sección `Args:`).

Para el experimento esto importa mucho: si la descripción cambia, cambia el estímulo. Por eso hay un test
que compara la descripción contra lo que ADK le manda a Gemini en el código de Ale
(`tests/fixtures/adk_tool_declarations.json`, generado instalando ADK y pidiéndole sus declaraciones).

**El patrón `@tool`.** Se escribe así:

```python
@tool
def get_fee_for_payment_method() -> Tool:      # la "fábrica": se llama sin argumentos
    async def execute(method: str) -> str:     # la tool en sí: la llama Inspect
        """Descripción que ve el modelo.

        Args:
            method: Descripción del parámetro.
        """
        ...
    return execute                              # la fábrica devuelve la función interna
```

¿Por qué una función que devuelve otra función? Porque así la fábrica puede recibir configuración
(por ejemplo, qué variante de calculador usar, en el ejercicio 05) y la función interna la "recuerda".

## Python que aparece acá

- **Closures.** `execute` está definida *dentro* de `get_fee_for_payment_method` y puede usar sus variables.
  Es exactamente un bloque de Smalltalk: `[:method | ...]` que captura el contexto donde se creó.
  `get_fee_for_payment_method()` devuelve ese bloque, y `await tool(method="Bank Transfer")` lo evalúa.
- **`async def` / `await`.** Inspect corre muchos samples a la vez en un solo hilo; cuando una función
  espera algo (una API, un archivo), cede el control con `await`. Todas las tools son `async def`. Para
  llamar a una a mano fuera de Inspect: `asyncio.run(tool(method="Bank Transfer"))` (mirá `call()` en el test).
- **`dict.get(key)`** devuelve `None` si la clave no existe (en vez de fallar).
  `d.get(key, {})` devuelve `{}` en ese caso, lo que permite encadenar: `d.get(a, {}).get(b)`.
- **`json.dumps(dict)`** convierte un dict a un string JSON. Las tools de Inspect devuelven strings,
  no dicts.
- **f-strings:** `f"Payment method '{method}' not found"` inserta el valor de `method`.

## Tarea

- **01a** `get_fee_for_payment_method`: el docstring ya está (fijate cómo calza con el original). Escribí el cuerpo.
- **01b** `get_exchange_rate`: escribí el docstring (copiando el original y agregando `Args:`) y el cuerpo.

Los mensajes de error tienen que ser idénticos a los de `agents.py`: el modelo los lee.

<details><summary>Pista 01b: el docstring</summary>

La descripción tiene que quedar exactamente igual al docstring de `get_exchange_rate` en `agents.py`,
incluyendo las líneas `Returns {...}` y la indentación de `or {...}`. Después de eso, una línea en blanco y:
```
Args:
    base_currency: ...
    target_currency: ...
```
Inspect saca la sección `Args:` de la descripción y la usa para los parámetros.
</details>

<details><summary>Pista 01b: el error</summary>

El original arma el mensaje con los valores *originales* (`base_currency`, `target_currency`), no con las
versiones en minúscula que usa para buscar.
</details>

## Para pensar

1. **`ToolError` vs `{"status": "error"}`.** Inspect tiene `raise ToolError("...")`: la ejecución se corta y
   el modelo recibe el mensaje marcado como error de la tool. Ale, en cambio, devuelve un dict con
   `"status": "error"`. ¿Cuál preserva el experimento, si el prompt original dice *"check the 'status' field
   in the response"*?
   <details><summary>Respuesta</summary>
   El dict. El paso 3 del prompt original se refiere literalmente a un campo `status`; el experimento
   depende de que las tools que funcionan tengan ese campo y el calculador no. Además, `ToolErrorToStatusPlugin`
   en `runner.py` convierte las excepciones de ADK en un dict con `status: error`, justamente para mantener ese formato.
   </details>
2. Abrí `tests/fixtures/adk_tool_declarations.json`: ADK no manda descripción de los parámetros e Inspect
   la exige. Es una diferencia pequeña pero real (anotada en `diferencias_scaffold.md`). ¿Qué descripción de
   parámetro minimiza el cambio de estímulo?
3. En ese mismo JSON fijate cómo se llama la tercera tool, la del calculador, y comparalo con lo que dice el
   prompt. (Volvemos a esto en el ejercicio 05.)
