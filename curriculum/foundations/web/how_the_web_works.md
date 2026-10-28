### Introduction

Every language model you will use in this curriculum lives on someone else's computer. When your code "asks Claude a question," what actually happens is that your program sends a carefully formatted message across the internet to a server, waits, and reads the reply. The same is true for weather data, GitHub, payment systems and almost every tool an agent will ever call.

That message format is called HTTP. You don't need to become a networking expert, but you do need a clear picture of what a request and a response look like, because you will be reading them, debugging them and handling their failures for the rest of your career. This lesson gives you that picture.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What clients and servers are, and how they talk.
- The parts of a URL.
- The anatomy of an HTTP request: method, path, headers and body.
- The anatomy of an HTTP response: status code, headers and body.
- What the main groups of status codes mean.
- How to make and inspect requests from the terminal with `curl`.

### Clients, servers and HTTP

A **client** is any program that asks for something. A **server** is a program that waits for requests and answers them. Your web browser is a client. So is a Python script that fetches the weather. The machine at the other end, the one that has the weather data, is running a server.

They communicate using **HTTP** (HyperText Transfer Protocol). A protocol is just an agreed-upon format, like the rules for addressing an envelope. HTTP is a *request/response* protocol: the client always speaks first, sending one request, and the server sends back exactly one response. Then the conversation is over. The server does not remember you between requests unless you send something (like an API key or a cookie) that identifies you each time. This property is called being **stateless**, and you will meet it again when you discover that language model APIs don't remember your previous messages either.

**HTTPS** is HTTP wrapped in encryption, so nobody between you and the server can read or change the message. Everything you do in this curriculum will use HTTPS.

### Anatomy of a URL

A URL (Uniform Resource Locator) tells the client where to send a request. Take this one:

```text
https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current=temperature_2m
```

- `https://` is the **scheme**: which protocol to use.
- `api.open-meteo.com` is the **host**: which server to contact.
- `/v1/forecast` is the **path**: which resource on that server you want. APIs often put a version number like `v1` in the path so they can change things later without breaking old clients.
- Everything after the `?` is the **query string**: a list of `key=value` **parameters**, separated by `&`, that fine-tune the request.

Some characters (spaces, `&`, non-English letters) can't appear raw in a URL, so they get **URL-encoded**. A space becomes `%20`, for example. Libraries will do this for you, which is one reason we will use one in the next lesson instead of gluing strings together.

### Requests and responses

An HTTP request is plain text with a few parts:

```text
GET /v1/forecast?latitude=52.52&longitude=13.41 HTTP/1.1
Host: api.open-meteo.com
Accept: application/json
User-Agent: curl/8.7.1
```

- The first line holds the **method** (`GET`), the path, and the HTTP version.
- The lines after it are **headers**: `Name: value` pairs carrying extra information, such as which formats the client accepts or which credentials it's using.
- An optional **body** comes after a blank line. `GET` requests usually have no body; requests that send data do.

The methods you'll use most:

| Method | Meaning | Typical use |
| --- | --- | --- |
| `GET` | Read something | Fetch a forecast, list your repositories |
| `POST` | Create something or run an action | Send a message to a language model |
| `PUT` / `PATCH` | Replace or update something | Edit a record |
| `DELETE` | Remove something | Delete a file |

Here's a key fact for later: every call to a model API is a `POST` request with a JSON body containing your messages, and a response with a JSON body containing the model's reply.

The response looks similar:

```text
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: 263

{"latitude":52.52,"longitude":13.419998,"current":{"time":"2026-10-28T12:00","temperature_2m":9.1}}
```

The first line has a **status code** (`200`) and a short reason (`OK`). Then come headers, a blank line, and the body. `Content-Type` tells you how to read the body; `application/json` means it's JSON, the format you learned in the Files and JSON lesson.

### Status codes

The status code is a three-digit number that tells you, before you read anything else, how things went. The first digit is the group:

- **2xx, success.** `200 OK` is the usual one. `201 Created` means something new was made.
- **3xx, redirection.** The thing you want is somewhere else. Most tools follow redirects for you.
- **4xx, client error: you did something wrong.** `400 Bad Request` (your request was malformed), `401 Unauthorized` (missing or bad credentials), `403 Forbidden` (you're known but not allowed), `404 Not Found`, and `429 Too Many Requests` (slow down, you're being rate limited).
- **5xx, server error: they did something wrong.** `500 Internal Server Error`, `503 Service Unavailable`. Some APIs add their own; Anthropic's API uses `529` to mean "overloaded."

This split matters enormously for writing reliable software. A 4xx error usually means retrying the exact same request will fail again, so you need to fix something. A 429 or 5xx error is often temporary, so waiting and retrying is a sensible response. You'll build exactly that logic in the Tokens, Cost and Rate Limits lesson.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Read the body of an error

When a request fails, don't stop at the status code. Most APIs put a JSON explanation in the error response body, such as `{"error": {"type": "invalid_request_error", "message": "max_tokens: field required"}}`. That message usually tells you exactly what to fix.

</div>

### Making requests with curl

`curl` is a command-line client that ships with macOS, Linux and modern Windows. It's the fastest way to poke at an API before writing any Python. Try this in your terminal:

```bash
curl "https://api.github.com/users/octocat"
```

You get back a JSON description of GitHub's mascot account. Now add `-i` to include the status line and headers in the output:

```bash
curl -i "https://api.github.com/users/octocat"
```

Look for `HTTP/2 200`, the `content-type` header, and headers starting with `x-ratelimit-`, which tell you how many more requests GitHub will accept from you this hour. Next, ask for a user that doesn't exist:

```bash
curl -i "https://api.github.com/users/this-user-should-not-exist-12345"
```

You should see a `404` and a small JSON error body. Finally, `-v` (verbose) shows the request `curl` sent as well as the response, which is the single most useful debugging trick when an API isn't behaving.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read MDN's [overview of HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview). It's the clearest free explanation of the protocol, written by the people who document the web platform.
   - Read the whole page. Skim anything about proxies and caching; focus on "Components of HTTP-based systems," "HTTP flow" and "HTTP Messages."
1. Read MDN's [HTTP messages guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages) to see requests and responses dissected line by line.
1. Skim MDN's [HTTP response status codes reference](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status). Don't memorize it. Read the descriptions of 200, 201, 301, 400, 401, 403, 404, 429, 500 and 503, and bookmark the page.
1. Practice with `curl` against the free, no-key [GitHub REST API](https://docs.github.com/en/rest/using-the-rest-api/getting-started-with-the-rest-api).
   - Read the "About requests to the REST API" section, focusing on HTTP methods, paths, headers and query parameters.
   - Use `curl -i` to fetch your own GitHub user (`https://api.github.com/users/YOUR-USERNAME`) and your public repositories (`/users/YOUR-USERNAME/repos?per_page=5`). Find the status code, the `content-type` header and the `x-ratelimit-remaining` header in each response.
   - Trigger a 404 on purpose. Then run the same request with `-v` and identify the method, path and `Host` header in the request `curl` sent.
   - Add a short entry to your learning journal explaining, in your own words, the difference between a 4xx and a 5xx error and what your code should do about each.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- MDN's [What is a URL?](https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Web_mechanics/What_is_a_URL) breaks down every part of a URL with diagrams.
- MDN's [HTTP request methods reference](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods) covers every method, including the less common ones.
- [httpbin](https://httpbin.org/) is a free service that echoes back whatever you send it, handy for seeing exactly what your requests contain.
