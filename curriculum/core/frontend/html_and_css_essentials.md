<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

You do not need to become a frontend developer to build AI systems, but you do need to put a face on your work. A demo that runs in a browser is far easier to share than a command-line tool, and many AI features end up inside web pages. This lesson covers the minimum: enough HTML to structure a page, enough CSS to make it readable, and enough JavaScript to send a request to your API and show the result.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- How HTML, CSS and JavaScript divide the work of a web page.
- The HTML elements you need for a simple app: headings, text, forms, buttons and lists.
- Enough CSS to lay out and style a page.
- JavaScript basics: variables, functions, events and the DOM.
- How to call an API from the browser with fetch.
- What CORS is and why your API might block your page.

### Key ideas

- **Three languages, three jobs.** HTML describes the structure and content (this is a heading, this is a form). CSS describes how it looks (colors, spacing, layout). JavaScript adds behavior (when the button is clicked, send the question to the API).
- **Use semantic HTML.** Elements like `<main>`, `<form>`, `<label>`, `<button>` and `<ul>` say what content *is*, which makes pages accessible to screen readers and easier to style. A `<label>` tied to each input is a small habit that matters.
- **A little CSS goes a long way.** Learn the box model (content, padding, border, margin), a few typography rules, and flexbox for laying things out in rows and columns. That covers most simple app layouts.
- **JavaScript reacts to events.** You select elements from the page (the *DOM*, the browser's live model of the HTML) with `document.querySelector`, listen for events such as `submit` or `click`, and update the page by changing elements' text or adding new ones. Use `textContent`, not `innerHTML`, for model output, so text that looks like HTML cannot run as code.
- **fetch talks to your API.** `await fetch("/extractions", {method: "POST", headers: {...}, body: JSON.stringify(data)})` sends a request; `await response.json()` reads the reply. Check `response.ok` and show an error message when it is false. It is the browser version of the HTTP requests you made in Python.
- **CORS controls who can call your API.** Browsers block a page on one origin (domain and port) from reading responses from another unless the server allows it, a rule called *cross-origin resource sharing*. FastAPI's `CORSMiddleware` lets you allow your frontend's origin explicitly.
- **Never put secret keys in the browser.** Anything in frontend code is visible to every user. The browser calls your backend; only the backend holds the model API key.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Work through the core modules of [MDN's Learn web development](https://developer.mozilla.org/en-US/docs/Learn_web_development), the free, authoritative course from the team behind the main web reference.
   - In [Structuring content with HTML](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content), do the basic HTML syntax, headings and paragraphs, lists, and forms lessons.
   - In [CSS styling basics](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics), do the lessons up to and including the box model.
   - In [Dynamic scripting with JavaScript](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting), do the lessons on variables, functions, events and DOM scripting.
1. Read [Using the Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch) on MDN.
   - Read the sections on making a request, setting a body and headers, checking response status, and reading the response body.
1. Read [FastAPI's CORS guide](https://fastapi.tiangolo.com/tutorial/cors/) so you know how to let your page call your API.
1. Practice: write a single `index.html` page with a textarea, a button and a results area. When you submit, it calls your LLM-Powered API (or the summarizer API from the backend lessons) with `fetch` and shows the result. Show a loading message while waiting and a readable error message if the request fails.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The Modern JavaScript Tutorial](https://javascript.info/) is a free, thorough book on JavaScript if you want to go deeper than the essentials.
