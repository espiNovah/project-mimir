### Introduction

You built a GPT alongside a video in Building a Tiny GPT. Now you'll make one your own: pick a corpus that interests you, train a character-level GPT on it on a free GPU, and run a small experiment that changes one thing and measures its effect on loss. This is the same loop ML researchers run every day (form a hypothesis, change one variable, compare curves), shrunk down to an afternoon of GPU time.

When an interviewer asks "do you understand how these models actually work?", a repo with your own training curves and an experiment write-up is a far better answer than any explanation.

### Before you start

- Create a new repo named `mimir-tiny-gpt`. Keep your model code in a plain Python file (`model.py`, `train.py`, `sample.py`) so it's reviewable on GitHub, even if you run it from a notebook.
- Pick a corpus of roughly 1 to 10 MB of plain text that you are allowed to use. Good options: public-domain books from Project Gutenberg, your own writing, song lyrics you have the rights to, a programming language's open-source code, or recipes. [Tiny Shakespeare](https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt) is the classic fallback if you need something to get started, but your final model must be trained on a corpus you chose.
- Use a free GPU: [Google Colab](https://colab.research.google.com/) (select a GPU runtime) or [Kaggle Notebooks](https://www.kaggle.com/docs/notebooks) (turn on the GPU accelerator; Kaggle gives a weekly GPU quota). Free sessions disconnect, so save checkpoints to Google Drive, the Kaggle output folder, or download them regularly.
- Start from the code you wrote in Building a Tiny GPT. You may read [nanoGPT](https://github.com/karpathy/nanoGPT) for reference, but write and understand every line you submit.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Prepare your data: build a character vocabulary from your corpus, encode it, and split it 90/10 into training and validation sets. Print the corpus size, vocabulary size and a 200-character sample.
1. Train a bigram baseline and record its validation loss. Your transformer must beat it.
1. Train a character-level GPT with causal self-attention, multiple heads, feed-forward layers, residual connections and layer norm. Log training loss and validation loss at regular intervals, and save the log to a CSV file.
1. Save checkpoints at three points (for example early, middle and end of training). For each, generate a 500-character sample with a fixed seed and save it to `samples/`.
1. Plot training and validation loss on one chart and save it as `loss.png`. Mark the three checkpoint steps on the plot.
1. Run one controlled experiment. Change exactly one thing (number of layers, embedding size, context length, dropout, learning rate, or training data size), keep everything else and the random seed the same, train again, and plot both validation curves on one chart.
1. Write `sample.py` that loads a checkpoint and generates text from a prompt you pass on the command line.
1. Push your project to GitHub with a README that explains what it does, how to run it, and what you learned. The README must include:
   - Your corpus, where it came from and why you picked it.
   - Model size (parameter count), training time and the GPU you used.
   - The loss plot, the bigram baseline loss and your final validation loss.
   - The three samples, with a sentence each on what the model had learned by that point.
   - Your experiment: the hypothesis, the one change, both curves, and what happened to the loss and why you think it happened.

#### Extra credit

- Deliberately overfit: train a large model on a tiny slice of your corpus and show the training and validation curves separating, then fix it with dropout.
- Add temperature and top-k sampling to `sample.py` and include samples at three temperatures.
- Swap the character tokenizer for a small byte-pair encoding tokenizer and compare loss per character.
- Try [nanochat](https://github.com/karpathy/nanochat) and write up how its pipeline differs from your model.

</div>

### Submitting your work

A strong submission is honest and reproducible. Anyone should be able to run `train.py` with your settings and get similar curves. The samples show visible progress from noise to recognizable style. The experiment section is the part reviewers read most closely: it changes one variable, shows the curves side by side, and draws a careful conclusion (including "it made no difference," if that's what happened) rather than overclaiming.
