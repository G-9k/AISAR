# 00 · Primera eval

**Archivo:** `currency_eval/ex00_hello.py` · **Tests:** `pytest tests/test_ex00_hello.py`
**Tiempo estimado:** 30-45 min · **Docs:** [Tasks](https://inspect.aisi.org.uk/tasks.html), [Eval logs](https://inspect.aisi.org.uk/eval-logs.html), [Log viewer](https://inspect.aisi.org.uk/log-viewer.html)

## Objetivos

- Entender la fórmula central de Inspect: **Task = dataset + solver + scorer**.
- Correr una eval desde Python y desde la terminal.
- Saber qué hay dentro de un log y abrirlo con `inspect view`.
- Usar `mockllm` para probar sin gastar plata.

## Conceptos

**Task.** Es la unidad que Inspect corre. Junta tres cosas:
- `dataset`: una lista de `Sample`. Cada uno tiene un `input` (lo que recibe el modelo) y, opcionalmente,
  un `target` (la respuesta esperada).
- `solver`: qué se hace con cada sample. El más simple es `generate()`: le manda los mensajes al modelo
  y guarda la respuesta.
- `scorer`: cómo se puntúa la respuesta. `includes()` marca correcto si el `target` aparece en la respuesta.

**eval().** Corre una o más tasks contra un modelo y devuelve **una lista** de `EvalLog`, uno por task.
También escribe cada log a disco (`log_dir`).

**EvalLog.** Todo lo que pasó, en un objeto:
- `log.status`: `"success"`, `"error"`, etc.
- `log.eval`: configuración (task, modelo, fecha...).
- `log.samples`: lista de `EvalSample`. Cada uno tiene `messages` (la conversación completa) y `output`
  (la última respuesta del modelo; `output.completion` es su texto).
- `log.results.scores`: un resultado por scorer, cada uno con sus `metrics` (por ejemplo `"accuracy"`).

**mockllm.** Un "modelo" de Inspect que no llama a ninguna API. Por defecto responde un texto fijo.
Con `custom_outputs=[...]` le das un guion: la primera vez que se le pide una respuesta devuelve el
primer elemento, después el segundo, y así sigue. En todos los tests vamos a usarlo para simular a Gemini.

## Python que aparece acá

- **Decoradores (`@task`).** `@task` arriba de una función es azúcar sintáctico para
  `hello_currency = task(hello_currency)`: una función que recibe tu función y devuelve otra "envuelta".
  En este caso la registra para que `inspect eval` la encuentre en el archivo. Es parecido a envolver un
  método en Smalltalk para agregarle comportamiento sin cambiar su código.
- **Type hints (`-> Task`, `log: EvalLog`).** Son anotaciones: Python no las verifica al correr, pero
  documentan y el editor las usa para autocompletar.
- **Argumentos con nombre (`eval(task, model=m, log_dir=d)`).** Como los keywords de Smalltalk, pero opcionales
  y en cualquier orden.

## Tarea

- **00a** `hello_currency()`: devolvé la `Task` descripta en el `TODO`.
- **00b** `run_with_mock(answer, log_dir)`: corré la task con un mockllm que responde `answer`.
- **00c** `final_answer(log)`: sacá del log el texto de la respuesta final.
- **00d** `accuracy_of(log)`: sacá del log el valor de la métrica `accuracy`.

Cuando pasen los tests, probá desde la terminal:

```powershell
inspect eval currency_eval/ex00_hello.py --model mockllm/model
inspect view
```

`inspect view` abre el visor en el navegador (o usá la extensión de VS Code, que muestra los logs en el
panel lateral). Abrí el log y recorré: la conversación, el score, la pestaña de info del modelo.

<details><summary>Pista 00b</summary>

```python
model = get_model("mockllm/model", custom_outputs=[ModelOutput.from_content(model="mockllm/model", content=answer)])
```
Después `eval(...)` y quedate con el elemento `[0]` de la lista.
</details>

<details><summary>Pista 00d</summary>

`log.results.scores` es una lista (un elemento por scorer). Cada elemento tiene un dict `metrics`,
y cada métrica tiene `.value`.
</details>

## Para pensar

1. Desde la terminal la accuracy da **0**, pero en el test con `GOOD_ANSWER` da 1. ¿Por qué? (Mirá en el
   visor qué respondió el modelo.)
2. `includes()` buscaría `"103430.25"`. ¿Qué pasaría si el modelo respondiera `"103,430.25"`? ¿Qué te dice
   eso sobre usar `includes()` para detectar violaciones? (Lo retomamos en el ejercicio 06.)
3. ¿Qué cambiarías para que esta misma task corra con Gemini? (No lo corras todavía: solo es el flag `--model`.)
