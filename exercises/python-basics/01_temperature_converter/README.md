# 01 · Temperature converter

**Lesson:** [Functions](https://espinovah.github.io/project-mimir/#/lessons/foundations/functions)

## Task

Write two functions in `temperature_converter.py`:

- `celsius_to_fahrenheit(celsius)` returns the temperature in Fahrenheit.
- `fahrenheit_to_celsius(fahrenheit)` returns the temperature in Celsius.

Both round the result to **1 decimal place**.

```python
celsius_to_fahrenheit(100)   # 212.0
fahrenheit_to_celsius(100)   # 37.8
```

## Hints

- The formulas are `F = C × 9 / 5 + 32` and `C = (F − 32) × 5 / 9`.
- `round(number, 1)` rounds to one decimal place.
- Use `return`, not `print`. The tests check the value your function gives back.

## Run the tests

```bash
cd exercises
uv run pytest python-basics/01_temperature_converter
```

Stuck? Make the tests pass first, then compare with `solution/temperature_converter.py`.
