### Introduction

You do not need to become a frontend developer to build AI systems, but you do need to put a face on your work. A demo that runs in a browser is far easier to share than a command-line tool, and most AI features end up inside web pages: a chat box, a search page, a form that fills itself in. Everything you build in the rest of this section, from plain pages to React and Next.js apps, ends up as HTML and CSS in the browser.

This lesson covers the two languages that describe a page. **HTML** says what is on the page and what each piece *is*. **CSS** says how it looks and where it goes. You'll learn the elements an app needs, how forms work, the accessibility habits that make a page usable by everyone, and the layout tools (the box model, flexbox, grid and media queries) that cover almost every interface you'll build. You'll finish with a chat page that works on a phone and on a laptop. In the next lesson, JavaScript Fundamentals, you'll make it send questions to your API and show the answers.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- How HTML, CSS and JavaScript divide the work of a web page.
- Semantic HTML: choosing elements for what content is, not how it looks.
- How forms, labels and buttons work.
- Accessibility basics: keyboards, screen readers, headings and contrast.
- How CSS selects elements, and how the box model sizes them.
- Laying out pages with flexbox and grid.
- Responsive layout with a mobile-first approach and media queries.

### Three languages, three jobs

A web page is built from three languages, each with one job:

- **HTML** (HyperText Markup Language) describes structure and content: this is a heading, this is a list of messages, this is a form with a text box and a button.
- **CSS** (Cascading Style Sheets) describes presentation: colors, fonts, spacing, and where each piece sits on the screen.
- **JavaScript** adds behavior: when the button is clicked, send the question to the API and add the answer to the list.

Keeping them separate is what makes pages easy to change. You can restyle a whole site by editing CSS without touching the HTML, and a screen reader can make sense of the HTML without any CSS at all. This lesson covers the first two. JavaScript Fundamentals covers the third, including `fetch`, calling your FastAPI backend from a page (and the CORS rules that govern it), and showing model output safely.

You don't need any tools to start. Save a file called `index.html`, double-click it, and your browser opens it. Then open the browser's **developer tools** (right-click anything on the page and choose *Inspect*). The Elements panel shows the HTML the browser built and every CSS rule that applies to the selected element, and you can edit both live. You'll use it constantly.

### Semantic HTML

HTML is made of **elements**, written as tags: `<p>Hello</p>` is a paragraph, with an opening tag, content and a closing tag. Tags can carry **attributes**, such as `lang="en"` or `id="question"`, and elements nest inside each other to form a tree.

There are two ways to mark up the same page. You could build everything from `<div>` and `<span>`, generic boxes that mean nothing, and use CSS to make some of them look like headings and buttons. Or you could use **semantic** elements, which say what the content *is*: `<header>`, `<main>`, `<h1>`, `<ol>`, `<form>`, `<button>`. Both can look identical. But semantic HTML is far better, for three reasons:

1. **It's accessible.** A screen reader announces "heading level 1," "list, 4 items" or "button, Ask." It can't say anything useful about a `<div>` styled to look like a button.
1. **It comes with behavior.** A real `<button>` can be focused with the Tab key and pressed with Enter or Space. A `<div>` can't, unless you rebuild all of that yourself.
1. **It's easier to read and style.** `main`, `header` and `aside` tell the next developer, and your AI coding assistant, what each part of the page is for.

Here is the markup for a chat page over your docs chatbot, with one example exchange filled in:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Ask the docs</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header class="site-header">
    <h1>Ask the docs</h1>
    <p>Answers come only from the product handbook, with sources.</p>
  </header>

  <main class="chat">
    <h2 class="visually-hidden">Conversation</h2>
    <ol class="messages" aria-live="polite">
      <li class="message message--user">How much is the Team plan?</li>
      <li class="message message--assistant">
        <p>The Team plan costs $45 a month and includes 5 seats [1].</p>
      </li>
    </ol>

    <form class="ask" action="/ask" method="post">
      <label for="question">Your question</label>
      <div class="ask__row">
        <textarea id="question" name="question" rows="2" maxlength="500"
                  required placeholder="For example: how long do refunds take?"></textarea>
        <button type="submit">Ask</button>
      </div>
    </form>
  </main>

  <aside class="sources" aria-labelledby="sources-title">
    <h2 id="sources-title">Sources</h2>
    <ol>
      <li><strong>handbook.pdf, page 2</strong>, 3 Plans and prices</li>
    </ol>
  </aside>
</body>
</html>
```

Walk through it from the top:

- **`<!doctype html>`** tells the browser to use modern rules. **`lang="en"`** tells screen readers which language to pronounce.
- **The `<head>`** holds information *about* the page. `charset="utf-8"` makes characters such as "é" and "—" display correctly. The **viewport** line tells phones to use the real screen width instead of pretending to be a desktop and shrinking everything; without it, no responsive layout works. `<link>` loads the stylesheet.
- **`<header>`, `<main>` and `<aside>`** are *landmarks*. Screen reader users can jump straight to the main content, and there should be exactly one `<main>` per page.
- **Headings form an outline.** One `<h1>` names the page, and `<h2>`s name its sections. Don't skip levels, and never pick a heading level for its size; that's CSS's job. The "Conversation" heading is hidden on screen but still read aloud, which you'll see how to do below.
- **The conversation is an ordered list**, because messages have an order. Each message is a list item with a class saying who sent it. The `[1]` marker matches the numbered citations from Citations and Grounding, and the sources list in the `<aside>` explains it.
- **`aria-live="polite"`** asks screen readers to announce new items added to the list later, once the user stops typing. JavaScript will add the messages, and this one attribute makes them heard. ARIA attributes like this fill gaps that plain HTML can't cover; reach for them only when no native element does the job.

### Forms that work

Forms are how users give your app input, and HTML does a lot of the work for you if you let it.

- **Every input needs a label.** `<label for="question">` is tied to the input with `id="question"`. Screen readers read the label when the box gets focus, and clicking the label focuses the box, which makes small targets easier to hit. A placeholder is *not* a label: it disappears as soon as you type, and many screen readers skip it.
- **`name="question"`** is the key the value is sent under when the form is submitted, just like a field name in a JSON body.
- **Built-in validation** is free. `required` stops an empty submit and shows a message. `maxlength="500"` stops the user typing more than 500 characters, the same cap your backend should enforce (never rely only on the browser, since anyone can bypass it). There are input types for common data too: `type="email"`, `type="number"` and `type="url"` check their format and bring up the right keyboard on phones.
- **Use `<textarea>` for long text and `<input>` for one line.** A question to a chatbot can be several lines, so it gets a textarea.
- **Give every button a `type`.** Inside a form, a button defaults to `type="submit"`. Write it explicitly, and use `type="button"` for buttons that shouldn't submit, such as a "Clear" button.

Without JavaScript, submitting this form sends a `POST` request to `/ask` with the body `question=...` and loads whatever page comes back, the old-fashioned way. In JavaScript Fundamentals you'll intercept the submit, send the question with `fetch`, and update the page without reloading it. The HTML stays exactly the same.

### Accessibility basics

**Accessibility** (often shortened to *a11y*) means people can use your page whatever their abilities and devices: with a keyboard instead of a mouse, a screen reader instead of a screen, a zoomed-in browser, or a phone in bright sunlight. Accessibility is a legal requirement for many companies, and it's a sign of care that hiring managers notice. Semantic HTML already does most of the work. A handful of habits cover most of the rest:

- **Everything works from the keyboard.** Put your mouse away and press Tab. You should be able to reach every control, in a sensible order, and press it with Enter or Space. Native elements do this for you; this is the strongest argument against clickable `<div>`s.
- **Focus is visible.** When a control has keyboard focus, users must be able to see it. Never remove the focus outline without replacing it. The stylesheet below draws a clear ring with `:focus-visible`, which shows for keyboard users without flashing on every mouse click.
- **Images have text alternatives.** `<img src="chart.png" alt="Accuracy rose from 71% to 84% after reranking">` describes what the image *says*. A purely decorative image gets `alt=""` so screen readers skip it.
- **Text has enough contrast.** Light gray on white is hard to read for many people. Body text needs a contrast ratio of at least 4.5 to 1 with its background; a contrast checker tells you the ratio.
- **Color is never the only signal.** If failed answers are only shown in red, color-blind users miss it. Add an icon or the word "Failed."
- **Text can grow.** Size text in `rem` (relative to the user's chosen font size) rather than fixed pixels, so people who set a larger default size get it.

Browsers can check much of this for you. The Lighthouse panel in Chrome's developer tools runs an accessibility audit and lists problems such as missing labels and low contrast. An automated audit catches perhaps a third of real problems, though, so also try the keyboard test yourself.

### How CSS finds elements

A CSS **rule** has a **selector**, which picks elements, and **declarations**, which set properties on them:

```css
.message--user { align-self: flex-end; background: var(--accent); color: white; }
```

The selectors you'll use most are element names (`body`, `textarea`), classes (`.message`, matching `class="message"`), and **pseudo-classes** for states, such as `:focus-visible` or `:hover`. You can combine them: `.ask label` means "any `label` inside an element with class `ask`." Prefer classes for styling. They say what a thing is in your design, and they don't break when you change an element. The class names in this lesson follow a common convention, *BEM* (block, element, modifier): `ask__row` is a part of the `ask` block, and `message--user` is a variant of `message`.

When several rules set the same property on an element, the **cascade** decides which wins. Roughly: a more specific selector beats a less specific one (an ID beats a class, a class beats an element name), and when specificity ties, the rule that comes later wins. When a style isn't applying, the developer tools show the losing declaration crossed out, along with the rule that beat it.

**Custom properties** (CSS variables) keep your design consistent. Define them once on `:root`, the top of the page, as in `--accent: #1a56db;`, and use them anywhere with `var(--accent)`. Change one line and every button and bubble changes with it.

### The box model

Every element on a page is a rectangular box with four layers, from the inside out:

1. **Content**: the text or image itself.
1. **Padding**: space between the content and the border, inside the box's background.
1. **Border**: a line around the padding, which may be invisible.
1. **Margin**: space *outside* the border that pushes other boxes away.

Here's the trap that catches everyone. By default, `width` sets only the *content* width. A box with `width: 300px`, `padding: 16px` and a `1px` border actually takes up 334 pixels, which breaks layouts in confusing ways. The fix is one line that nearly every modern stylesheet starts with:

```css
*, *::before, *::after { box-sizing: border-box; }
```

With `border-box`, `width` includes the padding and border, so a 300-pixel box is 300 pixels. Two more facts are worth knowing. Elements are either **block** (like `<p>`, `<li>` and `<div>`: they start on a new line and fill the available width) or **inline** (like `<strong>` and `<a>`: they flow inside a line of text). And vertical margins between block elements *collapse*: two paragraphs with 16-pixel margins are 16 pixels apart, not 32. Flexbox and grid don't collapse margins, which is one reason to prefer their `gap` property for spacing.

Select any element in the developer tools and the Computed panel draws its box model with the exact sizes of each layer. When something is mysteriously too wide or too far away, look there first.

### Flexbox and grid

For years, laying out a page in CSS involved hacks. Today there are two tools built for the job, and between them they cover almost everything.

**Flexbox** arranges items in one direction, a row or a column. Set `display: flex` on a container, and its children become *flex items*:

- `flex-direction: row` (the default) or `column` picks the direction.
- `gap: 0.5rem` puts space between items, and never at the edges.
- `flex: 1` on an item tells it to grow and take the leftover space. In the chat form, the textarea has `flex: 1` and the button doesn't, so the box stretches and the button stays its natural size.
- `justify-content` positions items along the direction of the flex (start, center, space-between), and `align-items` positions them across it. An individual item can override the cross-axis alignment with `align-self`, which is how user messages sit on the right and assistant messages on the left of the same column.

**Grid** arranges items in two dimensions, rows *and* columns at once. Set `display: grid` and describe the tracks:

```css
body {
  display: grid;
  grid-template-columns: 1fr 18rem;    /* a flexible column and a fixed 18rem column */
  grid-template-rows: auto 1fr;        /* a header as tall as it needs, then the rest */
}
```

`fr` means "a fraction of the leftover space," so `1fr 18rem` gives the sidebar 18rem and the first column everything else. `grid-template-areas` lets you name the regions and draw the layout as text, which you'll see in the full stylesheet.

A good rule of thumb: use **grid for the page** (header, main area, sidebar) and **flexbox for components** (a row of buttons, a column of messages, a form row). They nest happily: a grid cell can be a flex container.

### Responsive layout

A **responsive** page adapts to the screen it's on. Many people will open your demo link on a phone, so it has to work on a 390-pixel-wide screen as well as on a laptop.

The reliable way to do this is **mobile first**. Write your base styles for small screens, where most layouts are a single column and need the least CSS. Then add **media queries**, blocks of CSS that apply only when a condition is true, to rearrange things on wider screens:

```css
@media (min-width: 48rem) {   /* about 768px: tablets and up */
  /* two columns instead of one */
}
```

A few other habits do much of the work without any media queries:

- **Don't set fixed widths on big things.** Let blocks fill their container, and use `max-width` to stop lines of text getting too long to read.
- **Use `min()` for limits that depend on the screen.** `max-width: min(36rem, 85%)` means "36rem, or 85% of the container on screens where that's smaller."
- **Use relative units.** `rem` for spacing and text, `%` and `fr` for widths, and `dvh` (a percentage of the visible screen height, which accounts for a phone's address bar) for full-height layouts.

Test with the device toolbar in your browser's developer tools, which shows your page at phone and tablet sizes, and then on a real phone if you have one.

### Styling the chat page

Here is the stylesheet for the chat page, `style.css`, saved next to `index.html`. On a phone, the header, conversation and sources stack in one column. From 48rem up, the sources move into a side column, and the conversation scrolls on its own while the question box stays at the bottom.

```css
/* style.css: mobile first. The base rules are for small screens. */
*, *::before, *::after { box-sizing: border-box; }   /* width includes padding and border */

:root {
  --text: #1d1d1f;
  --muted: #555;
  --surface: #f4f4f6;
  --accent: #1a56db;
  --radius: 0.75rem;
  font-family: system-ui, sans-serif;
  line-height: 1.5;
  color: var(--text);
}

body {
  margin: 0;
  min-height: 100dvh;                  /* the full visible height of the screen */
  display: grid;
  grid-template-rows: auto 1fr auto;   /* header, chat (takes the rest), sources */
}

.site-header { padding: 1rem; border-bottom: 1px solid #ddd; }
.site-header h1 { margin: 0; font-size: 1.25rem; }
.site-header p { margin: 0.25rem 0 0; color: var(--muted); }

.chat {
  display: flex;
  flex-direction: column;              /* messages above, form below */
  min-height: 0;                       /* lets the message list scroll inside the grid row */
  padding: 1rem;
  gap: 1rem;
}

.messages {
  flex: 1;                             /* grow to fill the space above the form */
  overflow-y: auto;
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.message {
  max-width: min(36rem, 85%);          /* bubbles never get too wide to read */
  padding: 0.75rem 1rem;
  border-radius: var(--radius);
}
.message p { margin: 0; }
.message--user { align-self: flex-end; background: var(--accent); color: white; }
.message--assistant { align-self: flex-start; background: var(--surface); }

.ask label { display: block; font-weight: 600; margin-bottom: 0.25rem; }
.ask__row { display: flex; gap: 0.5rem; }
.ask textarea { flex: 1; font: inherit; padding: 0.5rem; border: 1px solid #888; border-radius: 0.5rem; }
.ask button {
  font: inherit;
  padding: 0.5rem 1.25rem;
  border: 0;
  border-radius: 0.5rem;
  background: var(--accent);
  color: white;
  cursor: pointer;
}
.ask textarea:focus-visible, .ask button:focus-visible {
  outline: 3px solid var(--accent);    /* a clear focus ring for keyboard users */
  outline-offset: 2px;
}

.sources { padding: 1rem; background: var(--surface); }
.sources h2 { margin-top: 0; font-size: 1rem; }

.visually-hidden {                     /* hidden on screen, still read by screen readers */
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
}

@media (min-width: 48rem) {            /* tablets and up: sources move to a side column */
  body {
    height: 100dvh;
    grid-template-columns: 1fr 18rem;
    grid-template-rows: auto 1fr;
    grid-template-areas:
      "header header"
      "chat   sources";
  }
  .site-header { grid-area: header; }
  .chat { grid-area: chat; }
  .sources { grid-area: sources; overflow-y: auto; border-left: 1px solid #ddd; }
}
```

The parts worth studying:

- **The page is a grid; the parts are flex.** `body` is a grid of regions. Inside the chat region, a flex column puts the message list above the form, and `flex: 1` on the list makes it take all the leftover height, pushing the form to the bottom.
- **`min-height: 0` on `.chat`** is a famous fix. By default, a grid or flex item refuses to shrink below the height of its content, so a long conversation would stretch the page instead of scrolling. Setting it to zero allows the shrink, and `overflow-y: auto` on the list then adds a scrollbar.
- **The media query only changes the grid.** Below 48rem the regions stack in source order. Above it, `grid-template-areas` draws a two-column layout, the body is fixed to the screen height, and each column scrolls on its own. The HTML didn't change at all.
- **`.visually-hidden`** is a standard pattern for text that screen readers need but sighted users don't. It's not `display: none`, which would hide it from everyone.
- **The colors pass contrast.** White on `#1a56db` and `#1d1d1f` on `#f4f4f6` are both well above 4.5 to 1. If you change the palette, check the new pair.

Open `index.html` in your browser, then drag the window narrower and watch the sources jump below the conversation at the breakpoint.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Work through the core modules of [MDN's Learn web development](https://developer.mozilla.org/en-US/docs/Learn_web_development), the free, authoritative course from the team behind the main web reference.
   - In [Structuring content with HTML](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content), do the lessons on basic HTML syntax, web page metadata, headings and paragraphs, lists, structuring documents, creating links, images, and forms and buttons.
   - In [CSS styling basics](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics), do the lessons up to and including the box model, plus "Handling conflicts" and "Values and units."
   - In [CSS layout](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout), do the lessons on flexbox, CSS grid layout, responsive design and media query fundamentals.
1. Play [Flexbox Froggy](https://flexboxfroggy.com/) and [Grid Garden](https://cssgridgarden.com/), two free browser games that drill flexbox and grid properties until they're second nature.
   - Finish Flexbox Froggy. Do at least the first 15 levels of Grid Garden.
1. Read selected modules of [web.dev's Learn Accessibility course](https://web.dev/learn/accessibility), Google's free course on building accessible pages.
   - Read the modules on why accessibility matters, ARIA and HTML, content structure, keyboard focus, forms, and color and contrast.
1. Practice: build the chat page from this lesson, then make it your own.
   - Add a "Clear conversation" button that doesn't submit the form, and a third example message that shows the "I don't know" reply in a way that isn't signaled by color alone.
   - Change the color palette, and check every text and background pair with the [WebAIM contrast checker](https://webaim.org/resources/contrastchecker/).
   - Check your page at phone, tablet and laptop widths with [Chrome's device mode](https://developer.chrome.com/docs/devtools/device-mode). Then use it with only the keyboard, run a [Lighthouse](https://developer.chrome.com/docs/lighthouse/overview) accessibility audit, and fix what it reports.
   - Paste your HTML into the [W3C Markup Validation Service](https://validator.w3.org/) and fix any errors. Keep the page; in JavaScript Fundamentals you'll make it talk to your API.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What are the jobs of HTML, CSS and JavaScript?](#three-languages-three-jobs)
- [Why use a button element instead of a div styled to look like a button?](#semantic-html)
- [Why does every input need a label, and why isn't a placeholder enough?](#forms-that-work)
- [How can you check that a page works with a keyboard, and why must focus stay visible?](#accessibility-basics)
- [What are the four layers of the box model, and what does box-sizing: border-box change?](#the-box-model)
- [When would you use grid, and when flexbox?](#flexbox-and-grid)
- [What does mobile first mean, and what does a media query do?](#responsive-layout)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Josh Comeau's interactive guide to flexbox](https://www.joshwcomeau.com/css/interactive-guide-to-flexbox/) explains how flexbox actually decides sizes, with live demos you can drag.
- [CSS-Tricks' complete guide to grid](https://css-tricks.com/snippets/css/complete-guide-grid/) is a visual reference for every grid property, handy to keep open while you build. Its sister [guide to flexbox](https://css-tricks.com/snippets/css/a-guide-to-flexbox/) does the same for flexbox.
- [web.dev's Learn CSS course](https://web.dev/learn/css) goes deeper than this lesson on the cascade, specificity, sizing units and layout.
- [MDN's HTML elements reference](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements) lists every element with its meaning and accessibility notes.
