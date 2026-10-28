<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

In the Foundations path you made your first API calls and wrote your first system prompts. Now it is time to get deliberate about it. A prompt is the program you hand a language model, and like any program it can be clear or confusing, tested or untested. This lesson covers the core habits that make prompts work reliably: being explicit, showing examples, and giving your prompt a structure the model can follow. These habits apply to every provider, not just Claude.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why clear, specific instructions beat clever wording.
- How to give the model context: who the audience is, what the output is for, and what "good" looks like.
- How few-shot examples steer format and tone.
- How XML tags separate instructions from data.
- How roles and system prompts set behavior.
- Why you should treat prompts as code you test, not text you guess at.

### Key ideas

- **Write for a brilliant new hire.** The model has no memory of your project, your users or your taste. If a smart colleague who had never seen your codebase would need more detail to do the task well, so does the model. State the goal, the audience, the constraints and the output format.
- **Say what to do, not only what to avoid.** "Respond in two short paragraphs of plain prose" works better than "don't use markdown." Explaining *why* a rule exists ("this text is read aloud by a speech engine, so avoid symbols") helps the model generalize the rule to cases you did not list.
- **Examples are the strongest steering tool you have.** Two to five well-chosen input/output examples (called *few-shot* prompting) pin down format and edge-case handling faster than paragraphs of description. Make them varied, or the model will copy surface details such as length or wording.
- **Use XML tags to separate the parts of a prompt.** Wrapping material in tags like `<instructions>`, `<document>` and `<example>` makes it obvious what is a command and what is data. It also lets you ask for output inside tags (`<answer>`) that your code can extract with a simple string search.
- **System prompts set the role and the rules.** Put stable behavior (persona, tone, hard constraints) in the system prompt and the specific task in the user turn. A short role such as "You are a support triage assistant for a SaaS billing product" focuses the model's knowledge.
- **Modern models follow instructions literally.** Current models do what you ask, not what you meant. If you want ambitious output, ask for it; if you want only a suggestion and no edits, say so.
- **Prompts are code.** Keep them in files under version control, change one thing at a time, and check changes against a fixed set of test inputs. Your gut feeling about a prompt is not a measurement. The Prompt Lab project at the end of this section turns this idea into practice.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Anthropic's prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices), the living reference for prompting current Claude models.
   - Read the general principles, the sections on examples and XML tags, and the parts on output format. Skim the rest; you will come back to the thinking and long-context parts in the next two lessons.
1. Work through [Anthropic's interactive prompt engineering tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial). It is a set of notebooks with exercises that check your answers.
   - Do chapters 1 through 7 (basic structure through few-shot examples).
   - The tutorial was written for Claude 3 models. When it disagrees with the current docs, follow the current docs, and swap in a current model ID such as `claude-haiku-5-5`.
1. Read [OpenAI's prompt engineering guide](https://developers.openai.com/api/docs/guides/prompt-engineering) to see that the same principles hold across providers.
   - Focus on the sections about message roles, few-shot learning and formatting with Markdown and XML.
1. Practice: pick a small task, such as rewriting product reviews into one-sentence summaries. Write a one-line prompt, run it on five inputs, then rewrite the prompt using what you learned (context, format spec, two examples, XML tags). Compare the outputs side by side and write down what changed.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Anthropic's prompt engineering overview](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview) explains when prompting is the right lever and when it is not, and how to set success criteria before you start.
