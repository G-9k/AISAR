# Plan: separar el tutorial del producto

Hoy el repo mezcla dos cosas: **el port de Ale a Inspect**, que es el producto del proyecto, y el
**andamiaje de los ejercicios** con que lo construimos (guías, stubs, soluciones, notas). La idea es
separarlas en dos ramas que nunca se vuelven a unir:

- **`main`: el producto.** La réplica, y después el diseño factorial. Código limpio, sin `TODO` ni guías.
- **`tutorial`: el curso.** Un camino para aprender Inspect replicando el experimento de Ale, con los
  stubs vacíos, las guías, los tests y las soluciones. Sirve para que otra persona haga lo mismo que hiciste vos.

## Cuándo hacerlo

**Recomendación: al terminar el bloque 4 (ejercicios 08 y 09) y antes de la primera corrida paga.**

- **No antes**, porque los ejercicios que faltan siguen construyendo el producto. Separar ahora obliga a
  mantener dos copias de todo lo que se agregue.
- **No después de correr**, porque los resultados de la réplica tienen que salir del código limpio de
  `main`, que es el que vas a mostrarle a tu mentor y eventualmente publicar.
- Los ejercicios bonus (B1 a B3) se pueden sumar al tutorial más adelante, o quedar afuera.

## Qué va en cada rama

| Qué | `tutorial` | `main` | Nota |
|---|---|---|---|
| `currency_eval/*.py` | **stubs** (`TODO` + `NotImplementedError`) | tu código, limpio | ver "El problema de los stubs" |
| `currency_eval/ex00_hello.py` + su test | sí | no | es solo un calentamiento |
| `ejercicios/NN_*.md`, `ejercicios/README.md` | sí | no | el README pasa a ser el README del tutorial |
| `ejercicios/diferencias_scaffold.md` | sí | **sí**, en `docs/` | es documentación de la investigación, no del curso |
| `soluciones/` | sí | no | |
| `conftest.py` (opción `--soluciones`) | sí | no | en `main` no hay soluciones aparte |
| `tests/test_exNN_*.py` | sí | sí, renombrados (`test_tools.py`, `test_agent.py`, ...) | sacar las referencias a guías y ejercicios |
| `tests/helpers.py`, `tests/fixtures/`, `tests/test_data.py` | sí | sí | |
| `tutorial_inspect/` (notas, mapas HTML) | sí | no | material de estudio |
| `arena_running_evals_with_inspect.txt` | no | no | es una copia de material de ARENA: mejor un link |
| `original_currency_experiment/` | sí | sí | lo usan los tests (prompts byte a byte, test diferencial del 06). Licencia Apache 2.0: se puede redistribuir con su `LICENSE` |
| `data/` | sí | sí | |
| `CLAUDE.md` | uno propio del tutorial | sí | ver "Para que otros lo puedan usar" |
| `pyproject.toml` | versión de Inspect **fija** (`inspect_ai==0.3.285`) | `>=` | el tutorial está verificado contra esa versión, e Inspect cambia rápido |
| `README.md` | el del tutorial | uno del producto, en inglés | qué es, cómo correrlo, resultados |
| `plan_rama_tutorial.md` (este archivo) | no | no | se borra cuando el plan se ejecutó |

## El problema de los stubs

En `tutorial`, `currency_eval/` tiene que tener los stubs **vacíos**, no tus respuestas. Pero en el
historial los stubs viven en distintos commits:

- **Bloque 1** (00 a 03): están en el primer commit, `c4f0790` (verificado: tiene los `NotImplementedError`).
- **Bloque 2 en adelante**: cada bloque llega como stubs nuevos, sin commitear. **Hay que commitear cada
  bloque apenas llega, antes de empezar a resolverlo**, para que la versión vacía quede en el historial. El
  bloque 2 (`agent.py` y `calculator.py`) está en esa situación ahora.

Las guías y los tests, en cambio, hay que tomarlos de la **última** versión, porque se fueron corrigiendo
(por ejemplo, la guía del 02 y el test de orden del 02c). Entonces, en la rama `tutorial`:
`currency_eval/*.py` sale del commit en que llegó cada bloque, y todo lo demás queda como está en la punta.

## Pasos

1. **En `main`, con todos los ejercicios resueltos:** que pasen `pytest` y `pytest --soluciones`. Commit.
2. **Crear la rama:** `git switch -c tutorial`.
3. **Armar el tutorial:**
   - Restaurar los stubs de cada bloque: `git checkout <commit-del-bloque> -- currency_eval/<archivo>.py`.
   - Fijar la versión de Inspect en `pyproject.toml`.
   - Promover `ejercicios/README.md` a `README.md` y escribir el `CLAUDE.md` del tutorial.
   - Sacar `arena_running_evals_with_inspect.txt` (dejar el link a ARENA en el README).
   - **Verificar:** `pytest --soluciones` pasa entero, y `pytest` falla solo con mensajes
     `"Ejercicio NN: falta completar ..."`. Commit.
4. **Volver a `main` y limpiar:** `git switch main`.
   - Antes de borrar nada: `git tag mis-soluciones`, para tener a mano tu versión con los comentarios de los ejercicios.
   - Borrar lo que la tabla marca como "no" en `main`.
   - Renombrar los tests y simplificar `conftest.py`.
   - Reemplazar los comentarios `TODO` en español por docstrings en inglés (`CLAUDE.md` pide código en inglés).
   - Mover `diferencias_scaffold.md` a `docs/` y escribir el README del producto.
   - **Verificar:** `pytest` pasa entero. Commit.
5. **Subir las dos ramas:** `git push -u origin tutorial` y `git push`.

**Regla para después:** las ramas no se mergean. Si aparece un bug en algo compartido (un test, un archivo
de `data/`), se arregla en `main` y se lleva a `tutorial` con `git cherry-pick`.

**Alternativa que descarté:** una sola rama con marcadores en el código (`# BEGIN SOLUTION` / `# END SOLUTION`)
y un script que genera los stubs, como hacen algunos cursos. Tiene una sola fuente de verdad, pero es más
maquinaria de la que necesita un tutorial que queda congelado.

## Para que otros lo puedan usar

- **Claude como tutor.** Vos aprendiste con Claude dando pistas en vez de soluciones. Un `CLAUDE.md` propio
  del tutorial puede pedir lo mismo para cualquiera: no completar los stubs, dar pistas, explicar con
  ejemplos. Sin eso, Claude probablemente resolvería los ejercicios directamente.
- **Sacar lo personal.** Las guías mencionan a Gonzalo, al mentor, las analogías con Smalltalk y el
  presupuesto de $50. Las analogías se pueden quedar como estilo; el resto conviene generalizarlo.
- **Idioma.** Las guías están en español, lo que encaja con la comunidad de AISAR. Traducirlas es opcional.
- **Costo cero hasta el 08.** Todos los ejercicios hasta el 08 usan `mockllm`, así que nadie necesita una
  API key para seguirlos. Vale la pena decirlo en el README.
- **Preguntas abiertas.** Las decisiones de fidelidad (nombre y descripción del calculador, etc.) quedan
  como preguntas en el tutorial; en `main` ya están tomadas y documentadas en `docs/diferencias_scaffold.md`.
- **Licencias y créditos.** El código de Ale es Apache 2.0: mantener su `LICENSE` e indicar que los prompts
  en `data/` vienen de ahí. Los textos del calculador vienen del repo de Aditya (licencia MIT): ya están
  citados en `tests/test_data.py`, y conviene citarlos también en el README. El repo de GitHub
  (`G-9k/AISAR`) es público, y hoy incluye la copia del texto de ARENA: revisá su licencia o reemplazala por
  un link.
- **Avisarles.** Antes de difundir el tutorial, conviene avisarles a Ale y a Aditya: es su experimento.
