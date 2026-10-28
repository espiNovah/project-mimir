<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Language models produce text, but the rest of your program wants data: a dictionary with the right keys, a number that is actually a number, a date in a known format. Before you can ask a model for structured data, you need a precise way to describe what "the right shape" means. This lesson introduces two tools for that. JSON Schema is the language-neutral standard for describing JSON data, and Pydantic is the Python library that lets you describe the same thing as a class and check real data against it.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a schema is and why AI apps need one.
- The building blocks of JSON Schema: types, properties, required fields and enums.
- How to define data models in Python with Pydantic.
- How Pydantic validates and converts incoming data.
- How to handle nested objects, lists and optional fields.
- How to turn a Pydantic model into a JSON Schema.

### Key ideas

- **A schema is a contract.** It says which fields exist, what type each one is, and which are required. Code on both sides of the contract can rely on it. For AI apps the schema is also an instruction: it tells the model exactly what to produce.
- **JSON Schema is itself JSON.** A schema such as `{"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}` describes an object with a required string field. Keywords like `enum`, `minimum`, `format` and `items` add constraints. Model APIs accept JSON Schema directly, so it is worth being able to read it.
- **Pydantic models are Python classes with type hints.** You write `class Invoice(BaseModel): total: float` and Pydantic checks that real data matches. It builds on the Type Hints lesson from Foundations.
- **Validation is parsing, not just checking.** Pydantic converts compatible input (the string `"42"` into the integer `42`) and raises a `ValidationError` when it cannot, with a clear message saying which field failed and why. Those messages are useful to send back to a model when you ask it to try again.
- **Real data is nested and incomplete.** Models can contain other models (`customer: Customer`), lists (`items: list[LineItem]`) and optional fields (`phone: str | None = None`). Deciding what is optional is a design choice: an optional field lets the model say "not present" instead of inventing a value.
- **Constraints and descriptions carry meaning.** `Literal["low", "medium", "high"]` restricts values; `Field(description="ISO 8601 date")` documents intent. Both end up in the generated schema, so they guide a model as well as a human reader.
- **One model, many uses.** `Model.model_json_schema()` produces a JSON Schema, `Model.model_validate_json()` parses a model's output, and later FastAPI uses the same classes to validate API requests.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Work through [JSON Schema's step-by-step getting started guide](https://json-schema.org/learn/getting-started-step-by-step).
   - Do the whole guide. It builds one schema from scratch, covering types, required fields, nesting and arrays.
1. Read [Pydantic's getting started guide](https://pydantic.dev/docs/validation/latest/get-started/) to install Pydantic and see a model validate data.
   - Install it in a project with `uv add pydantic` and run the examples yourself.
1. Read the [Pydantic models concept page](https://pydantic.dev/docs/validation/latest/concepts/models/).
   - Read the sections on basic model usage, validation, nested models and error handling. Skip the advanced generic and dynamic model sections.
1. Read the [Pydantic JSON Schema page](https://pydantic.dev/docs/validation/latest/concepts/json_schema/) up to the end of the first few examples, to see how a model becomes a schema.
1. Practice: write a Pydantic model for a recipe with a title, a list of ingredients (each with a name, an optional quantity and an optional unit), a number of servings that must be positive, and a difficulty limited to three values. Print its JSON Schema, then try to validate three broken dictionaries and read each error message.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Understanding JSON Schema](https://json-schema.org/understanding-json-schema/) is the full free reference book on JSON Schema, useful when you meet a keyword you do not know.
