<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

In Neural Networks, Intuitively you learned what a neural network is. This lesson is about how it learns. The answer is backpropagation: a systematic way to work out, for every one of a network's millions of weights, which direction to nudge it to make the loss a little smaller. Once you see it in a tiny example, every training run you meet later, from the tiny GPT in the next lesson to fine-tuning an open model, becomes understandable.

You will also meet PyTorch, the library most researchers and open models use. PyTorch computes backpropagation for you automatically, but you'll understand what it is doing.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Neurons, layers, activations and the forward pass.
- Derivatives as "how much does the output change if I wiggle this input."
- The chain rule and backpropagation through a computation graph.
- Gradient descent, learning rate and the training loop.
- Tensors, autograd and modules in PyTorch.
- Running code on a GPU, including free options.

### Key ideas

- **The forward pass is just math you already know.** Each layer multiplies its input by a weight matrix, adds a bias, and applies a nonlinearity such as ReLU (which zeroes out negatives). Stack layers and you get a network. The final output is compared to the right answer with a loss function.
- **A derivative measures sensitivity.** The derivative of the loss with respect to a weight tells you how much the loss would change if you nudged that weight slightly. The collection of all those derivatives is the gradient.
- **Backpropagation is the chain rule applied backward.** The network is a chain of simple operations. Starting at the loss, you multiply local derivatives backward through each operation to get every weight's gradient in one sweep. Karpathy's micrograd does this in about 100 lines of Python.
- **The training loop is always the same four steps:** forward pass, compute loss, backward pass (compute gradients), and an optimizer step that moves each weight a little against its gradient. Then zero the gradients and repeat. The learning rate controls the step size: too high and training diverges, too low and it crawls.
- **PyTorch tensors are NumPy arrays that remember how they were made.** With autograd, calling `loss.backward()` fills in `.grad` for every parameter. `nn.Module` bundles layers and parameters; `torch.optim` implements the update step.
- **GPUs make training practical.** Neural network training is mostly large matrix multiplications, which GPUs run in parallel. Move a model and its data with `.to("cuda")`. You don't need to own one: Google Colab and Kaggle Notebooks both offer free GPU time with usage limits.
- **Watch the loss curve.** Training loss should go down. Validation loss going up while training loss keeps falling is the same overfitting you met in Overfitting and Baselines.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Watch [3Blue1Brown's neural networks series](https://www.3blue1brown.com/topics/neural-networks) for the visual intuition behind learning.
   - Watch chapters 2 (gradient descent), 3 (backpropagation, intuitively) and 4 (backpropagation calculus). Chapter 4 is optional if the math feels heavy on first pass.
1. Work through the first video of [Andrej Karpathy's Neural Networks: Zero to Hero](https://karpathy.ai/zero-to-hero.html), "The spelled-out intro to neural networks and backpropagation: building micrograd."
   - Code along in your own notebook rather than just watching. It's long (about 2.5 hours); split it over several sessions.
   - The finished code is in the [micrograd repository](https://github.com/karpathy/micrograd) if you get stuck.
1. Complete the [PyTorch "Learn the Basics" tutorial](https://docs.pytorch.org/tutorials/beginner/basics/intro.html), which covers tensors, datasets, building a model, autograd, optimization and saving.
   - Run it in [Google Colab](https://colab.research.google.com/) with a GPU runtime selected, or in a [Kaggle Notebook](https://www.kaggle.com/docs/notebooks) with the GPU accelerator turned on. Check each service's current free limits before relying on them.
1. Write a PyTorch training loop from scratch that fits a two-layer network to `y = sin(x)` on 1,000 random points. Plot the training loss, then try three learning rates and note which one diverges.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Kaggle's guide to efficient GPU usage](https://www.kaggle.com/docs/efficient-gpu-usage) explains the free GPU quota and how not to waste it.
- [The Google Colab FAQ](https://research.google.com/colaboratory/faq.html) explains what the free tier includes and why runtimes disconnect.
