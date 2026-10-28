<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

A language model on its own can only produce text. It cannot check the weather, read a file or send an email. **Function calling** (also called **tool use**) is how you give it those abilities: you describe functions your code can run, the model replies with a structured request to run one, and your code does the work and reports back. This is the "act" step of the agent loop, and it is the mechanism underneath every agent you will build in this path.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a tool definition contains and why the description matters so much.
- The request, tool call, tool result round trip.
- How to tell when the model wants a tool and when it is finished.
- The difference between client tools (your code runs them) and server tools (the provider runs them).
- Forcing or forbidding tool use with tool choice settings.
- How the same idea looks across different providers.

### Key ideas

- **A tool is a name, a description and an input schema.** The schema is written in JSON Schema, the same format you used in the Structured Outputs section. The model never sees your Python code; it only sees this definition, so the description is effectively a prompt.
- **The model does not run anything.** When it decides a tool would help, the API response contains a `tool_use` block with the tool name, the arguments and an ID, and the response's `stop_reason` is `"tool_use"`. Your code reads that block, calls the real function and decides what to send back.
- **Results go back as a new message.** You append the model's response to the conversation, then add a user message containing a `tool_result` block that carries the same ID and the output as text. Then you call the API again. This round trip is the agent loop from the previous section, made concrete.
- **The loop ends when there are no more tool calls.** A `stop_reason` of `"end_turn"` means the model has given its final answer. Your step cap still applies on top of this.
- **Client tools versus server tools.** Most tools are *client tools*: you define and run them. Some providers also offer *server tools*, such as web search or code execution, that run on the provider's side and return results without any code from you.
- **Tool choice gives you control.** By default the model decides whether to call a tool (`auto`). You can require it to call some tool (`any`), a specific tool, or none at all. Forcing a specific tool is a reliable way to get structured output.
- **Every major provider works this way.** OpenAI, Google and open-model servers use slightly different field names, but the shape is identical: definitions in, structured call out, result back in.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Tool use with Claude](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview) for the big picture of how tool calls flow between your code and the model.
   - Focus on the difference between client tools and server tools.
1. Read [Define tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools) to learn exactly what goes into a tool definition.
   - Read the sections on tool definitions and on forcing tool use with `tool_choice`. Skim the rest.
1. Work through Rings 1 and 2 of the [Tutorial: Build a tool-using agent](https://platform.claude.com/docs/en/agents-and-tools/tool-use/build-a-tool-using-agent). Type the code yourself rather than copying it, and run it.
   - Ring 1 is a single tool call; Ring 2 turns it into a loop. Stop there for now. You will come back for later rings in the next two lessons.
1. Skim OpenAI's [function calling guide](https://developers.openai.com/api/docs/guides/function-calling) and list three differences in naming between its format and Claude's. Seeing a second provider makes it clear which parts are universal.
1. Practice: write a tool called `get_word_length` that returns the number of letters in a word. Ask the model "How many letters are in 'strawberry' and 'banana' combined?" Print the raw `tool_use` blocks it sends and the final answer.

</div>
