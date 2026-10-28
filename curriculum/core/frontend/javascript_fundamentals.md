### Introduction

Every web browser runs exactly one programming language: JavaScript. If you want a chat box that streams an answer, a button that sends a document to your API, or a page that shows eval results updating live, some JavaScript has to run in the user's browser. Most AI products ship their interfaces in JavaScript (or TypeScript, which is JavaScript with types, and comes next), so job postings for AI engineers often ask for it.

The good news is that you already know how to program. Variables, functions, loops, lists, dictionaries, exceptions, JSON, HTTP requests and `async`/`await` all exist in JavaScript, and most of them work the way you expect from Python. This lesson teaches JavaScript by translation: for each idea, here is the Python you know and here is the JavaScript equivalent, with the few places where JavaScript surprises Python programmers called out loudly. By the end you'll be able to write a page that reads a form, calls an API with `fetch`, and shows the result, which is exactly what the rest of this section builds on.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- How to run JavaScript in the browser console and with Node.
- Variables with `let` and `const`, JavaScript's types, and why you compare with `===`.
- Functions, arrow functions, arrays and objects, and the `map`, `filter` and `reduce` methods.
- Destructuring, spread and modules with `import` and `export`.
- Promises, `async`/`await` and calling an API with `fetch`.
- Handling errors and working with JSON.
- The DOM: selecting elements, listening for events and updating the page.

### Running JavaScript

There are two places to run JavaScript, and you'll use both.

**The browser console.** Open any web page, press F12 (or Cmd+Option+I on a Mac) and click the Console tab. Type `2 + 2` and press Enter. This is a REPL (read-eval-print loop), like typing `python` with no arguments. It's the quickest way to try a line of JavaScript, and it runs inside the current page, so `document.title` shows that page's title.

**Node.** Node is a program that runs JavaScript outside the browser, the same way `python` runs `.py` files. Install the current LTS (long-term support) release from [nodejs.org](https://nodejs.org/en/download), or with your package manager, and check that you have version 22.18 or newer:

```bash
node --version      # v22.18.0 or newer
node                # a REPL, like python; press Ctrl+D to leave
node basics.mjs     # run a file, like python basics.py
```

Node also ships `npm`, its package manager. `npm` plays the role `uv` plays for Python: a `package.json` file lists a project's dependencies and scripts (like `pyproject.toml`), `npm install` downloads packages into a `node_modules` folder (like `.venv`), and `npm test` runs the project's test script. You'll use it for this lesson's exercises.

Two small things look odd at first. JavaScript prints with `console.log(...)`, not `print(...)`. And you'll see files end in `.mjs`. That tells Node the file is a *module*, which turns on the modern `import`/`export` syntax shown below. (A `package.json` with `"type": "module"` does the same for plain `.js` files, which is how the exercises are set up.)

### Variables and types

Python creates a variable the moment you assign to it. JavaScript asks you to declare it first, with one of two keywords:

- `const name = "Ada";` declares a name you won't reassign. Use it by default.
- `let count = 0;` declares a name you will reassign, such as a loop counter.

You'll also see `var` in old code and tutorials. It has confusing scoping rules, so don't use it. Statements usually end with a semicolon, and blocks use curly braces `{ }` instead of indentation. Indent anyway, for humans. Comments start with `//`.

`const` stops you reassigning the *name*, not changing the *value*. `const tags = []; tags.push("new");` is fine, just as a Python list can change while the variable still points at it.

The main types map onto Python like this:

| Python | JavaScript | Notes |
| --- | --- | --- |
| `int`, `float` | `number` | One number type. `7 / 2` is `3.5`; use `Math.floor(7 / 2)` for `//`. |
| `str` | `string` | Template literals use backticks: `` `Hi ${name}` `` is an f-string. |
| `bool` | `boolean` | Lowercase: `true`, `false`. |
| `None` | `null` and `undefined` | `undefined` means "never set", such as a missing object key; `null` means "deliberately empty". |
| `list` | array | `[1, 2, 3]` |
| `dict` | object | `{ name: "Ada", age: 36 }`; keys don't need quotes. |

Python's `and`, `or` and `not` are written `&&`, `||` and `!`.

Two surprises matter most.

**Use `===`, never `==`.** JavaScript's `==` converts types before comparing, so `"1" == 1` is `true` and `0 == ""` is `true`. `===` (strict equality) compares without converting, which is what Python's `==` does for these values. Use `===` and `!==` everywhere. Like Python's `is`, though, `===` compares arrays and objects by *identity*: `[1, 2] === [1, 2]` is `false` because they are two different arrays. JavaScript has no built-in deep equality for objects.

**Truthiness is different.** As in Python, `0`, `""`, `null` and `undefined` are falsy. Unlike Python, an empty array `[]` and an empty object `{}` are *truthy*. To check for an empty list, write `if (items.length === 0)`, not `if (!items)`.

Two operators help with missing values, and you'll meet them constantly in code that handles API responses. *Optional chaining*, `user?.address?.city`, returns `undefined` instead of crashing if `user` or `address` is missing (like a chain of `.get()` calls). The *nullish coalescing* operator `??` supplies a default: `data.title ?? "Untitled"` uses `"Untitled"` only when `title` is `null` or `undefined`.

### Functions and arrow functions

A function declaration looks like Python's `def` with braces and an explicit `return`:

```javascript
function greet(name, greeting = "Hello") {
  return `${greeting}, ${name}!`;
}
```

JavaScript has a second, shorter syntax called an *arrow function*. `const double = (x) => x * 2;` is a function that takes `x` and returns `x * 2`. When the body is a single expression, its value is returned automatically, so arrow functions do the job of Python's `lambda`. Unlike `lambda`, they can also have a full body in braces, with an explicit `return`. You'll pass arrow functions to other functions all the time, the same way you passed `key=lambda r: r["stars"]` to `sorted` in Pythonic Python.

JavaScript has no keyword arguments. Calling `greet("Ada", "Hi")` matches arguments by position only, and calling a function with too few arguments doesn't raise an error: the missing ones are just `undefined`. When a function has several options, the JavaScript habit is to take a single object, `createChat({ model, maxTokens: 500 })`, and pull out the fields with destructuring, shown next. That's how `fetch` takes its options.

### Arrays, objects and their methods

Arrays and objects are JavaScript's lists and dictionaries, and you work with them through methods. The three you'll use most replace Python's comprehensions:

- `array.map(fn)` makes a new array by calling `fn` on each item: `[f(x) for x in xs]`.
- `array.filter(fn)` keeps the items where `fn` returns something truthy: `[x for x in xs if cond(x)]`.
- `array.reduce(fn, start)` folds the array into one value, like `sum()` or `functools.reduce`.

Others worth knowing: `push` (append), `includes` (`in`), `find` (the first match, or `undefined`), `some` and `every` (`any` and `all`), `join`, `slice` and `length` (a property, not a function, so no parentheses). For objects, `Object.keys`, `Object.values` and `Object.entries` work like a dict's `.keys()`, `.values()` and `.items()`. To loop over an array, use `for (const item of items)`. Note the word `of`: there is also a `for...in` loop, but it loops over keys, which is rarely what you want for an array.

**Destructuring** pulls values out of an object or array into variables, like Python's tuple unpacking but by name. `const { text, stars } = review;` makes two variables from two fields. **Spread**, written `...`, copies an array or object into a new one, like `{**review}` and `[*items]` in Python. Together they're how JavaScript code makes changed copies instead of changing data in place, a habit React depends on.

Save this as `basics.mjs` and run it with `node basics.mjs`:

```javascript
// basics.mjs: run with `node basics.mjs`
const reviews = [
  { id: 1, text: "Fast shipping, great mug", stars: 5, tags: ["shipping"] },
  { id: 2, text: "Arrived broken", stars: 1, tags: ["shipping", "damage"] },
  { id: 3, text: "Okay, a bit small", stars: 3, tags: [] },
];

// map: like [r["stars"] for r in reviews]
const stars = reviews.map((r) => r.stars);
console.log(stars); // [ 5, 1, 3 ]

// filter: like [r for r in reviews if r["stars"] <= 2]
const unhappy = reviews.filter((r) => r.stars <= 2);
console.log(unhappy.length); // 1

// reduce: like sum(...) or functools.reduce
const total = reviews.reduce((sum, r) => sum + r.stars, 0);
console.log(`Average: ${(total / reviews.length).toFixed(2)}`); // Average: 3.00

// Chaining reads left to right, top to bottom.
const shippingTexts = reviews
  .filter((r) => r.tags.includes("shipping"))
  .map((r) => r.text.toUpperCase());
console.log(shippingTexts); // [ 'FAST SHIPPING, GREAT MUG', 'ARRIVED BROKEN' ]

// Destructuring: pull fields out by name, with a default.
const { text, stars: rating, author = "anonymous" } = reviews[0];
console.log(text, rating, author); // Fast shipping, great mug 5 anonymous

// Spread: a copy with one field changed, like {**review, "stars": 4}
const edited = { ...reviews[2], stars: 4 };
console.log(reviews[2].stars, edited.stars); // 3 4

// Equality: === compares value and type; objects compare by identity.
console.log(1 === 1, "1" === 1, "1" == 1); // true false true
console.log([1, 2] === [1, 2]); // false: two different arrays
console.log(Boolean([]), Boolean("")); // true false: empty arrays are truthy!
```

Notice `stars: rating` in the destructuring line: it reads the `stars` field into a variable named `rating`. And `author = "anonymous"` supplies a default because that field doesn't exist.

### Modules

As in Python, you split a program into files, and each file is a *module*. The difference is that a JavaScript module shares nothing unless you say so. You mark what other files may use with `export`, and bring it in with `import`:

```javascript
// github.mjs
export async function getRepo(fullName) { /* ... */ }

// main.mjs
import { getRepo } from "./github.mjs";
```

The braces list *named* exports, like `from github import get_repo`. Some modules also have one *default* export, imported without braces: `import React from "react"`. The path starts with `./` for your own files and usually includes the extension. A bare name such as `"react"` means a package installed with `npm`, the way `import httpx` finds a package that `uv` installed.

### Promises and async/await

You learned in Async Basics that waiting for the network is slow, and that `async`/`await` lets a program do other work while it waits. JavaScript is built around this idea even more than Python. A browser runs your code on a single thread that also draws the page, so code that blocked while waiting for a server would freeze the whole tab. As a result, almost every slow operation in JavaScript is asynchronous.

A slow operation returns a **promise**: an object standing for a value that will arrive later. A promise is *pending* at first, then becomes *fulfilled* with a value or *rejected* with an error. Inside an `async function`, `await somePromise` pauses that function until the promise settles, then gives you the value, or throws the error. The syntax is nearly identical to Python's:

| Python | JavaScript |
| --- | --- |
| `async def main():` | `async function main() {` |
| `await client.get(url)` | `await fetch(url)` |
| `asyncio.gather(a(), b())` | `Promise.all([a(), b()])` |
| `asyncio.run(main())` | `main()`, because the runtime's event loop is always running |

Two differences matter. First, there's no `asyncio.run`: the *event loop* (the scheduler that resumes paused functions when their promises settle) is always running in the browser and in Node, so you just call an async function. Second, a JavaScript promise starts working immediately when you create it, while a Python coroutine does nothing until you await it. Calling `getRepo("a")` sends the request right away, even before any `await`.

The most common bug is forgetting `await`. `const data = res.json();` gives you a pending promise, not the data, and printing it shows `Promise { <pending> }`. If you see that, look for a missing `await`.

You'll also see older code that chains promises with `.then(...)`, such as `fetch(url).then((res) => res.json())`. It does the same thing as `await`. Prefer `async`/`await`, but recognize `.then` when you read it.

### Calling an API with fetch

`fetch` is the built-in HTTP client in browsers and in Node, the JavaScript counterpart of `httpx` from Working with APIs. `await fetch(url)` resolves to a `Response` as soon as the status and headers arrive. The body comes separately, so you read it with a second `await`:

- `await res.json()` reads the body and parses it as JSON, like `response.json()` in httpx.
- `await res.text()` reads it as a string.
- `res.body` is the body as a *stream*, delivered in chunks as they arrive. You'll use it in Streaming in the Browser to show a model's answer token by token.

You can read the body only once, so pick one of these.

Here is a small module that fetches a repository from GitHub's public API, and a script that uses it. Save both files in one folder and run `node main.mjs`:

```javascript
// github.mjs: a module. Only what you export is visible to other files.
const API = "https://api.github.com";

export async function getRepo(fullName) {
  const res = await fetch(`${API}/repos/${fullName}`, {
    headers: { Accept: "application/vnd.github+json" },
  });
  if (!res.ok) {
    // fetch only rejects on network failure. A 404 or 500 still "succeeds",
    // so check the status yourself, like response.raise_for_status() in httpx.
    throw new Error(`GitHub said ${res.status} for ${fullName}`);
  }
  const data = await res.json(); // read the body and parse it as JSON
  return { name: data.full_name, stars: data.stargazers_count };
}
```

```javascript
// main.mjs: run with `node main.mjs`
import { getRepo } from "./github.mjs"; // note the ./ and the file extension

async function main() {
  // One request: await pauses this function until the promise settles.
  const repo = await getRepo("python/cpython");
  console.log(`${repo.name} has ${repo.stars} stars`);

  // Several at once, like asyncio.gather. Total time is about the slowest request.
  const names = ["nodejs/node", "microsoft/TypeScript"];
  const repos = await Promise.all(names.map((n) => getRepo(n)));
  for (const { name, stars } of repos) console.log(name, stars);

  // Errors from await are caught with an ordinary try/catch.
  try {
    await getRepo("no-such-owner-xyz/no-such-repo");
  } catch (err) {
    console.error("Failed:", err.message);
  } finally {
    console.log("Done.");
  }
}

main();
```

To send data, as you will to your own FastAPI backend, pass a method, headers and a body. The body must be a string, so you convert the object to JSON yourself:

```javascript
const res = await fetch("/summaries", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ text: "A long article..." }),
});
```

A path that starts with `/` goes to the same server that served the page. If your page and API live on different *origins* (a scheme, host and port, such as `http://localhost:5173` and `http://localhost:8000`), the browser blocks the page from reading the response unless the API allows it. That rule is called CORS, and FastAPI's `CORSMiddleware` is how your API allows it. Serving the page from the API itself, as Streaming in the Browser does, avoids the problem.

<div class="lesson-note lesson-note--critical" markdown="1">

#### Never put an API key in browser code

Every user can read every line of JavaScript your page sends them, in the browser's developer tools. A model API key in frontend code is a public key. The browser calls *your* backend, and only the backend holds the key, read from the environment as in API Keys and Secrets.

</div>

### Errors and exceptions

JavaScript's exceptions work like Python's with different words. `throw new Error("message")` is `raise ValueError("message")`. `try { } catch (err) { } finally { }` is `try`/`except`/`finally`. There's only one `catch` per `try`, so instead of several `except` clauses you check inside it, for example `if (err.name === "AbortError")`. Every error has a `.message` and a `.stack` (the traceback).

When an awaited promise rejects, `await` throws, so `try`/`catch` around `await` handles async errors exactly as it handles ordinary ones. Two traps catch Python programmers:

- **`fetch` doesn't throw on HTTP errors.** It rejects only when no response arrives at all: the network is down, the server is unreachable or CORS blocked it. A `404` or `500` is a successful `fetch` with `res.ok === false`. Always check `res.ok` (true for status 200–299), as `getRepo` does.
- **A rejected promise nobody awaits** is reported as an "unhandled promise rejection". In Node this crashes the program, and in the browser it shows up only in the console. Make sure every promise is awaited or returned somewhere that handles errors.

### JSON in and out

JSON's syntax comes from JavaScript objects, so it fits the language naturally. `JSON.stringify(value)` turns a value into a JSON string, like `json.dumps`, and `JSON.stringify(value, null, 2)` pretty-prints it with two-space indentation. `JSON.parse(text)` turns a JSON string back into a value, like `json.loads`, and throws a `SyntaxError` on invalid input. You'll use `JSON.parse` directly when a response arrives as text, as each streamed event does in Streaming in the Browser.

A few things don't round-trip. `undefined` values and functions are left out when stringifying, and a `Date` becomes a string that stays a string when you parse it back. Most importantly, `JSON.parse` and `res.json()` trust whatever arrives. If the API sends `{"stars": "lots"}`, nothing complains until your code tries to do arithmetic with it. TypeScript Basics shows how to check data at that boundary, the way Pydantic checks it in Python.

### The DOM

When the browser loads an HTML page, it builds a tree of objects, one for each element, called the **DOM** (Document Object Model). JavaScript changes what's on screen by changing that tree. Three operations cover most of what you'll do:

1. **Select** an element with `document.querySelector(cssSelector)`, using the same selectors as CSS: `"#answer"` for an id, `".card"` for a class, `"form button"` for a button inside a form. It returns the first match, or `null`. `document.querySelectorAll` returns every match.
1. **Listen** for events with `element.addEventListener("submit", handler)`. The browser calls `handler` with an event object every time the event happens: `click`, `submit`, `input` (on every keystroke) and so on.
1. **Update** the element. Set `element.textContent` to change its text, toggle `element.disabled` on a button, or build new elements with `document.createElement("li")` and add them with `list.append(item)`.

Here is a page that uses `github.mjs` from above. Save it as `index.html` in the same folder:

```html
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Repo stars</title></head>
<body>
  <form id="lookup">
    <label for="repo">Repository</label>
    <input id="repo" value="python/cpython" required>
    <button>Look up</button>
  </form>
  <p id="result"></p>
  <ul id="looked-up"></ul>

  <script type="module">
    import { getRepo } from "./github.mjs"; // the same module Node used

    const form = document.querySelector("#lookup");
    const input = document.querySelector("#repo");
    const result = document.querySelector("#result");
    const list = document.querySelector("#looked-up");

    form.addEventListener("submit", async (event) => {
      event.preventDefault(); // stop the browser's default: reloading the page
      const button = form.querySelector("button");
      button.disabled = true; // no double submits while waiting
      result.textContent = "Loading...";
      try {
        const { name, stars } = await getRepo(input.value.trim());
        result.textContent = `${name}: ${stars.toLocaleString()} stars`;
        const item = document.createElement("li");
        item.textContent = name;
        list.prepend(item); // newest first
      } catch (err) {
        result.textContent = `Error: ${err.message}`;
      } finally {
        button.disabled = false;
      }
    });
  </script>
</body>
</html>
```

Browsers won't load modules from a page opened as a file, so serve the folder with Python's built-in web server, `python3 -m http.server 8000`, and open `http://localhost:8000`. Try a real repository, then a made-up one, and watch the error path work. Open the console too: any mistake in your script shows up there with a line number.

Notice two habits from this example. A form's default behavior is to send the data and reload the page, so a script-driven form calls `event.preventDefault()` first. And text from outside your code always goes in with `textContent`. Its alternative, `innerHTML`, parses the string as HTML, so text from a user, an API or a model that contains `<img src=x onerror=...>` would run as code in your user's browser. That attack is called cross-site scripting (XSS), and model output is just as untrusted as user input.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [JavaScript language overview](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Language_overview) on MDN, a fast tour written for people who already program in another language.
   - Read it all. Compare each section with the Python you know, and try any line that surprises you in the browser console.
1. Work through Part 1 of [The Modern JavaScript Tutorial](https://javascript.info/) for depth on the language itself.
   - Read [Data types](https://javascript.info/types), [Comparisons](https://javascript.info/comparison), [Arrow functions, the basics](https://javascript.info/arrow-functions-basics), [Array methods](https://javascript.info/array-methods), [Destructuring assignment](https://javascript.info/destructuring-assignment) and [Modules, introduction](https://javascript.info/modules-intro). Skim the rest of the chapters around them as needed.
1. Learn promises properly, because everything with a network in it depends on them.
   - Read [Promises, async/await](https://javascript.info/async) on javascript.info, chapters 1 to 8. Skip the "Promisification" and "Microtasks" chapters on a first pass.
   - Then read [Using the Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch) on MDN: making a request, setting a body and headers, checking response status and reading the response body.
1. Read [DOM scripting introduction](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/DOM_scripting) and [Introduction to events](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/Events) from MDN's Learn web development course, and do their exercises in the browser.
1. Practice with the [JavaScript exercise set](https://github.com/espiNovah/project-mimir/tree/main/exercises/javascript). Each exercise is a starter file plus failing tests that run with Node's built-in test runner. There's nothing to install beyond Node.
   - From the `exercises/` folder, run `npm test -- javascript/<exercise>` for one exercise, or `npm test -- javascript` for the whole set, and make the tests pass.
1. Build a page that talks to your own backend. Extend `index.html` from this lesson so it sends text to an endpoint in your LLM-Powered API (or the summarizer from FastAPI Basics) with a `POST` request and a JSON body, and shows the reply.
   - Show a loading message, disable the button while waiting, and show a readable error when `res.ok` is false. Stop the API and confirm the network-error path works too.
   - Serve the page from FastAPI with `StaticFiles` so page and API share an origin, or add `CORSMiddleware` for the page's origin.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why should you compare values with === instead of ==, and what does === do with two arrays?](#variables-and-types)
- [Which values are truthy in JavaScript but falsy in Python?](#variables-and-types)
- [How do map, filter and reduce correspond to Python comprehensions and functions?](#arrays-objects-and-their-methods)
- [What is a promise, and what happens if you forget to await one?](#promises-and-async-await)
- [Why must you check res.ok after a fetch, and how do you read the response body?](#calling-an-api-with-fetch)
- [Why should text from an API or a model be added with textContent and not innerHTML?](#the-dom)
- [What do JSON.parse and JSON.stringify do, and what don't they check?](#json-in-and-out)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Eloquent JavaScript](https://eloquentjavascript.net/) is a free, well-loved book that goes deeper into the language, with exercises you can run in the browser.
- MDN's [JavaScript Guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide) is the reference-style companion to everything in this lesson. Keep it open while you work.
- [Node.js's own introduction](https://nodejs.org/en/learn/getting-started/introduction-to-nodejs) explains how Node differs from the browser and what `npm` does.
