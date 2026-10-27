# 02 · Dataset: las condiciones del experimento

**Archivo:** `currency_eval/dataset.py` · **Tests:** `pytest tests/test_ex02_dataset.py`
**Tiempo estimado:** 45 min · **Docs:** [Datasets](https://inspect.aisi.org.uk/datasets.html)
**Original:** `ExperimentConfig` y `prompt_variant_configs()` en `runner.py`; prompts en `agents.py:204-359`
**ARENA:** equivale a `record_to_sample` (sección 1)

## Objetivos

- Representar el diseño experimental como un dataset de Inspect.
- Usar `metadata` para registrar la condición de cada sample (lo pide `CLAUDE.md`).
- Entender la diferencia entre **samples** (condiciones distintas) y **epochs** (repeticiones de la misma condición).

## Conceptos

**Sample.** Los campos que vamos a usar:
- `id`: identificador único y legible. Aparece en el visor y en los análisis; elegilo bien.
- `input`: el mensaje del usuario (un string alcanza; Inspect lo convierte en `ChatMessageUser`).
- `target`: la respuesta esperada. Acá es informativo (el monto correcto); la violación se detecta en el ejercicio 06.
- `metadata`: un dict libre. Va al log y los solvers y scorers lo pueden leer.

**Una condición, un sample.** En `runner.py`, cada `ExperimentConfig` (modelo × prompt × calculador) se
corre `n_runs` veces. En Inspect:
- **prompt × calculador → samples.** Cada combinación es un sample distinto con su metadata.
- **`n_runs` → epochs.** Inspect corre cada sample `epochs` veces y agrega los resultados. No hagas 20
  copias del sample: con epochs el log ya sabe que son repeticiones de lo mismo.
- **modelo → el flag `--model`.** El modelo no es parte del dataset.

**Los prompts viven en `data/`.** `CLAUDE.md` pide que las variantes vivan en un solo lugar. Están en
`data/prompts/main/*.txt`, copiados byte a byte de `agents.py`; `tests/test_data.py` lo verifica.
Ojo al editarlos: algunos terminan con espacios, y un editor que "limpia" los espacios al final de línea
cambia el experimento. (`.gitattributes` fija los finales de línea LF para que git en Windows no los cambie.)

**¿Por qué guardar el texto del prompt en la metadata, y no solo el nombre de la variante?** Así el log
queda autocontenido: si mañana alguien edita un `.txt`, el log viejo sigue diciendo qué prompt se usó.
Además, el solver del ejercicio 03 lo lee directo de ahí.

## Python que aparece acá

- **`pathlib.Path`:** `PROMPTS_DIR / "main" / "original.txt"` arma una ruta (el `/` está sobrecargado,
  como un mensaje binario en Smalltalk). `path.exists()` dice si el archivo existe.
- **Desempaquetar un dict (`**`):** `{"a": 1, **SCENARIO}` crea un dict nuevo con `a` más todas las claves de `SCENARIO`.
- **`itertools.product(xs, ys)`:** todas las combinaciones `(x, y)`, en orden: primero fija `x` y recorre `ys`.
- **List comprehension:** `[f(x, y) for x, y in product(xs, ys)]` es como `collect:` sobre las combinaciones.
- **`is None` vs "falsy":** `if x is None` distingue "no me pasaron nada" de "me pasaron una lista vacía".
  `if not x` las confunde. Con `build_dataset(prompt_variants=[])`, ¿qué debería pasar?

## Tarea

- **02a** `load_main_prompt(variant)`: leé el `.txt`; `ValueError` si la variante no existe.
- **02b** `make_sample(prompt_variant, calculator_variant)`: el `Sample` de una celda.
- **02c** `build_dataset(...)`: todas las celdas (o un subconjunto) en un `MemoryDataset`.

<details><summary>Pista 02c</summary>

```python
samples = [make_sample(pv, cv) for cv, pv in product(calculator_variants, prompt_variants)]
```
Ojo con el orden de `product`: los tests esperan primero todos los prompts de `StaticResponse` y después
todos los de `CodeOnly`.
</details>

## Para pensar

1. El diseño factorial de `CLAUDE.md` tiene los factores A (cláusula de falla), B (precedencia) y C (stakes).
   Con este esquema, ¿cómo agregarías un factor nuevo? (Pista: otra lista, otra dimensión del `product`,
   otra clave en la metadata, y un prompt que se *compone* en vez de leerse entero. Lo diseñamos cuando
   lleguemos al factorial.)
2. El calculador `Original` (el que ejecuta código de verdad) quedó afuera de `CALCULATOR_VARIANTS`. Leé
   en el README de Ale qué es un run "ineligible" y pensá por qué esa variante complica la medición.
