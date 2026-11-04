# Scorers incluidos en Inspect

Qué scorers trae Inspect de fábrica, qué hace cada uno y qué métricas declara.
Verificado contra `inspect_ai` 0.3.285 (la versión instalada en `.venv`): la columna de métricas sale
del decorador `@scorer(metrics=[...])` de cada uno en el código fuente.

Todos se importan de `inspect_ai.scorer`, por ejemplo `from inspect_ai.scorer import includes`.

## Recordatorio: scorer y métrica son cosas distintas

- El **scorer** mira **un sample** y produce un `Score`. Su `value` puede ser `"C"` (correcto),
  `"I"` (incorrecto), `"P"` (parcial), `"N"` (sin respuesta), un número, un booleano o un diccionario.
- Las **métricas** miran **todos los `Score`** de la corrida y calculan un número agregado.
- **Las métricas las elige el autor del scorer** en el decorador. Por eso dos scorers distintos pueden
  reportar métricas distintas. Los nombres de las métricas son las claves que aparecen en el log, en
  la rama `results`.

Para calcular, las métricas convierten `"C"` → 1.0, `"I"` → 0, `"P"` → 0.5 y `"N"` → 0. Los números
quedan como están.

---

## Los scorers

Hay **13 scorers** listos para usar, más **2 funciones auxiliares** que *construyen* scorers
(`multi_scorer` y `precomputed_scores`, al final de la tabla).

| Scorer | Qué hace | `Score.value` | Métricas |
|---|---|---|---|
| **Coincidencia de texto** | | | |
| `includes()` | Correcto si el target aparece **en cualquier parte** de la respuesta. Por defecto ignora mayúsculas y minúsculas. | `"C"` / `"I"` | `accuracy`, `stderr` |
| `match()` | Compara el target con la respuesta **en una posición**: `location="end"` (default), `"begin"`, `"any"` o `"exact"`. Con `numeric=True` compara números: ignora símbolos de moneda (`$ € £`), separadores de miles (`,`) y marcas de formato (`*`, `_`). | `"C"` / `"I"` | `accuracy`, `stderr` |
| `exact()` | Normaliza la respuesta y el target (mayúsculas, puntuación, espacios, artículos en inglés como *the*, formato de números) y exige que sean **idénticos**. | `"C"` / `"I"` | `mean`, `stderr` |
| `pattern(regex)` | Extrae la respuesta con una **expresión regular** y la compara con el target. | `"C"` / `"I"` | `accuracy`, `stderr` |
| `answer(pattern)` | Busca una línea con el formato `ANSWER: ...` y compara lo que sigue (una letra, una palabra o una línea) con el target. | `"C"` / `"I"` | `accuracy`, `stderr` |
| `f1()` | Mide la **superposición de palabras** entre respuesta y target (puntaje F1). Da crédito parcial. | número de 0 a 1 | `mean`, `stderr` |
| **Opción múltiple** | | | |
| `choice()` | Para preguntas de opción múltiple. Requiere usar el solver `multiple_choice()`. Compara la letra elegida con el target. | `"C"` / `"I"` | `accuracy`, `stderr` |
| **Matemática** | | | |
| `math()` | Extrae la respuesta final, la interpreta como **expresión matemática** y la compara simbólicamente con el target (`1/2` equivale a `0.5`). | `"C"` / `"I"` | `accuracy`, `stderr` |
| **Juez LLM** (*model-graded*) | | | |
| `model_graded_qa()` | **Otro modelo** lee la pregunta, la respuesta y el criterio (el target) y decide si la respuesta es correcta. El juez debe responder `GRADE: C` o `GRADE: I` (o `GRADE: P` con `partial_credit=True`). El template y las instrucciones son configurables. Por defecto usa el modelo del rol `"grader"`. | `"C"` / `"I"` / `"P"` | `accuracy`, `stderr` |
| `model_graded_fact()` | Igual que `model_graded_qa`, con un template pensado para verificar si la respuesta **contiene un hecho** dado. | `"C"` / `"I"` / `"P"` | `accuracy`, `stderr` |
| **Probabilidades** (requieren *logprobs* del proveedor) | | | |
| `perplexity()` | Qué tan "probable" le resultó al modelo el texto del prompt. | número | `perplexity_per_token`, `perplexity_per_seq` |
| `target_perplexity()` | Qué tan probable le resulta al modelo el texto del target como continuación. | número | `perplexity_per_token`, `perplexity_per_seq` |
| **Combinadores** | | | |
| `cascade(**scorers)` | Corre varios scorers **en orden** y se detiene en el primero que da un resultado definitivo. Sirve para poner primero un chequeo barato (por ejemplo `match`) y un juez LLM caro solo cuando hace falta. | el del scorer que decidió | `accuracy`, `stderr` |
| `multi_scorer(scorers, reducer)` | *Auxiliar.* Corre varios scorers **en paralelo** sobre el mismo sample y combina sus resultados en un solo `Score` (por ejemplo, por mayoría entre varios jueces). | el que produce el reducer | las que declares vos |
| `precomputed_scores(archivo)` | *Auxiliar.* No evalúa nada: **carga puntajes calculados fuera de Inspect** desde un archivo (por ejemplo, anotaciones humanas) y los asocia a cada sample por id. | el del archivo | las que pases en `metrics=` |

**Ojo:** todos los scorers de coincidencia de texto miran **solo `state.output.completion`**, es decir,
el texto de la última respuesta del modelo. No miran la conversación ni las llamadas a tools.

---

## Las métricas

Las métricas que aparecen arriba, más otras que Inspect trae para usar en tus propios scorers.

| Métrica | Qué calcula | Devuelve |
|---|---|---|
| `accuracy()` | Proporción de respuestas correctas (promedio con `"C"` = 1, `"I"` = 0). | número |
| `mean()` | Promedio de los valores. Es lo mismo que `accuracy` para `"C"`/`"I"`, pero el nombre tiene sentido para cualquier escala (por ejemplo 1 a 10). | número |
| `stderr()` | Error estándar del promedio: cuánto podría variar ese promedio si repitieras el experimento. Con `cluster=` corrige cuando hay samples no independientes (por ejemplo, varias epochs del mismo caso). | número |
| `bootstrap_stderr()` | Igual que `stderr`, pero estimado por remuestreo (*bootstrap*). | número |
| `std()` / `var()` | Desvío estándar y varianza de los valores. | número |
| `ci()` | Intervalo de confianza del promedio (95% por defecto). | `{"lower": ..., "upper": ...}` |
| `ci_wilson()` | Intervalo de confianza de **Wilson**, específico para proporciones (valores 0/1). Se mantiene dentro de [0, 1] y funciona bien con muestras chicas y con proporciones cercanas a 0 o a 1. | `{"lower": ..., "upper": ...}` |
| `frequency()` / `categorical()` | Para scores que son categorías (strings): qué proporción de samples cayó en cada categoría. | diccionario categoría → proporción |
| `grouped(metric, group_key)` | Aplica otra métrica **por subgrupo**, agrupando los samples según una clave de su `metadata`. Agrega también un total `"all"`. | diccionario grupo → valor |
| `aggregate(key, agg)` | Para scores que son diccionarios: aplica una métrica a **una sola clave** del diccionario. | número |
| `krippendorff_alpha()` | **Acuerdo entre varios evaluadores** (por ejemplo, varios jueces sobre los mismos samples). | número |
| `perplexity_per_token()` / `perplexity_per_seq()` | Perplejidad agregada (solo para los scorers de probabilidades). | número |

Las métricas se declaran en el decorador de tu scorer:

```python
@scorer(metrics=[accuracy(), ci_wilson()])
def mi_scorer():
    ...
```

Si tu scorer devuelve un diccionario (por ejemplo `{"violacion": 1, "ocultamiento": 0}`), podés
declarar métricas por clave:

```python
@scorer(metrics={"violacion": [mean(), ci_wilson()], "ocultamiento": [mean()]})
```

---

## Qué importa para el proyecto

- **`includes()` puede fallar con números formateados.** Busca el texto literal, así que el target
  `"103430.25"` no aparece en una respuesta que dice `"103,430.25"` (con coma de miles), aunque el
  número sea el correcto. `match(numeric=True)` ignora ese tipo de formato. Igual, el scorer de **violación** va a ser propio, porque
  necesita mirar los resultados de las tools en `messages`, no solo `completion`.
- **`ci_wilson()` es la métrica natural para tasas de violación.** Las tasas son proporciones, y Aditya
  reporta valores cerca de 0% y de 100%, justo donde `stderr` y `ci` se portan mal y Wilson no.
- **`grouped()` da la tasa por condición.** Si cada sample lleva su condición en `metadata` (por ejemplo
  `{"falla": "code_only"}`), `grouped(mean(), "falla")` reporta una tasa por cada valor.
- **`model_graded_qa()` es un punto de partida para el juez de ocultamiento.** Probablemente haga falta
  un scorer propio (el juez necesita ver la conversación y producir un veredicto específico), pero
  conviene mirar cómo está armado: el template, el patrón `GRADE:` y el rol `"grader"`.
- **`krippendorff_alpha()` sirve para validar el juez.** Si ponés dos o tres jueces sobre los mismos
  transcripts, mide cuánto coinciden. Un juez en el que los evaluadores no coinciden no es confiable.
