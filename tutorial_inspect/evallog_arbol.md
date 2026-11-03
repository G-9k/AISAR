# Anatomía de un `EvalLog`

Qué hay adentro del objeto que devuelve `eval()` (y que `read_eval_log()` lee desde disco).
Nombres y tipos verificados contra la versión de Inspect instalada en `.venv`.

No están todos los atributos (un `EvalSample` tiene más de 30). Están los útiles.
★ = relevante para el proyecto.

## Cómo leer los tipos

| Si el type hint dice... | Significa... | Cómo accedés al siguiente nivel |
|---|---|---|
| `EvalSpec` (una clase) | Hay un objeto | Con punto: `log.eval.model` |
| `list[EvalSample]` | Hay una lista | Con índice: `log.samples[0]` |
| `dict[str, Score]` | Hay un diccionario (como un `Dictionary` de Smalltalk) | Con clave: `algo["clave"]` |
| `... \| None` | Puede haber eso, o nada | Chequear antes: `None[0]` o `None.algo` da error |
| `"a" \| "b" \| "c"` | Un string, solo uno de esos valores | — |

## El árbol

```
EvalLog                                         ← una corrida (una task × un modelo)
├── status    : "started" | "success" | "cancelled" | "error"   ★ chequealo siempre
├── error     : EvalError | None                ← si status == "error", por qué
│     ├── message   : str
│     └── traceback : str
├── location  : str                             ← ruta del archivo .eval
│
├── eval      : EvalSpec                        ← la "ficha" de la corrida
│     ├── task        : str                     ← nombre de la task
│     ├── model       : str                     ← "mockllm/model", "google/gemini-..."
│     ├── created     : str                     ← fecha y hora
│     ├── task_args   : dict[str, Any]          ★ los argumentos de la task (tu condición A/B/D)
│     ├── model_generate_config : GenerateConfig ★ temperature, reasoning_effort, etc.
│     ├── tags        : list[str] | None
│     ├── metadata    : dict[str, Any] | None   ← el metadata= que le pasaste a eval()
│     └── dataset     : EvalDataset
│           ├── name    : str | None
│           └── samples : int | None            ← cuántos samples tenía el dataset
│
├── stats     : EvalStats                       ← tiempos y consumo
│     ├── started_at / completed_at : str
│     └── model_usage : dict[str, ModelUsage]   ★ tokens por modelo (→ costo)
│           └── ModelUsage
│               ├── input_tokens / output_tokens / total_tokens : int
│               └── reasoning_tokens : int | None
│
├── samples   : list[EvalSample] | None         ← DETALLE: uno por sample × epoch
│     └── EvalSample
│         ├── id        : int | str             ← id del Sample original
│         ├── epoch     : int                   ← qué repetición (1, 2, 3...)
│         ├── input     : str | list[ChatMessage]
│         ├── target    : str | list[str]
│         ├── metadata  : dict[str, Any]        ★ el metadata del Sample (condición por sample)
│         ├── error     : EvalError | None      ← si ESTE sample falló técnicamente
│         ├── limit     : EvalSampleLimit | None ★ si chocó un límite
│         │     ├── type  : "message" | "token" | "time" | ...
│         │     └── limit : float
│         ├── total_time  : float | None        ← segundos
│         ├── model_usage : dict[str, ModelUsage]
│         │
│         ├── messages  : list[ChatMessage]     ★ LA CONVERSACIÓN COMPLETA, en orden
│         │     ├── ChatMessageSystem           ← role "system": el system prompt
│         │     │     └── content : str | list[Content]
│         │     ├── ChatMessageUser             ← role "user": la pregunta
│         │     │     └── content : str | list[Content]
│         │     ├── ChatMessageAssistant        ← role "assistant": el modelo
│         │     │     ├── content    : str | list[Content]
│         │     │     │     ├── ContentText      → .text : str
│         │     │     │     └── ContentReasoning → .reasoning : str, .summary, .redacted  ★ CoT
│         │     │     └── tool_calls : list[ToolCall] | None   ★ qué tools pidió
│         │     │           └── ToolCall
│         │     │               ├── id        : str
│         │     │               ├── function  : str            ← nombre de la tool
│         │     │               └── arguments : dict[str, Any] ← con qué argumentos
│         │     └── ChatMessageTool             ← role "tool": lo que devolvió una tool
│         │           ├── content      : str | list[Content]   ★ el resultado de la tool
│         │           ├── function     : str | None            ← qué tool fue
│         │           ├── tool_call_id : str | None            ← a qué ToolCall responde
│         │           └── error        : ToolCallError | None
│         │
│         ├── output    : ModelOutput           ← la ÚLTIMA respuesta del modelo
│         │     ├── model      : str
│         │     ├── completion : str            ★ texto plano de la respuesta final
│         │     ├── choices    : list[ChatCompletionChoice]
│         │     │     └── ChatCompletionChoice
│         │     │         ├── message     : ChatMessageAssistant   (igual que arriba)
│         │     │         └── stop_reason : "stop" | "max_tokens" | "tool_calls" | ...
│         │     ├── usage      : ModelUsage | None
│         │     ├── time       : float | None
│         │     └── error      : str | None
│         │
│         ├── scores    : dict[str, Score] | None  ← por nombre de scorer
│         │     └── Score
│         │         ├── value       : str | int | float | bool | list | dict  ★
│         │         ├── answer      : str | None  ← qué respuesta extrajo el scorer
│         │         ├── explanation : str | None  ★ el porqué (ej. razonamiento del juez)
│         │         └── metadata    : dict | None
│         │
│         └── events    : list[Event]           ← línea de tiempo detallada: cada llamada
│                                                  al modelo, cada tool, cada score. Es lo que
│                                                  muestra inspect view en la pestaña de eventos.
│
└── results   : EvalResults | None              ← AGREGADO: métricas sobre todos los samples
      ├── total_samples / completed_samples : int
      └── scores : list[EvalScore]              ← uno por scorer
            └── EvalScore
                ├── name    : str
                └── metrics : dict[str, EvalMetric]
                      └── EvalMetric
                          ├── name  : str
                          └── value : float
```

## Notas

- **`Sample` y `EvalSample` no son lo mismo.** `Sample` es la *definición* del caso (lo que pusiste en el
  dataset). `EvalSample` es el *registro de lo que pasó*: copia `input` y `target`, y agrega la
  conversación, la respuesta y los puntajes.
- **Dos niveles de scoring.** `samples[i].scores` guarda el `Score` individual de cada sample (por
  ejemplo `"C"` o `"I"`). `results.scores` guarda las métricas calculadas sobre todos los samples
  (`accuracy`, `stderr`...).
- **`output` y `messages` se superponen.** El `ChatMessageAssistant` de `output.choices[0].message` es
  el mismo que el último `ChatMessageAssistant` de `messages`. `output` es un atajo a la respuesta
  final; `messages` es la historia completa.
- **`completion` solo contiene las partes de texto.** El razonamiento (`ContentReasoning`) y los pedidos
  de tools (`tool_calls`) no aparecen ahí: hay que buscarlos en el mensaje.

## Recorrer muchos samples

El `for` de Python recorre los elementos directamente, como `do:` en Smalltalk:

```python
for sample in log.samples:                 # log samples do: [:sample | ...]
    print(sample.id, sample.epoch, sample.output.completion)
```

Si además necesitás la posición:

```python
for i, sample in enumerate(log.samples):
    print(i, sample.output.completion)
```

Para juntar valores en una lista, una *list comprehension* (equivalente a `collect:`):

```python
respuestas = [sample.output.completion for sample in log.samples]
```

Con varios logs (varios modelos o tasks), hay un loop más afuera:

```python
for log in logs:
    if log.status != "success":            # samples puede ser None si falló
        continue
    for sample in log.samples:
        print(log.eval.model, sample.id, sample.epoch, sample.output.completion)
```

Cuidados:

- **Con `epochs`, el mismo `id` aparece varias veces**, una por repetición, con distinto `epoch`. Para
  contar tasas, cada par `(id, epoch)` es una observación.
- **Para detectar violaciones no alcanza con `completion`.** Hay que recorrer `sample.messages` y mirar
  qué devolvió cada `ChatMessageTool`. Para el CoT, los `ContentReasoning` de los mensajes del asistente.
- **A escala**, `inspect_ai.analysis` (por ejemplo `samples_df`) convierte logs en una tabla con una fila
  por sample. Por dentro hace este mismo doble loop.
