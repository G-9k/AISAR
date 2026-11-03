# `eval()`: defaults y parámetros relevantes para el proyecto

Notas de referencia sobre la función `eval()` de Inspect. Verificado contra el código fuente de la
versión instalada en `.venv` y con corridas de prueba usando `mockllm` (sin costo).

`eval()` tiene más de 60 parámetros. Acá están solo los que importan para este proyecto. La lista
completa está en el docstring: Ctrl+clic sobre `eval` en VS Code, o `inspect eval --help` en la terminal.

---

## 1. Qué pasa si no pasás un parámetro

### Lo primero: `eval()` casi nunca tira una excepción

Si algo sale mal, `eval()` **no corta tu programa con un error**. Te devuelve igual la lista de logs,
pero con `log.status == "error"` y el detalle en `log.error`. Además, el archivo de log se escribe
igual en disco.

Consecuencia: **siempre chequeá `log.status`** antes de mirar resultados. Una corrida fallida puede
pasar desapercibida si solo mirás que el código no explotó.

### `model`: el default es `NOT_GIVEN`, que no es lo mismo que `None`

```python
model: str | Model | list[str] | list[Model] | None | NotGiven = NOT_GIVEN
```

Inspect necesita distinguir dos situaciones:

- **No dijiste nada** (`NOT_GIVEN`). Inspect busca el modelo en la variable de entorno
  `INSPECT_EVAL_MODEL`.
- **Dijiste explícitamente "ningún modelo por defecto"** (`model=None`). No se busca nada. Es para
  tasks que eligen su propio modelo internamente.

`None` ya significa algo, así que hace falta otro valor que signifique "no me pasaron nada". Por eso
Inspect define el objeto especial `NOT_GIVEN`. Este idiom de Python se llama *sentinel*: un objeto
único cuyo único propósito es marcar "ausente".

Qué pasa en la práctica (probado):

| Llamada | `INSPECT_EVAL_MODEL` | Resultado |
|---|---|---|
| `eval(task)` | no definida | `status: "error"`, `model: "none/none"`, error: *No model specified (and no model environment variable defined)* |
| `eval(task, model=None)` | no definida | Igual que arriba, porque nuestra task usa `generate()` y eso necesita un modelo |
| `eval(task)` | `mockllm/model` | `status: "success"`, `model: "mockllm/model"` |

Inspect lee el archivo `.env` automáticamente, así que `INSPECT_EVAL_MODEL` se puede definir ahí.

> **Sugerencia de seguridad para el presupuesto:** si algún día ponés `INSPECT_EVAL_MODEL` en `.env`,
> usá `mockllm/model` y no un modelo pago. Si te olvidás de `--model` en una corrida, no gastás nada.

### `display`: el default es `"full"`

El valor `None` se resuelve así: primero la variable de entorno `INSPECT_DISPLAY`; si no existe,
`"full"`.

| Valor | Qué muestra durante la corrida |
|---|---|
| `"full"` (default) | Interfaz interactiva en la terminal: progreso, métricas en vivo, tokens |
| `"conversation"` | La conversación (mensajes, llamadas a tools) a medida que ocurre |
| `"rich"` | Como `full` pero sin interactividad |
| `"plain"` | Texto simple sin formato |
| `"log"` | Solo mensajes de logging |
| `"none"` | Nada |

Solo afecta la pantalla, **nunca lo que se evalúa ni lo que queda en el log**. En los tests usamos
`"none"` porque pytest corre sin que nadie mire la terminal, y la interfaz `"full"` puede chocar con
la captura de salida de pytest.

### `log_dir`: el default es `./logs`

El valor `None` se resuelve así: primero la variable de entorno `INSPECT_LOG_DIR`; si no existe,
`./logs`. Es relativo a la carpeta desde donde corrés, no a donde está el archivo de la task.

- En este proyecto, `.env.example` ya trae `INSPECT_LOG_DIR=./logs`.
- `logs/` está en `.gitignore`.
- Los tests pasan `log_dir=str(tmp_path)`, una carpeta temporal de pytest, para no ensuciar `logs/`.

Cada corrida genera un archivo con este formato:

```
2026-11-03T00-58-58-00-00_hello-currency_GyCE2eq3oaUQwx64qx2j8Y.eval
└─ fecha y hora (UTC) ──┘ └─ task ─────┘ └─ id único ───────────┘
```

---

## 2. Parámetros relevantes para el proyecto

Agrupados por para qué sirven. Los marcados con ★ son los que más probablemente uses.

### Qué correr

| Parámetro | Qué hace | Por qué importa |
|---|---|---|
| ★ `tasks` | La o las tasks a evaluar. Único parámetro obligatorio. | — |
| ★ `model` | El o los modelos. Con varios, obtenés un log por cada combinación de task y modelo. | Correr la misma celda contra Gemini 3.1 Pro, Argon, Claude, etc. y comparar. |
| ★ `task_args` | Diccionario de argumentos para la función `@task`. Ejemplo: `task_args={"condicion_a": "A2", "falla": "code_only"}`. | Si la task recibe la condición experimental como parámetro, cada celda del diseño factorial es la misma task con distintos `task_args`, sin duplicar código. |
| `model_roles` | Asigna modelos a roles con nombre, por ejemplo `{"grader": "google/..."}`. Dentro del código se piden con `get_model(role="grader")`. | El juez LLM de ocultamiento puede ser un modelo distinto del evaluado, configurable sin tocar el scorer. |
| `model_args` | Opciones específicas del proveedor (por ejemplo, `custom_outputs` de mockllm). | Sobre todo para tests con mocks. |

### Qué samples y cuántas veces

| Parámetro | Qué hace | Por qué importa |
|---|---|---|
| ★ `limit` | Corre solo los primeros N samples. | **Pilotos baratos.** CLAUDE.md pide pilotos chicos antes de escalar. |
| ★ `epochs` | Repite cada sample N veces. | Medís una *tasa* de violación: necesitás muchas repeticiones por celda. Aditya reporta porcentajes, así que para comparar con él necesitás N suficiente. |
| `sample_id` | Corre solo los samples con esos ids. | Re-correr un caso puntual que dio algo raro, sin pagar por el resto. |

### Límites por sample (la correa del agente)

| Parámetro | Qué hace | Por qué importa |
|---|---|---|
| ★ `message_limit` | Máximo de mensajes por sample. | Un agente frente a una tool que falla puede reintentar en loop. Esto lo corta, y protege el presupuesto. |
| `token_limit` | Máximo de tokens por sample (acepta `"500k"`, etc.). | Otra protección de costo, más directa que contar mensajes. |
| `time_limit` | Máximo de segundos por sample. | Evita samples colgados. |
| `cost_limit` | Máximo de dólares por sample. | Útil para el tope de $50, pero **requiere cargar los precios del modelo** (`model_cost_config`). Sin eso no hace nada. |

Si un sample llega a un límite, no se descarta: queda en el log marcado con el límite que alcanzó.
Hay que decidir cómo contarlo en el análisis (¿violó?, ¿no terminó?).

### Errores de la API

| Parámetro | Qué hace | Por qué importa |
|---|---|---|
| ★ `fail_on_error` | `True` (default): aborta al primer sample con error. `False`: nunca aborta. Un número entre 0 y 1: aborta si falla más de esa proporción. | Las APIs fallan a veces (errores 500, rate limits). Con el default, un error aislado tira abajo una corrida paga entera. Algo como `fail_on_error=0.1` es más razonable para corridas grandes. |
| `retry_on_error` | Reintenta N veces los samples con error. | Recupera fallas transitorias sin intervención. |

Ojo: "error" acá es una falla técnica (la API no respondió), no que el modelo haya violado la
restricción. Una violación es un sample exitoso con mal comportamiento.

### Concurrencia

| Parámetro | Qué hace | Por qué importa |
|---|---|---|
| `max_connections` | Cuántas llamadas simultáneas a la API del modelo. | Si la API devuelve errores de rate limit, se baja esto. |
| `max_samples` | Cuántos samples corren en paralelo (default: igual a `max_connections`). | Normalmente no hace falta tocarlo. |

### Logs y registro de la condición experimental

| Parámetro | Qué hace | Por qué importa |
|---|---|---|
| ★ `log_dir` | Carpeta donde se guardan los logs (default: `./logs`). | Una carpeta por fase o experimento (por ejemplo `logs/replicacion/`, `logs/fase1/`) ordena el análisis. |
| ★ `tags` | Lista de etiquetas para la corrida. Ejemplo: `tags=["replicacion", "piloto"]`. | Filtrar corridas después. |
| ★ `metadata` | Diccionario libre que queda en el log. Ejemplo: `metadata={"prompt_version": "v2"}`. | CLAUDE.md pide registrar condición, modelo y versión del prompt. Lo que es igual para toda la corrida va acá; lo que varía por sample va en el `metadata` de cada `Sample`. |
| `log_samples` | Si es `False`, no guarda el detalle de cada sample. | **No lo apagues.** Sin transcripts no hay análisis de ocultamiento ni de CoT. |

### Pantalla

| Parámetro | Qué hace | Por qué importa |
|---|---|---|
| `display` | Ver sección 1. `"conversation"` es muy útil para mirar qué hace el agente mientras debuggeás. | — |
| `trace` | Imprime cada interacción con el modelo en la terminal. | Debug fino del scaffold. |

### Configuración de generación del modelo (van "sueltos", por `**kwargs`)

Estos no son parámetros propios de `eval()`: se pasan como argumentos con nombre extra y Inspect se
los reenvía al modelo. Por ejemplo: `eval(task, model=..., temperature=1.0, reasoning_effort="high")`.

| Parámetro | Qué hace | Por qué importa |
|---|---|---|
| ★ `temperature` | Aleatoriedad de las respuestas. | **Pregunta abierta de la replicación:** hay que igualar la temperatura del experimento original. Es una variable de scaffold que puede cambiar la tasa de violación. |
| ★ `reasoning_effort` | Cuánto "piensa" el modelo. En Gemini 3+ Inspect lo traduce al `thinking_level` de Google. | **Otra pregunta abierta de la replicación** (configuración de thinking). Además, más o menos razonamiento podría cambiar la propensión a violar la restricción. |
| `reasoning_tokens` | Presupuesto de tokens de razonamiento. En Gemini lo traduce al `thinking_budget` (mecanismo viejo; para Gemini 3+ se prefiere `reasoning_effort`). | Alternativa a `reasoning_effort` si el original usaba un budget numérico. |
| `max_tokens` | Largo máximo de cada respuesta. | Si es muy bajo, corta respuestas y puede parecer que el modelo no terminó la tarea. |
| `seed` | Semilla aleatoria, en los proveedores que la soportan. | Reproducibilidad parcial. No todos los proveedores la respetan. |

**Sobre los thought summaries de Gemini:** Inspect los pide automáticamente
(`include_thoughts=True`) para todos los Gemini con thinking, sin que tengas que configurar nada.
Llegan como `ContentReasoning` dentro de `message.content`. El parámetro `reasoning_summary` es
**solo para modelos de OpenAI** y no afecta a Gemini.

---

## 3. Equivalencia Python ↔ terminal

Cada parámetro tiene su versión de línea de comandos: `_` pasa a `-` y se antepone `--`.

```python
eval(hello_currency(), model="mockllm/model", limit=1, epochs=5,
     display="conversation", temperature=1.0)
```

```
inspect eval currency_eval/ex00_hello.py --model mockllm/model --limit 1 --epochs 5 --display conversation --temperature 1.0
```

`task_args` en la terminal se pasa con `-T`: `-T condicion_a=A2 -T falla=code_only`.

---

## 4. Más adelante: `eval_set()`

Para la Fase 1 (24 celdas) existe una función hermana, `eval_set()`. Corre un conjunto de tasks y
modelos, y si algo falla, al re-ejecutarla **retoma solo lo que faltó** en vez de empezar de cero.
Cuando tengamos el diseño factorial armado, conviene mirarla. Para eso va a haber un ejercicio aparte.
