### Introduction

JavaScript, like Python, checks types only while the program runs. Misspell a field name, pass a string where a number belongs, or forget that a value might be `undefined`, and you find out when a user clicks the button and the page breaks. In a frontend with dozens of components passing data to each other, those mistakes are the most common bugs.

**TypeScript** is JavaScript with type annotations, plus a checker that reads them and reports mistakes before the code runs. You met the same idea in Type Hints: Python annotations checked by a tool such as mypy. TypeScript takes it further. Nearly every serious JavaScript codebase now uses it, including React and Next.js projects, the Vercel AI SDK and the official SDKs of the model providers. When you read a job posting that says "React", it almost always means React with TypeScript. The rest of this section is written in it.

This lesson assumes JavaScript Fundamentals. Everything you learned there is still true: TypeScript adds types on top and changes nothing about how the code behaves.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What types buy you, and what they don't.
- How to run TypeScript with Node and check it with `tsc`.
- Type annotations and type inference.
- Describing objects with interfaces and type aliases.
- Union types and narrowing.
- Generics at a basic level.
- Typing API responses, and why you still need runtime validation with zod.

### Why types

A type checker reads your code without running it and proves certain mistakes can't happen. Here's a mistake JavaScript happily runs:

```javascript
const review = { id: 1, stars: 5 };
console.log(review.author.toUpperCase()); // TypeError at runtime: author is undefined
```

TypeScript would refuse this with `'review.author' is possibly 'undefined'` before you ever ran it. You get three benefits from that:

1. **Mistakes show up as you type.** Your editor underlines them in red, the same moment you write them, instead of after a deploy.
1. **Your editor understands your data.** Type `review.` and it lists the fields that exist. Rename a field and it finds every place that used the old name.
1. **Types document the code.** A function signature such as `getRepo(fullName: string): Promise<Repo>` tells the next reader (and your AI coding assistant) what goes in and what comes out.

What types *don't* do is check data at runtime. TypeScript's types are erased before the code runs, so they can only describe what you *believe* about data that arrives from outside, such as an API response or a form field. Hold on to that; it's the point of the last teaching section.

### Running TypeScript

There are two separate jobs: **running** the code and **checking** its types. Keeping them apart is the most important practical idea in this lesson.

**Running.** Node 22.18 or newer can run `.ts` files directly, with `node main.ts`. Node does this by *type stripping*: it deletes the annotations, replacing them with spaces, and runs what's left as JavaScript. That's fast and needs no setup, but Node **does not check the types**. A file full of type errors runs anyway, and crashes the same way plain JavaScript would. The exercises for this lesson run this way.

Type stripping only works for TypeScript syntax that can be deleted cleanly. A few older features generate real JavaScript code, such as `enum` and parameter properties in classes. Node refuses those with `ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX`. Use a union of string literals instead of an `enum` (shown below), and you won't miss it.

**Checking.** `tsc`, the TypeScript compiler, reads your whole project and reports every type error. With the `noEmit` setting it writes no files and just checks, which is all you need when Node does the running. It's the TypeScript equivalent of running `mypy` or `ruff check`: it goes in your editor, in a `typecheck` script, and in CI. Bundlers such as the one inside Next.js work the same way. They strip types to build quickly and leave checking to `tsc`.

Before you set up a project, you can try anything in this lesson in the [TypeScript Playground](https://www.typescriptlang.org/play), which shows type errors in the browser as you type.

### Annotations and inference

An annotation goes after a name, with a colon, just as in Python:

```typescript
let count: number = 0;
const names: string[] = ["ada", "grace"];
function greet(name: string, greeting = "Hello"): string {
  return `${greeting}, ${name}!`;
}
```

The basic types are the JavaScript ones in lowercase: `string`, `number`, `boolean`, `null` and `undefined`. Arrays are `string[]` (or `Array<string>`, like `list[str]`).

You don't need to annotate everything. TypeScript *infers* types from values: `let count = 0` is already a `number`, and assigning `"three"` to it later is an error. The usual habit is to annotate function parameters and the things you export, and let inference handle local variables. Return types are optional too, but writing them on exported functions catches mistakes inside the function.

Two special types are worth knowing early. `any` turns checking off for a value: anything goes, and any mistake gets through. Avoid it. `unknown` means "this could be anything, so prove what it is before you use it", which makes it the honest type for data you haven't checked yet.

### Interfaces and type aliases

Most data in a web app is objects, so most of your types describe object shapes. There are two ways to write one:

```typescript
interface Review {
  id: number;
  text: string;
  author?: string; // optional: may be missing, so its type is string | undefined
}

type Sentiment = "positive" | "neutral" | "negative";
```

An `interface` names an object shape, much like a Python `TypedDict` or the fields of a Pydantic model. A `type` alias names any type at all: an object shape, a union like `Sentiment`, or a function type. For plain object shapes the two are nearly interchangeable. Pick one style per project and stay consistent. Many teams use `interface` for objects and `type` for everything else.

TypeScript checks shapes *structurally*. Any object with the right fields counts as a `Review`, whether or not anyone declared it as one. There are no classes to inherit from: if it has the shape, it fits. Python's `Protocol` works the same way. An object literal with an extra field that the type doesn't list is reported as a probable typo.

### Unions and narrowing

A *union type*, written with `|`, says a value is one of several types: `string | number`, or `Review | undefined`. Unions of literal values are especially useful. `"positive" | "neutral" | "negative"` allows exactly those three strings, which makes it a lightweight `enum`, and your editor autocompletes them.

Before you use a union value, you must show TypeScript which member you have. That's called **narrowing**. You narrow with ordinary JavaScript checks, and TypeScript follows your `if` statements:

```typescript
function label(x: string | number): string {
  if (typeof x === "string") return x.toUpperCase(); // here x is a string
  return x.toFixed(2);                               // here x is a number
}

type Result<T> =
  | { ok: true; value: T }
  | { ok: false; error: string };

function show(r: Result<number>): string {
  if (r.ok) return `got ${r.value}`; // TypeScript knows value exists here
  return `failed: ${r.error}`;       // and error exists here
}
```

The common narrowing checks are `typeof x === "string"`, comparing with `=== undefined` or `=== null`, `Array.isArray(x)` and `"field" in x`. The `Result` type shows the most useful pattern of all, a *discriminated union*. Each member has a shared field, here `ok`, with a different literal value, so checking that one field tells TypeScript which shape you have. You'll see this pattern in chat UIs everywhere: a message part is `{ type: "text"; text: string }` or `{ type: "tool-call"; toolName: string; ... }`, and you `switch` on `type`.

With `strict` mode on (always turn it on), `null` and `undefined` are not part of other types. A `string` can't be `undefined`, so anything that might be missing has to say so in its type, and you have to handle that case before you use it. This one check catches more real bugs than everything else in TypeScript put together.

### Generics

Look at `Result<T>` again. The `T` is a *type parameter*: a placeholder filled in when the type is used, so `Result<number>` holds a number and `Result<string[]>` holds a list of strings. Types and functions that take type parameters are called *generics*. You used them in Python already: `list[str]` and `dict[str, int]` are generic types, and Python 3.12's `def first[T](items: list[T]) -> T` is a generic function.

```typescript
function first<T>(items: T[]): T | undefined {
  return items[0];
}

const n = first([1, 2, 3]);      // n: number | undefined
const s = first(["a", "b"]);     // s: string | undefined
```

TypeScript infers `T` from the argument, so you rarely write it out. At this stage you'll mostly *use* generics rather than write them. The ones you'll meet constantly are `T[]` or `Array<T>`, `Promise<T>` (what an `async` function returning a `T` really returns), `Record<string, T>` (an object used as a dictionary, like `dict[str, T]`) and, in React, `useState<T>`.

### A worked example

Here's a complete file that uses most of the above. Save it as `src/reviews.ts` in the project from Setting up a project, below:

```typescript
// src/reviews.ts: run with `node src/reviews.ts`, check with `npx tsc`
interface Review {
  id: number;
  text: string;
  stars: 1 | 2 | 3 | 4 | 5; // a union of literal types: only these five numbers
  author?: string;          // optional: string | undefined
}

type Sentiment = "positive" | "neutral" | "negative";

function sentiment(review: Review): Sentiment {
  if (review.stars >= 4) return "positive";
  if (review.stars === 3) return "neutral";
  return "negative";
}

function byline(review: Review): string {
  // review.author.toUpperCase() here would be an error: author may be undefined.
  if (review.author === undefined) return "anonymous";
  return review.author.toUpperCase(); // narrowed: TypeScript knows it's a string now
}

// A generic function: works for an array of anything, and keeps the type.
function first<T>(items: T[]): T | undefined {
  return items[0];
}

const reviews: Review[] = [
  { id: 1, text: "Fast shipping, great mug", stars: 5, author: "ada" },
  { id: 2, text: "Arrived broken", stars: 1 },
];

const top = first(reviews); // type: Review | undefined
console.log(top ? `${byline(top)}: ${sentiment(top)}` : "no reviews");
console.log(reviews.map(sentiment)); // type: Sentiment[]
```

It prints `ADA: positive` and `[ 'positive', 'negative' ]`. Now break it on purpose. Delete `author: "ada"` from the first review, delete the `if` line in `byline`, and change the second review to `stars: 6`. `node src/reviews.ts` still starts, because Node only strips types, and then crashes with `TypeError: Cannot read properties of undefined (reading 'toUpperCase')`. `npx tsc` reports both mistakes, with file, line and column, without running anything:

```text
src/reviews.ts(19,10): error TS18048: 'review.author' is possibly 'undefined'.
src/reviews.ts(29,36): error TS2322: Type '6' is not assignable to type '1 | 2 | 3 | 4 | 5'.
```

### Typing API responses

Here's the trap. `await res.json()` returns `any`, because TypeScript can't know what a server will send. It's tempting to write `const repo = (await res.json()) as Repo;`. That `as` is a *type assertion*: you telling the compiler "trust me". It checks nothing at runtime. If the API changes a field name, returns an error object or sends `null`, your code carries a value labeled `Repo` that isn't one, and it fails somewhere far away from the cause.

This is the same problem you solved in Python with Pydantic, and TypeScript's answer is the same: validate data at the boundary where it enters your program. The most popular library for this is **[zod](https://zod.dev/)**, which plays Pydantic's role. You describe the shape once as a schema. zod checks real data against it at runtime and *derives the static type from the schema*, so the type and the check can never disagree:

```typescript
// src/github.ts: run with `node src/github.ts`
import * as z from "zod";

// 1. A schema describes the shape at runtime, like a Pydantic model.
const Repo = z.object({
  full_name: z.string(),
  stargazers_count: z.number().int(),
  description: z.string().nullable(), // GitHub sends null when there's none
});

// 2. The static type is derived from the schema, so the two never disagree.
type Repo = z.infer<typeof Repo>;

export async function getRepo(fullName: string): Promise<Repo> {
  const res = await fetch(`https://api.github.com/repos/${fullName}`);
  if (!res.ok) throw new Error(`GitHub said ${res.status} for ${fullName}`);
  const data: unknown = await res.json(); // unknown: we haven't checked it yet
  return Repo.parse(data); // 3. throws a ZodError if the shape is wrong
}

const repo = await getRepo("microsoft/TypeScript"); // top-level await works in modules
console.log(`${repo.full_name}: ${repo.stargazers_count} stars`);
console.log(repo.description?.slice(0, 40) ?? "(no description)");

// What a bad payload looks like: safeParse returns a result instead of throwing.
const result = Repo.safeParse({ full_name: "x/y", stargazers_count: "lots" });
if (!result.success) console.log(z.prettifyError(result.error));
```

| Pydantic | zod |
| --- | --- |
| `class Repo(BaseModel): full_name: str` | `const Repo = z.object({ full_name: z.string() })` |
| `Repo.model_validate(data)` | `Repo.parse(data)`, or `Repo.safeParse(data)` to get a result instead of an error |
| `ValidationError` | `ZodError` |
| `Repo.model_json_schema()` | `z.toJSONSchema(Repo)` |

The last line of the file prints exactly what's wrong with the bad payload: a string where a number belongs, and a missing `description`. That error points at the cause, at the moment the data arrived.

Where should you validate? Anywhere data crosses into your code from outside: API responses, JSON from `localStorage`, form input, and, in AI apps especially, a model's structured output, which can be malformed however good your prompt is. Inside your own code, between functions you wrote, plain types are enough. If your backend is the FastAPI app you built, you can also generate TypeScript types from its OpenAPI schema, but a zod check on the responses that matter most is still worth having.

### Setting up a project

A tiny TypeScript project needs a `package.json`, the compiler as a development dependency and a `tsconfig.json` with its settings. From an empty folder:

```bash
npm init -y                                  # creates package.json
npm pkg set type=module                      # use import/export modules
npm install --save-dev typescript @types/node
npm install zod
```

`--save-dev` marks packages needed only while developing, like `uv add --dev`. `@types/node` holds the types for Node's built-in modules. Then create `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "esnext",
    "module": "nodenext",
    "types": ["node"],
    "strict": true,
    "noEmit": true,
    "allowImportingTsExtensions": true,
    "erasableSyntaxOnly": true,
    "verbatimModuleSyntax": true,
    "skipLibCheck": true
  },
  "include": ["src"]
}
```

`strict` turns on the full set of checks. `noEmit` makes `tsc` a checker only, since Node runs the files. The next three keep your code compatible with Node's type stripping: you may write `import { getRepo } from "./github.ts"` with the real extension, as Node requires; `tsc` rejects syntax Node can't strip, such as `enum`; and type-only imports must say `import type { Repo } from "./github.ts"` so they can be deleted safely. `skipLibCheck` skips checking the packages' own type files, which saves time.

Finally, add two scripts with `npm pkg set scripts.start="node src/main.ts" scripts.typecheck="tsc"`. Now `npm start` runs the program and `npm run typecheck` checks it. Put `npm run typecheck` in your GitHub Actions workflow next to ruff and pytest, so a type error fails the build just as a failing test does.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Let the editor do the work

VS Code ships with TypeScript support built in, so you see errors as you type without running anything. When a type confuses you, hover over the variable to see what TypeScript inferred. Reading inferred types is the fastest way to build intuition.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [TypeScript for JavaScript Programmers](https://www.typescriptlang.org/docs/handbook/typescript-in-5-minutes.html) from the official handbook, a short tour that fits right after JavaScript Fundamentals.
1. Read three chapters of [the TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html), the official and free guide, and try the examples in the [Playground](https://www.typescriptlang.org/play).
   - [Everyday Types](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html): read all of it.
   - [Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html): read up to and including discriminated unions.
   - [Generics](https://www.typescriptlang.org/docs/handbook/2/generics.html): read the first sections, up to generic constraints. Stop there for now.
1. Read [Running TypeScript Natively](https://nodejs.org/en/learn/typescript/run-natively) from Node's docs, so you know what type stripping does and doesn't support.
1. Read the [zod basics](https://zod.dev/basics) page to see how parsing, `safeParse` and inferred types work. Compare each part with what you know from Pydantic.
1. Practice with the [TypeScript exercise set](https://github.com/espiNovah/project-mimir/tree/main/exercises/typescript). Each exercise is a starter `.ts` file plus failing tests.
   - From the `exercises/` folder, run `npm test -- typescript/<exercise>` for one exercise, or `npm test -- typescript` for the set, and make the tests pass.
   - Remember that the tests run through type stripping, so they check behavior, not types. Install TypeScript in a scratch project as in Setting up a project, or paste your solution into the Playground, to check the types too.
1. Build the project from Setting up a project, with `src/reviews.ts` and `src/github.ts` from this lesson.
   - Break `reviews.ts` as in the worked example and compare what `node` and `npx tsc` each report.
   - Add a zod schema for a response from one of your own FastAPI endpoints, call the endpoint with `fetch`, and print a readable error when the response doesn't match.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What does a type checker catch, and what can't types do at runtime?](#why-types)
- [What is the difference between running a file with node and checking it with tsc?](#running-typescript)
- [When would you use unknown instead of any?](#annotations-and-inference)
- [How does TypeScript narrow a union, and what makes a discriminated union useful?](#unions-and-narrowing)
- [What does the T in Result of T or Promise of T stand for?](#generics)
- [Why is casting a response with as unsafe, and what does zod do instead?](#typing-api-responses)
- [Which tsconfig settings keep a project compatible with Node's type stripping?](#setting-up-a-project)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- The [TSConfig reference](https://www.typescriptlang.org/tsconfig/) explains every compiler option, with examples, for when you meet a setting you don't recognize.
- Node's [TypeScript module documentation](https://nodejs.org/api/typescript.html) lists exactly which syntax type stripping supports and how it handles imports.
- The [zod documentation](https://zod.dev/) covers everything beyond the basics, including JSON Schema conversion, which is useful for model tool definitions.
