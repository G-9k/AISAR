# Ejercicios: aprender Inspect portando el currency experiment

Cada ejercicio enseña una pieza de Inspect y, a la vez, porta una parte del código de Ale
(`original_currency_experiment/`). Cuando pasan todos los tests, el paquete `currency_eval/`
es la réplica en Inspect, lista para correr con Gemini.

Es el mismo formato que ARENA: leés la guía, completás los `TODO` y corrés los tests. La diferencia
es que acá el resultado es código que vamos a usar de verdad.

## Preparación (una vez)

1. Activá el entorno (PowerShell, desde `AISAR/`):
   ```powershell
   .venv\Scripts\activate
   ```
   En VS Code: `Ctrl+Shift+P` → *Python: Select Interpreter* → `.venv`.
2. Instalá la extensión **Inspect AI** de VS Code (UK AISI). Sirve para ver los logs dentro del editor
   y para correr tasks con un click.
3. Copiá `.env.example` a `.env`. Por ahora no hace falta ninguna API key: todos los ejercicios
   usan `mockllm`, un modelo falso de Inspect que no cuesta nada.

## Cómo se trabaja

| Qué | Dónde |
|---|---|
| Guía de cada ejercicio (conceptos, pistas) | `ejercicios/NN_*.md` |
| Código a completar (`TODO` + `NotImplementedError`) | `currency_eval/*.py` |
| Tests | `tests/test_exNN_*.py` |
| Mis soluciones (mirá solo si te trabás, o al final para comparar) | `soluciones/currency_eval/` |

```powershell
pytest tests/test_ex01_tools.py          # los tests de un ejercicio
pytest tests/test_ex01_tools.py -k 01a   # solo una parte
pytest                                   # todo
pytest --soluciones                      # corre los tests contra mis soluciones
```

Leer los tests también es parte del ejercicio: muestran cómo se prueba código de Inspect sin gastar
plata (modelos guionados con `mockllm`, `TaskState` armados a mano). Los helpers están en `tests/helpers.py`.

## Itinerario

| Bloque | Ejercicio | Pieza de Inspect | Qué se porta |
|---|---|---|---|
| **1** | [00 Primera eval](00_primera_eval.md) | `Task`, `eval()`, logs, `mockllm`, `inspect view` | nada (calentamiento) |
| **1** | [01 Tools](01_tools.md) | `@tool`, descripción que ve el modelo | `get_fee_for_payment_method`, `get_exchange_rate` |
| **1** | [02 Dataset](02_dataset.md) | `Sample`, metadata, `MemoryDataset` | las condiciones del experimento (prompt × calculador) |
| **1** | [03 Solvers](03_solvers.md) | `@solver`, `TaskState`, `chain`, `generate(tool_calls="loop")` | elección del system prompt; primer agente |
| 2 | 04 Loop del agente | loop escrito a mano, `execute_tools`, límites | `run_single`, `CallLimitPlugin` |
| 2 | 05 Calculador | tools por sample | `CalculationAgent` (StaticResponse, CodeOnly) |
| 3 | 06 Scorer de violación | `@scorer`, `@metric` | `violations.py` |
| 3 | 07 Juez de ocultamiento | model roles, salida estructurada | `judge.py` |
| 4 | 08 Task y corridas | `@task`, epochs, `GenerateConfig`, `eval_set` | `runner.py` |
| 4 | 09 Logs y análisis | `read_eval_log`, `samples_df` | `plot_prompt_variants.py` |
| bonus | B1-B3 | `@agent` + `as_tool()`, razonamiento, `agent_bridge()` | calculador LLM fiel, CoT, ADK directo |

Los bloques 2 en adelante todavía no existen: los armo cuando termines el anterior, ajustados a cómo te fue.

**Al terminar un bloque:** avisame. Reviso tu código (no solo si pasan los tests: también estilo y
fidelidad con el original) y armo el bloque siguiente.

## Diferencias de scaffold

Portar de ADK a Inspect cambia detalles de lo que ve el modelo. Las que vayamos encontrando quedan
anotadas en [diferencias_scaffold.md](diferencias_scaffold.md). Si los resultados no coinciden con los
de Aditya, ese es el primer lugar donde mirar.
