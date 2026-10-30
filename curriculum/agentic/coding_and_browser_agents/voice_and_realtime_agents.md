<div class="lesson-note" markdown="1">

#### This lesson is optional

Voice is a specialty, not a requirement. No later lesson or project depends on it, so skip it if you like and come back when a job or a project idea calls for it. It's worth a read if you're curious, because voice agents are a growing area of hiring, especially in customer support, and they teach latency in a way nothing else does.

</div>

### Introduction

A voice agent is an agent you talk to out loud: a phone line that books appointments, a support bot that answers calls, an assistant in a car. Underneath, it's the same loop you've built all along, with tools, a model and a stop condition. What changes is time. In a chat window, a reply that takes four seconds is fine. On a phone call, four seconds of silence feels like the line has dropped, and people start talking again just as the agent answers.

This lesson explains the two ways to build a voice agent, where the milliseconds go, and how voice agents decide when you've finished speaking. You'll build one cascaded voice turn with a latency report, and you'll leave knowing which questions to ask before building a real one.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Cascaded pipelines versus speech-to-speech models.
- The latency budget, and why streaming every stage matters.
- Turn-taking: voice activity detection, endpointing and interruptions.
- Choosing and using speech-to-text and text-to-speech.
- Realtime voice APIs and the frameworks around them.
- What changes about tools, safety and evaluation when the agent talks.

### Two ways to build a voice agent

**The cascaded pipeline** chains three models:

1. **Speech-to-text (STT)** turns the caller's audio into text. You used Whisper for this in Images, PDFs and Audio.
1. **A language model** reads the transcript and the conversation so far, calls tools if it needs to, and writes a reply as text.
1. **Text-to-speech (TTS)** turns the reply into audio.

Each piece is swappable, and the middle is an ordinary text agent, so everything you know about prompts, tools, traces and evals still applies. You can read the transcript of every turn, which makes debugging and compliance much easier. The costs are latency, since three models run one after another, and lost information: the transcript drops tone of voice, hesitation and emphasis, and the TTS has to guess how to say the reply.

**Speech-to-speech** models take audio in and produce audio out, in one model. Because nothing waits for a full transcript, they can respond faster, they hear tone and can answer with expression, and they handle interruptions more naturally. Providers offer them through **realtime APIs**, which keep a connection open and stream audio both ways. The tradeoffs are fewer model choices, a higher price per minute, less control over exactly what is said, and a harder time debugging, because the "reasoning" happens on audio.

Most production voice agents in 2026 still use the cascade, or a hybrid, because control and debuggability matter for businesses. Speech-to-speech is growing fast for conversations where natural feel matters most. Neither is always right. Pick based on the latency you need, the control you need and the models you can use.

### The latency budget

People in conversation leave gaps of only about 200 milliseconds between turns. A voice agent can't match that, but it needs to stay close: under about one second from the moment the caller stops speaking to the moment they hear the first sound of the reply feels responsive, and past two seconds feels broken. That number, **voice-to-voice latency**, is the one to design around.

A **latency budget** splits that second among the stages, the same way the Agent Cost and Latency lesson split an agent run into steps. A typical cascaded budget looks like this:

| Stage | Typical time | What it is |
| --- | --- | --- |
| Endpointing | 200–500 ms | Waiting to be sure the caller has stopped talking |
| Final transcript | 100–300 ms | The STT finishes the last words |
| Model time to first token | 200–700 ms | Grows with the prompt size and with thinking |
| TTS time to first audio | 100–300 ms | The first syllable of speech |
| Network | 50–200 ms | Both directions, more on phone lines |

Add the middle of each range and you're already near a second, so every stage must **stream**. The STT transcribes while the caller is still talking, so only the last words remain when they stop. The model streams its reply token by token. The pipeline cuts the reply into sentences and sends the first sentence to the TTS while the model is still writing the second. The caller hears the start of the answer before the end of it exists.

The levers follow from the table. Use a fast model for the conversation, at low effort, and keep the prompt short and cacheable. Ask the model for short spoken replies. Put STT, model and TTS servers close together and close to your users. And watch tool calls closely: a tool that takes two seconds blows the budget alone, so voice agents often say a short filler line ("Let me check that for you") while a slow tool runs. Measure **percentiles**, not averages, because the slowest 5 percent of turns (the p95) are the ones callers remember.

### Turn-taking and interruptions

Text chat has a send button. Voice doesn't, so the agent has to decide when the caller has finished. That's called **turn detection**, and it's harder than it sounds.

The basic tool is **voice activity detection (VAD)**: a small, fast model, such as the open-source Silero VAD, that labels each slice of audio as speech or not speech. **Endpointing** then decides the turn is over after a stretch of silence, say 500 milliseconds. Set that too short and the agent cuts in whenever someone pauses to think, mid-sentence. Set it too long and every reply feels slow. Newer systems add a **semantic** turn detector, a small model that reads the words so far and judges whether the sentence sounds finished, so "My account number is..." waits while "That's all, thanks." doesn't.

The other half of turn-taking is **barge-in**: the caller interrupts while the agent is talking. A good agent stops speaking within a fraction of a second, which means the pipeline must be able to cancel the model stream and the TTS at once. Then it must fix its own history. If the model wrote four sentences but the caller only heard one before interrupting, the conversation history should contain just the one they heard, or the agent will later refer to things it never said. Echo is a related trap: the agent's own voice, picked up by the caller's microphone, can trigger the VAD, so real systems use echo cancellation.

### Speech-to-text and text-to-speech

When choosing an **STT** model, check four things. **Streaming support**, so transcription happens while people speak. **Word error rate** (WER, the share of words wrong, missing or added, from the Images, PDFs and Audio lesson) on audio like yours: phone audio is low quality, and accents and background noise all raise it. **Domain words**, since names, product terms and numbers are where transcripts fail, and many STT services let you pass a list of expected words to bias toward. And **latency** to the final transcript. Whisper and its faster reimplementations run locally for free. Hosted STT services cost a fraction of a cent per minute and add streaming and features like telling speakers apart.

For **TTS**, judge naturalness, latency to first audio, streaming, voice choice, languages and price. Local open-source options such as Piper are free and fast but sound more robotic. Hosted voices sound far more natural.

Language models write for readers, so a voice agent's prompt must ask for writing for the ear. Markdown, bullet lists, URLs and tables sound terrible read aloud. "$1,250.00" may come out as "dollar sign one comma two five zero." Ask for short sentences, plain speech and numbers in words, and confirm important details by repeating them back.

### A cascaded voice turn

This script runs one turn of a cascaded voice agent on a recorded clip, and reports where the time went. It uses the Claude API for the middle step. (The Claude API takes text, images and documents, not audio, so it fits the cascade but not speech-to-speech.) Set up a project with `uv add anthropic faster-whisper "av<19" python-dotenv` (the `av` pin is explained in Images, PDFs and Audio), keep `ANTHROPIC_API_KEY` in `.env`, and save this as `voice_turn.py`:

```python
"""voice_turn.py: one cascaded voice turn (STT, then model, then TTS) with a latency report."""
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time

import anthropic
from dotenv import load_dotenv
from faster_whisper import WhisperModel

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
SYSTEM = ("You are a voice assistant. Everything you write is spoken aloud. Reply in one to "
          "three short sentences of plain speech: no lists, no markdown, numbers in words.")
TTS = shutil.which("say") or shutil.which("espeak-ng")  # macOS, or Linux with espeak-ng
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def speaker(lines: queue.Queue, first_audio: list) -> None:  # (1) speaks while the model writes
    while (line := lines.get()) is not None:
        first_audio.append(time.perf_counter())
        if TTS:
            subprocess.run([TTS, line], check=False)
        else:
            print(f"  (would say) {line}")


def main(path: str) -> None:
    stt = WhisperModel("base", device="cpu", compute_type="int8")  # (2) load before the turn starts
    t_end_of_speech = time.perf_counter()
    segments, _ = stt.transcribe(path)
    text = " ".join(s.text.strip() for s in segments)
    t_transcript = time.perf_counter()
    print("heard:", text)

    lines, first_audio = queue.Queue(), []
    thread = threading.Thread(target=speaker, args=(lines, first_audio))
    thread.start()
    buffer, t_first_token = "", None
    with anthropic.Anthropic().messages.stream(
        model=MODEL, max_tokens=1000, system=SYSTEM,
        output_config={"effort": "low"},  # (3) a Claude setting: less thinking, faster first token
        messages=[{"role": "user", "content": text}],
    ) as stream:
        for chunk in stream.text_stream:
            t_first_token = t_first_token or time.perf_counter()
            buffer += chunk
            *finished, buffer = SENTENCE_END.split(buffer)  # (4) hand over each complete sentence
            for sentence in finished:
                lines.put(sentence)
    if buffer.strip():
        lines.put(buffer.strip())
    lines.put(None)  # tell the speaker thread there's nothing more
    thread.join()

    ms = lambda a, b: f"{(b - a) * 1000:6.0f} ms"
    print("STT (whole clip):     ", ms(t_end_of_speech, t_transcript))
    print("model first token:    ", ms(t_transcript, t_first_token))
    print("voice-to-voice (est.):", ms(t_end_of_speech, first_audio[0]))


if __name__ == "__main__":
    main(sys.argv[1])
```

Make a test clip on a Mac with `say -o question.aiff "What should I pack for a weekend in Edinburgh?"` (or record one with any voice memo app) and run `uv run voice_turn.py question.aiff`.

1. **A separate speaker thread.** The TTS speaks sentence one while the main loop is still receiving sentence two. Without it, the model's whole reply would have to finish before any sound came out.
1. **Warm models.** Loading the STT model takes longer than using it. A real agent loads every model once at startup and keeps it in memory, so loading isn't part of the turn.
1. **Low effort.** Effort is a Claude setting that controls how much the model thinks. Less thinking means a faster first token, which is usually the right trade for small talk; use more for turns that need real reasoning. On other providers, look for a reasoning-effort setting or pick a non-reasoning model.
1. **Sentence chunking.** Sending each complete sentence to the TTS is the simplest way to start speaking early. Production systems use TTS that accepts streamed text directly.

The report is an estimate with an obvious gap: this script transcribes a finished file, so its STT number is the whole clip, where streaming STT would have done most of that work while the caller spoke. That's exactly the kind of thing a latency budget makes visible.

### Realtime voice APIs and frameworks

For speech-to-speech, providers offer realtime APIs. Two widely used ones are OpenAI's **Realtime API** and Google's **Gemini Live API**. Each keeps a session open over a **WebSocket** (a two-way connection that stays open, good for servers) or **WebRTC** (the protocol browsers use for video calls, built to survive poor networks, good for apps in the browser or on phones). You stream microphone audio in and get audio out. The session also handles VAD and turn detection on the server, lets you define tools just like in chat, and sends events when the caller interrupts. These are provider-specific APIs, each with its own event names and session settings, and open models offer fewer speech-to-speech options.

Wiring audio, VAD, interruptions, telephony and three models together by hand is a lot of plumbing, so most teams use a framework. **Pipecat** and **LiveKit Agents** are the two popular open-source ones. Both are Python, both let you build a cascade or plug in a realtime model, and both handle streaming, turn detection and interruptions. They're the "agent framework" of voice: as with LangGraph, learn what they do for you by building one turn by hand first, as you just did.

### Tools, safety and evaluation in voice

**Tools** work the same way, but every tool call spends latency budget, so give the agent quick tools, say a filler line before slow ones, and avoid long chains of calls in a single turn. **Confirm before acting.** A misheard "fifteen" for "fifty" is a typo in a chat and a wrong refund on a call, so read back amounts, dates and names, and get a clear yes before any action you can't undo, as in Approvals and Permissions.

**Safety** has voice-specific rules too. Tell callers they're talking to an AI, and know the recording-consent laws where your callers live. Never clone a real person's voice without their explicit permission. And remember that audio is untrusted input like any other: anything said on a call, or played into one, reaches your model, so prompt injection applies here too.

**Evaluate** a voice agent on several layers: WER for the STT on your own audio, latency percentiles for each stage and voice-to-voice, and task success for whole conversations. The simulated users you'll meet in the agent evals section work here too, with a TTS voice playing the caller.

### On other providers

The cascade is provider-neutral: any chat model can sit in the middle, and the streaming, sentence chunking and latency report carry over. With OpenAI's Chat Completions, you pass `stream=True` and read text from each chunk's `choices[0].delta.content`, as shown below; with a local model through [Ollama's OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility), change the `base_url` and model name, and expect a slower first token on a laptop. OpenAI also offers hosted transcription and text-to-speech endpoints (see its [speech-to-text guide](https://developers.openai.com/api/docs/guides/speech-to-text)). Speech-to-speech is where providers differ most: OpenAI's [Realtime API](https://developers.openai.com/api/docs/guides/realtime) and Google's [Gemini Live API](https://ai.google.dev/gemini-api/docs/live) each have their own session and event formats, and the Claude API has no realtime audio API, so on Claude you build the cascade.

```python
import os
from openai import OpenAI  # uv add openai; reads OPENAI_API_KEY

client = OpenAI()  # for Ollama: OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
stream = client.chat.completions.create(
    model=os.environ["MIMIR_OPENAI_MODEL"], stream=True,
    messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}],
)
for chunk in stream:
    piece = chunk.choices[0].delta.content if chunk.choices else None
    if piece:
        buffer += piece  # then split into sentences exactly as before
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read OpenAI's [voice agents guide](https://developers.openai.com/api/docs/guides/voice-agents) to see the speech-to-speech and chained (cascaded) architectures side by side, from a provider that offers both.
   - Read "Choose the right architecture" and "Measure latency" closely; skim the code.
1. Read the [Pipecat documentation](https://docs.pipecat.ai/) introduction and core concepts, to see how a real voice framework organizes a pipeline of frames, processors and transports.
   - Note where it handles VAD, interruptions and sentence aggregation, and compare with `voice_turn.py`.
1. Skim the [LiveKit Agents documentation](https://docs.livekit.io/agents/), the other popular open-source voice framework, especially its pages on turn detection.
1. Build and measure one voice turn.
   - Run `voice_turn.py` on three clips: a short question, a long question, and one with a name or number in it. Record the transcript and each latency line in a table.
   - Change one thing at a time and re-measure: the Whisper model size (`"tiny"` versus `"small"`), the effort level, and a system prompt that asks for long answers. Which change moves voice-to-voice latency most? Did any transcript get a name or number wrong?
   - Write three sentences on where you'd spend effort first to get this pipeline under one second.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What are the tradeoffs between a cascaded pipeline and a speech-to-speech model?](#two-ways-to-build-a-voice-agent)
- [What is voice-to-voice latency, and roughly what should it be?](#the-latency-budget)
- [Why must every stage of a voice pipeline stream?](#the-latency-budget)
- [What do VAD and endpointing do, and what goes wrong if the silence threshold is too short or too long?](#turn-taking-and-interruptions)
- [After a caller interrupts, what should the conversation history contain?](#turn-taking-and-interruptions)
- [Why does a voice agent's prompt need to ask for different writing than a chat agent's?](#speech-to-text-and-text-to-speech)
- [Why should a voice agent read back amounts and names before acting?](#tools-safety-and-evaluation-in-voice)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Silero VAD](https://github.com/snakers4/silero-vad) is a small open-source voice activity detector you can run locally to see how speech detection works on your own recordings.
- [Piper](https://github.com/OHF-Voice/piper1-gpl) is a fast, free, local text-to-speech engine, if you want a TTS that runs offline on every operating system.
