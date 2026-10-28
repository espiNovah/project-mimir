<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Now that you can describe the shape of your data, you need the model to actually produce it. There are three ways to do that: ask nicely in the prompt and hope, use the provider's native *structured outputs* feature that forces the response to match a schema, or use a library that wraps either approach with validation and retries. This lesson covers all three, and when each one is the right call.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why prompt-only JSON breaks in production.
- How native schema-constrained output works.
- How libraries such as Instructor add validation and retries on top.
- How to feed validation errors back to the model.
- The difference between a valid shape and a correct answer.
- How to design schemas that help the model rather than trap it.

### Key ideas

- **Prompt-only JSON fails sometimes, and "sometimes" is enough to break production.** Asking for JSON in the prompt works most of the time, but you will see stray prose before the JSON, markdown code fences, trailing commas and missing fields. At thousands of calls a day, a 1% failure rate is a steady stream of errors.
- **Native structured outputs constrain the model as it writes.** Claude, OpenAI and other providers let you pass a JSON Schema with the request. The provider restricts which tokens the model can produce, so the response is guaranteed to parse and match the schema. The official SDKs can also take a Pydantic model directly and return a parsed object. Check which schema features your provider supports; some keywords are not allowed.
- **Libraries add a validation loop.** Tools like Instructor wrap many providers behind one interface: you pass a Pydantic model, and the library extracts the output, validates it, and retries automatically when validation fails. This is useful for rules a schema cannot express, such as "end date must be after start date," which you write as Pydantic validators.
- **Retries work best with feedback.** When validation fails, send the model its previous output together with the exact `ValidationError` message and ask it to fix it. Cap the number of retries (two or three is typical) and log every failure so you can study it.
- **Valid is not the same as correct.** A guarantee that the output matches the schema says nothing about whether the extracted values are true. A model can fill a required `email` field with a plausible made-up address. You still need tests that compare outputs to known answers, which is what the Messy-Text Extractor project measures.
- **Design schemas for honesty.** Make fields optional (or allow `null`) when the information may not exist, add an `"unknown"` or `"other"` value to enums, and use field descriptions to explain intent. Required fields with no escape hatch push a model to invent data.
- **Put reasoning before answers.** Because models write fields in order, a schema with a `reasoning` field before the `label` field gives the model room to think before it commits, the same idea as the thinking lesson.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) in the Claude docs.
   - Read the overview, the JSON outputs examples (including the Pydantic version in Python) and the section on schema limitations. Skim the strict tool use part; you will use tools in the Agentic Systems path.
1. Read [OpenAI's structured outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs) to see the same feature from another provider.
   - Focus on the introduction, the comparison with plain JSON mode and the list of supported schemas.
1. Read the [Instructor documentation home page](https://python.useinstructor.com/) and follow its quick start.
   - Pay attention to how it handles validation errors and retries. Note that it works with many providers through the same code.
1. Practice: take the recipe model from the previous lesson. Extract a recipe from a messy blog post three ways: prompt-only JSON parsed with `json.loads`, native structured outputs, and Instructor. Add a Pydantic validator that rejects a recipe with zero ingredients. Run each approach on the same five inputs and count how many failed to parse or validate.

</div>
