### Introduction

In [Neural Networks, Intuitively](#/paths/foundations), you learned that a neural network is a mathematical function made of interconnected layers that process numbers. This lesson explains how that network actually learns.

The answer is **backpropagation**: an efficient algorithm that calculates, for every one of a network's parameters, exactly which direction and how far to adjust it to reduce error. Once you grasp backpropagation on a simple computation graph, every training process you will encounter—from training a tiny GPT to fine-tuning multi-billion parameter open models—reads as the exact same underlying mechanism.

You will also learn [PyTorch](https://pytorch.org/), the dominant deep learning library used in AI research and open-source model development. PyTorch computes backpropagation automatically using dynamic computational graphs, but understanding the mechanics behind it ensures you can debug vanishing gradients, exploding losses, and shape errors with confidence.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- How the forward pass transforms inputs through linear layers and non-linear activation functions.
- How derivatives measure parameter sensitivity: "If I wiggle this weight, how does the loss change?"
- The chain rule of calculus and how backpropagation routes gradients backward through a computation graph.
- The standard four-step training loop: forward pass, loss calculation, backward pass, and optimizer step.
- Core PyTorch primitives: `torch.Tensor`, `autograd`, `nn.Module`, and `torch.optim`.
- How to move tensors to a GPU, and how to read training versus validation loss curves to spot overfitting.

### Forward pass: layers, weights, and non-linearities

The **forward pass** is the step where a neural network takes an input and computes a prediction.

A single artificial neuron calculates a weighted sum of its inputs, adds a bias term, and passes the result through an **activation function**:

```text
z = w1*x1 + w2*x2 + ... + wn*xn + b
output = activation(z)
```

In vector notation, for a whole layer of neurons:

```text
z = W @ x + b
a = activation(z)
```

Why do we need an activation function? Without one, stacking multiple linear layers `W2 @ (W1 @ x + b1) + b2` simplifies algebraically into a single linear transformation `W_combined @ x + b_combined`. Stacking a hundred linear layers without activation functions has the exact same representational power as a single layer.

Activation functions introduce **non-linearity**, allowing the network to approximate complex, curved decision boundaries:

- **ReLU (Rectified Linear Unit):** `relu(z) = max(0, z)`. It is computationally cheap (zero out negative numbers, pass positive numbers unchanged) and avoids gradient saturation for positive inputs. It is the workhorse of deep learning.
- **GELU (Gaussian Error Linear Unit):** A smooth curve that weights inputs by their probability under a normal distribution. GELU is the standard activation function in modern transformer architectures like GPT and Claude.
- **Sigmoid:** Squashes inputs into the range `(0, 1)`. Used primarily at the output layer for binary classification.

```python
import torch
import torch.nn as nn

# A simple 2-layer multi-layer perceptron (MLP)
class SimpleMLP(nn.Module):
    def __init__(self, in_features: int, hidden_dim: int, out_features: int):
        super().__init__()
        self.layer1 = nn.Linear(in_features, hidden_dim)
        self.relu = nn.ReLU()
        self.layer2 = nn.Linear(hidden_dim, out_features)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (batch_size, in_features)
        h = self.relu(self.layer1(x))    # shape: (batch_size, hidden_dim)
        out = self.layer2(h)             # shape: (batch_size, out_features)
        return out
```

### Derivatives as sensitivity and the chain rule

Once the network produces an output, we compare it against the target label using a **loss function** `L`. The loss is a single scalar number representing total error.

To reduce this error, we need to know how each individual weight `w` affects `L`. That sensitivity is the partial derivative:

```text
dL / dw
```

- If `dL / dw = +2.5`, increasing `w` by a tiny amount increases the loss. To decrease error, we must nudge `w` downward.
- If `dL / dw = -4.0`, increasing `w` decreases the loss. To decrease error, we must nudge `w` upward.
- If `dL / dw = 0.0`, nudging `w` has no immediate effect on the loss.

How do we compute `dL / dw` when a weight is buried ten layers deep inside a network? We use the **chain rule** of calculus.

If a variable `y` depends on `u`, and `u` depends on `x`, the rate of change of `y` with respect to `x` is the product of the intermediate rates of change:

```text
dy / dx = (dy / du) * (du / dx)
```

Consider a tiny calculation: `a = 2`, `b = 3`, `c = a * b = 6`, and `L = c + 4 = 10`.
- The derivative of `L` with respect to `c` is `dL / dc = 1`.
- The derivative of `c` with respect to `a` is `dc / da = b = 3`.
- By the chain rule, `dL / da = (dL / dc) * (dc / da) = 1 * 3 = 3`.

Nudging `a` upward by 0.01 increases `c` by 0.03, which in turn increases `L` by 0.03. The chain rule cleanly propagates sensitivity backward.

### Backpropagation through a computation graph

**Backpropagation** is the chain rule applied systematically in reverse across an entire **computation graph**.

In the forward pass, data flows from inputs to outputs, evaluating intermediate values and caching them in memory. In the backward pass, gradients flow from the loss backward to the inputs:

1. Start at the end: set `dL / dL = 1.0`.
2. For each node in reverse topological order, take the incoming gradient from its output and multiply it by the local derivative of that node's operation.
3. If a node distributes its value to multiple downstream paths, sum the gradients coming back from each path.

```text
Forward:   x ---> [ Layer 1 ] ---> h ---> [ Layer 2 ] ---> y_pred ---> [ Loss ] ---> L
                                                                                     |
Backward:  dL/dx <-- dL/dW1  <--- dL/dh <-- dL/dW2  <--- dL/dy_pred <----------------
```

Because each local derivative is computed only once and multiplied backward, backpropagation computes the gradient of the loss with respect to **every parameter in the network in a single backward sweep**. This takes roughly twice the computation of a forward pass, making the training of networks with billions of parameters computationally feasible.

### The four-step training loop

Every neural network training loop in PyTorch follows the exact same four steps inside an epoch loop:

1. **Forward pass:** Pass a batch of inputs through the model to get predictions: `outputs = model(inputs)`.
2. **Compute loss:** Compare predictions to actual labels using a loss function: `loss = criterion(outputs, targets)`.
3. **Backward pass:** Compute gradients for all trainable parameters: `loss.backward()`. PyTorch traverses the computational graph and accumulates the gradient into each parameter's `.grad` attribute.
4. **Optimizer step:** Update parameters using an optimization algorithm (such as Stochastic Gradient Descent or AdamW): `optimizer.step()`, then reset gradients with `optimizer.zero_grad()`.

```python
# training_demo.py: Training a tiny network on synthetic regression data
import torch
import torch.nn as nn
import torch.optim as optim

# 1. Create synthetic data: y = 2*x1 - 3*x2 + noise
torch.manual_seed(42)
X = torch.randn(200, 2)
true_weights = torch.tensor([[2.0], [-3.0]])
y = X @ true_weights + 0.5 + 0.1 * torch.randn(200, 1)

# 2. Define a linear model and optimizer
model = nn.Linear(in_features=2, out_features=1)
criterion = nn.MSELoss()
optimizer = optim.SGD(model.parameters(), lr=0.05)

# 3. The training loop
for epoch in range(100):
    # Step 1: Forward pass
    predictions = model(X)
    
    # Step 2: Compute loss
    loss = criterion(predictions, y)
    
    # Step 3: Backward pass (compute gradients)
    optimizer.zero_grad()  # Clear gradients from previous iteration
    loss.backward()        # Populate .grad for model weights and bias
    
    # Step 4: Update weights
    optimizer.step()
    
    if (epoch + 1) % 20 == 0:
        print(f"Epoch {epoch+1:3d} | Loss: {loss.item():.5f}")

print("\nLearned weights:", model.weight.data.numpy().round(3))
print("Learned bias:   ", model.bias.data.numpy().round(3))
```

If you forget `optimizer.zero_grad()`, PyTorch defaults to adding new gradients to existing ones (`param.grad += new_grad`). This accumulation is useful when simulating larger batch sizes across memory-constrained GPUs, but failing to clear gradients during standard training will cause weights to explode.

### PyTorch fundamentals: tensors, autograd, and nn.Module

PyTorch is organized around three primary abstractions:

1. **`torch.Tensor`:** A multi-dimensional array similar to a NumPy `ndarray`, with two crucial additions: it can run on GPUs, and it tracks mathematical operations when `requires_grad=True`.
2. **`torch.autograd`:** PyTorch's automatic differentiation engine. When you execute operations on tensors, autograd builds a directed acyclic graph (DAG) of functions recording the operations. Calling `.backward()` on a scalar tensor traces this graph in reverse.
3. **`torch.nn.Module`:** The base class for all neural network building blocks. Subclassing `nn.Module` automatically tracks all internal `nn.Parameter` tensors, handles GPU device transfers, and switches behaviors between training (`model.train()`) and evaluation (`model.eval()`).

### GPU acceleration and watching the loss curve

Matrix multiplications on large tensors run dramatically faster on Graphics Processing Units (GPUs) than on CPUs.

In PyTorch, you move both your model and your data tensors to the GPU using the `.to(device)` method:

```python
device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
print(f"Using device: {device}")

model = model.to(device)
# Inside the training loop:
# inputs, targets = inputs.to(device), targets.to(device)
```

You do not need to purchase expensive hardware to train models. [Google Colab](https://colab.research.google.com/) and [Kaggle](https://www.kaggle.com/code) both offer free GPU environments (such as Nvidia T4 instances) adequate for learning and fine-tuning small open models.

When training any model, monitor the **loss curve**:

- **Training loss:** Measures error on the data currently used to update weights. It should steadily decrease.
- **Validation loss:** Measures error on held-out data the model has never trained on.

![Training versus validation loss curves and early stopping](assets/images/loss_curve_overfitting.svg)

If training loss decreases while validation loss starts rising, the model is overfitting: it is memorizing noise in the training set rather than learning generalizable patterns. When this occurs, apply regularization, reduce model capacity, add more training data, or use early stopping.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Watch chapters 2 ("Gradient descent") and 3 ("What is backpropagation really doing?") from [3Blue1Brown's neural networks series](https://www.3blue1brown.com/topics/neural-networks).
   - Focus on visualizing how changes in weights cascade through the network to nudge output activations.
1. Work through the first lesson of [Andrej Karpathy's Neural Networks: Zero to Hero](https://karpathy.ai/zero-to-hero.html): "The spelled-out intro to neural networks and backpropagation: building micrograd."
   - Follow along and build the scalar `Value` object and its backward methods in a Jupyter or Colab notebook. Inspect the completed reference code in the [micrograd repository](https://github.com/karpathy/micrograd) if you encounter bugs.
1. Complete the official [PyTorch Quickstart Tutorial](https://pytorch.org/tutorials/beginner/basics/intro.html).
   - Run the tutorial in a notebook. Make sure you understand the difference between `model.train()` and `model.eval()`, and how `torch.no_grad()` disables gradient tracking during validation.
1. Write a standalone Python script named `fit_sine.py`:
   - Generate 1,000 synthetic training pairs where `x` is sampled uniformly between `-pi` and `+pi`, and `y = sin(x) + noise`.
   - Build a 2-layer MLP in PyTorch using `nn.Linear`, `nn.Tanh`, and `nn.Linear` with 32 hidden units.
   - Train the model using `optim.Adam` for 500 epochs. Print the loss every 50 epochs and confirm that the model learns to approximate the sine wave.

</div>

### Knowledge check

The questions below confirm that you have mastered the core ideas in this lesson. Click any question to review the section that explains it.

- [Why are non-linear activation functions required when stacking linear layers?](#forward-pass-layers-weights-and-non-linearities)
- [How does the mathematical chain rule enable calculating gradients for early layers in a deep network?](#derivatives-as-sensitivity-and-the-chain-rule)
- [What are the four essential steps of a standard PyTorch training loop?](#the-four-step-training-loop)
- [Why is calling optimizer.zero_grad() necessary before computing loss.backward()?](#the-four-step-training-loop)
- [What does a divergence between training loss and validation loss indicate during model training?](#gpu-acceleration-and-watching-the-loss-curve)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Kaggle Notebooks](https://www.kaggle.com/code) provides free GPU quotas (up to 30 hours per week of Nvidia T4/P100 accelerators) for training neural networks.
- [Colab FAQ](https://research.google.com/colaboratory/faq.html) covers runtime limits, GPU memory allocation, and connecting Google Drive for persistent checkpoints.
- [PyTorch Autograd Mechanics](https://pytorch.org/docs/stable/notes/autograd.html) is the official in-depth explanation of how PyTorch builds dynamic backward graphs.