### Introduction

Language models produce text, but the rest of your program wants data: a dictionary with the right keys, a number that is actually a number, a date in a known format. Before you can ask a model for structured data, you need a precise way to describe what "the right shape" means. This lesson introduces two tools for that. JSON Schema is the language-neutral standard for describing JSON data, and Pydantic is the Python library that lets you describe the same thing as a class and check real data against it.

You will use both for the rest of the curriculum. The next lesson hands a Pydantic model to a model API, the Messy-Text Extractor validates every output with one, FastAPI uses the same classes to check web requests, and tool definitions for agents are written in JSON Schema.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a schema is and why AI apps need one.
- The building blocks of JSON Schema: types, properties, required fields and enums.
- How to define data models in Python with Pydantic.
- How Pydantic validates and converts incoming data.
- How to handle nested objects, lists and optional fields.
- How to add constraints, descriptions and custom validators.
- How to turn a Pydantic model into a JSON Schema and back.

### Schemas are contracts

A *schema* is a description of what valid data looks like: which fields exist, what type each one has, and which ones must be present. Think of it as a contract between two pieces of code. The code that produces data promises to follow it, and the code that consumes data can rely on it without checking every key by hand.

In ordinary software, the producer is another program you control, so the contract is mostly documentation. In AI apps, the producer is a language model, and it doesn't always keep promises. It might call a field `total_amount` one time and `total` the next, write `"twelve"` where you wanted `12`, or skip a field it wasn't sure about. A schema does two jobs here:

1. **It's an instruction.** You send the schema to the model, and it tells the model exactly what to produce.
1. **It's a check.** When the answer comes back, you validate it against the schema. If it doesn't match, you know immediately, instead of finding a `KeyError` three functions later.

### Reading JSON Schema

JSON Schema is itself written in JSON. Here is a schema for a single line on an invoice:

```json
{
  "type": "object",
  "properties": {
    "description": {"type": "string"},
    "quantity": {"type": "integer", "exclusiveMinimum": 0},
    "unit_price": {"type": "number", "minimum": 0}
  },
  "required": ["description", "quantity", "unit_price"],
  "additionalProperties": false
}
```

Read it top to bottom. The data must be an object (a JSON dictionary). It has three *properties*, each with its own small schema: a string, an integer greater than zero, and a number that can't be negative. All three are `required`. And `"additionalProperties": false` means no other keys are allowed, so a stray `"notes"` field would fail.

A handful of keywords cover most of what you'll write:

- `type`: one of `string`, `number`, `integer`, `boolean`, `array`, `object` or `null`.
- `properties` and `required`: the fields of an object, and which ones must appear.
- `items`: the schema every element of an array must match, such as `{"type": "array", "items": {"type": "string"}}` for a list of strings.
- `enum`: a fixed list of allowed values, such as `{"enum": ["low", "medium", "high"]}`.
- `description`: plain-language text explaining what a field means. Validators ignore it, but language models read it carefully.

You rarely need to write JSON Schema by hand in Python, because Pydantic generates it for you. You do need to be able to read it, because model APIs, tool definitions and error messages all speak it.

### Pydantic models

Pydantic lets you write the same contract as a Python class with type hints, which you met in the Type Hints lesson. Install it with `uv add pydantic`, then save this as `invoice.py`:

```python
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator


class LineItem(BaseModel):
    description: str
    quantity: int = Field(gt=0, description="How many units were bought")
    unit_price: float = Field(ge=0, description="Price of one unit, in the invoice currency")


class Invoice(BaseModel):
    vendor: str
    invoice_date: date = Field(description="Date printed on the invoice, ISO 8601")
    currency: Literal["USD", "EUR", "GBP", "other"]
    items: list[LineItem]                 # a nested model inside a list
    tax: float | None = None              # optional: many receipts don't show tax
    total: float

    @field_validator("vendor")
    @classmethod
    def vendor_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("vendor must not be blank")
        return value.strip()              # validators can also clean values

    @model_validator(mode="after")
    def total_matches_items(self) -> "Invoice":
        subtotal = sum(i.quantity * i.unit_price for i in self.items)
        expected = subtotal + (self.tax or 0)
        if abs(expected - self.total) > 0.01:
            raise ValueError(f"total {self.total} != items + tax ({expected:.2f})")
        return self


good = Invoice.model_validate({
    "vendor": "  Corner Cafe ",
    "invoice_date": "2026-10-02",
    "currency": "USD",
    "items": [{"description": "Latte", "quantity": "2", "unit_price": 4.5}],
    "total": 9.0,
})
print(good)
print(good.items[0].quantity + 1)   # 3: quantity is a real int now

try:
    Invoice.model_validate({
        "vendor": "Corner Cafe",
        "invoice_date": "last Tuesday",
        "currency": "usd",
        "items": [{"description": "Latte", "quantity": 0, "unit_price": 4.5}],
        "total": 9.0,
    })
except ValidationError as err:
    print(err)
```

Run it with `uv run invoice.py`. Every field is a class attribute with a type hint. `Invoice` contains a `list[LineItem]`, so the models nest exactly as the real document does. `Field(...)` attaches constraints (`gt=0` means "greater than zero") and descriptions. `Literal[...]` restricts a field to a few allowed values, the Pydantic version of `enum`.

### Validation is parsing

Look at the first result. The input had `"quantity": "2"`, a string, but `good.items[0].quantity` is the integer `2`, and `invoice_date` is a real `datetime.date` object. The vendor's extra spaces are gone too. Pydantic doesn't only *check* data, it *parses* it: it converts compatible input into the declared types and gives you back a clean object. The [Pydantic docs](https://pydantic.dev/docs/validation/latest/concepts/models/) call this "lax mode." If you want `"2"` to be rejected instead, you can turn on strict mode, but for model output the friendly conversion is usually what you want.

When conversion is impossible, Pydantic raises a `ValidationError`. The second call prints this (shortened):

```text
3 validation errors for Invoice
invoice_date
  Input should be a valid date or datetime, invalid character in year [type=date_from_datetime_parsing, input_value='last Tuesday', input_type=str]
currency
  Input should be 'USD', 'EUR', 'GBP' or 'other' [type=literal_error, input_value='usd', input_type=str]
items.0.quantity
  Input should be greater than 0 [type=greater_than, input_value=0, input_type=int]
```

Every error names the exact location (`items.0.quantity` means "the `quantity` of the first item"), what was expected and what arrived. Pydantic also collects *all* the field errors at once instead of stopping at the first. That makes these messages a perfect thing to send back to a model and say "fix these," which is exactly what you'll do in the next lesson.

Notice that `total_matches_items` didn't report anything. A `model_validator(mode="after")` runs only once every field has passed on its own, because it needs a complete object to compare fields against each other.

### Optional fields and honest schemas

Real documents are incomplete. Many receipts don't list tax, many job postings don't give a salary. How you model that is a design choice with real consequences for AI apps.

If you make `tax: float` required, you're telling the model "there is always a tax amount." When the receipt doesn't show one, the model is under pressure to produce *something*, and it may invent a plausible number. If you write `tax: float | None = None`, the model has an honest way to say "not present." The same goes for categories: an `"other"` option in `currency` gives the model an escape hatch instead of forcing it to pick the wrong one.

A good rule: make a field required only if every real example you've collected actually contains it.

### Constraints, descriptions and validators

There are three layers of rules, from simplest to most flexible:

1. **Types and constraints** such as `int`, `Literal[...]`, `Field(gt=0)` and `Field(max_length=200)`. They end up in the JSON Schema, so other tools understand them too.
1. **Descriptions** such as `Field(description="Date printed on the invoice, ISO 8601")`. They don't enforce anything, but they travel with the schema to the model. A good description removes ambiguity: "the total *including* tax" is far more useful to a model than a field called `total`.
1. **Custom validators** for rules that a schema can't express. A `field_validator` checks or cleans one field. A `model_validator` checks relationships between fields, like "the total must equal the items plus tax" or "the end date must be after the start date." These exist only in Python and don't appear in the JSON Schema, so the model never sees them. Your code is the only thing enforcing them.

The [validators page](https://pydantic.dev/docs/validation/latest/concepts/validators/) covers more variants, but `field_validator` and `model_validator(mode="after")` handle almost everything you'll need.

### From model to JSON Schema

One Pydantic class gives you everything else for free:

- `Invoice.model_json_schema()` returns the JSON Schema as a Python dictionary. Print `LineItem.model_json_schema()` and you'll see almost exactly the schema from earlier in this lesson, including your descriptions.
- `Invoice.model_validate_json(text)` parses a JSON *string*, such as the text a language model returns, straight into a validated object. It's `json.loads` and validation in one step.
- `invoice.model_dump()` turns an object back into a plain dictionary, and `invoice.model_dump_json()` into a JSON string, ready to save to a file.

So the workflow for structured output is: write the Pydantic model once, send its schema to the model, and validate the reply with the same class. You write the contract in one place, and it can't drift out of sync.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Model APIs support a subset of JSON Schema

Model providers accept JSON Schema, but usually not every keyword. For example, Claude's structured outputs don't enforce numeric bounds such as `minimum`, so the official SDK moves them into the field description and checks them after the response arrives. Keep using `Field(gt=0)` in Pydantic: validation in your own code still catches violations. The next lesson covers this in detail.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Work through [JSON Schema's step-by-step getting started guide](https://json-schema.org/learn/getting-started-step-by-step).
   - Do the whole guide. It builds one schema from scratch, covering types, required fields, nesting and arrays.
1. Read [Pydantic's getting started guide](https://pydantic.dev/docs/validation/latest/get-started/) to install Pydantic and see a model validate data.
   - Install it in a project with `uv add pydantic` and run the examples yourself.
1. Read the [Pydantic models concept page](https://pydantic.dev/docs/validation/latest/concepts/models/).
   - Read the sections on basic model usage, validation, nested models and error handling. Skip the advanced generic and dynamic model sections.
1. Read the [Pydantic JSON Schema page](https://pydantic.dev/docs/validation/latest/concepts/json_schema/) up to the end of the first few examples, to see how a model becomes a schema. Then skim the "Field validators" and "Model validators" sections of the [validators page](https://pydantic.dev/docs/validation/latest/concepts/validators/).
1. Practice: write a Pydantic model for a recipe with a title, a list of ingredients (each with a name, an optional quantity and an optional unit), a number of servings that must be positive, and a difficulty limited to three values. Add a validator that rejects a recipe with zero ingredients.
   - Print its JSON Schema and find each of your fields and constraints in it.
   - Validate three broken dictionaries (a wrong type, a missing required field, an empty ingredient list) and read each error message.
   - Validate a JSON string with `model_validate_json`, then turn the result back into JSON with `model_dump_json`.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What two jobs does a schema do in an AI app?](#schemas-are-contracts)
- [What do the `required` and `additionalProperties` keywords mean in a JSON Schema?](#reading-json-schema)
- [What happens when you validate the string `"2"` against an `int` field, and what happens with `"two"`?](#validation-is-parsing)
- [Why can making a field required push a model to invent data?](#optional-fields-and-honest-schemas)
- [Which rules end up in the JSON Schema, and which exist only in your Python code?](#constraints-descriptions-and-validators)
- [Which Pydantic method would you use to turn a model's text reply into a validated object?](#from-model-to-json-schema)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Understanding JSON Schema](https://json-schema.org/understanding-json-schema/) is the full free reference book on JSON Schema, useful when you meet a keyword you do not know.
- [Pydantic's fields page](https://pydantic.dev/docs/validation/latest/concepts/fields/) lists every option `Field()` accepts, such as defaults, aliases and string length limits.
