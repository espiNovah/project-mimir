### Introduction

A table of numbers tells you what happened. A chart shows you, and it often shows you something you didn't think to ask about: an outlier, a gap in the data, a trend that reverses halfway through. When you compare two prompts, track how latency changes over a week or show a client how an eval score moved, a chart is usually what people actually look at.

**matplotlib** is Python's original and most widely used plotting library. Most other Python plotting tools (including pandas' own `.plot()`) are built on top of it, so learning it pays off everywhere. Its reputation for being fiddly comes mostly from the fact that there are two ways to use it. This lesson teaches the one that stays clear as your charts grow, covers the four chart types you'll use most, and spends real time on the part beginners skip: choosing a chart that tells the truth, including showing how uncertain a number is.

You'll keep using the penguins data from the NumPy and pandas Basics lesson.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Figures and axes, and the object-oriented way to use matplotlib.
- Line charts, bar charts, histograms and scatter plots.
- Labels, titles, legends and saving figures to files.
- Error bars, and what they should mean.
- Choosing the right chart for the question.
- Habits that keep charts honest.

### Figures and axes

Add the library to your project with `uv add matplotlib`. Every matplotlib chart has two main parts:

- A **Figure** is the whole image, the canvas you save to a file.
- An **Axes** (yes, singular, despite the "s") is one plot inside the figure, with its own x-axis, y-axis, title and data. A figure can hold several.

The clearest way to work is to create both explicitly and then call methods on the axes:

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6, 4))  # width and height in inches
ax.plot([1, 2, 3, 4], [10, 14, 12, 18])
ax.set_title("A first chart")
```

This is called the **object-oriented** style. You'll also see a second style in many tutorials, which calls functions on `plt` directly (`plt.plot(...)`, `plt.title(...)`) and lets matplotlib keep track of the "current" chart behind the scenes. It's fine for a quick look, but it gets confusing as soon as you have two plots, so use `fig, ax = plt.subplots()` by default. The method names differ slightly between the two styles: `plt.title` becomes `ax.set_title`, `plt.xlabel` becomes `ax.set_xlabel`.

In a notebook, the chart appears under the cell automatically. In a script, call `plt.show()` to open a window, or save it to a file (covered below).

### The four everyday charts

Almost everything you'll need starts as one of four charts. Each answers a different kind of question.

```python
import matplotlib.pyplot as plt
import pandas as pd

URL = "https://raw.githubusercontent.com/allisonhorst/palmerpenguins/main/inst/extdata/penguins.csv"
penguins = pd.read_csv(URL).dropna(subset=["body_mass_g", "flipper_length_mm"])

# Histogram: how is one numeric column distributed?
fig, ax = plt.subplots(figsize=(6, 4))
ax.hist(penguins["body_mass_g"], bins=20, edgecolor="white")
ax.set_xlabel("Body mass (g)")
ax.set_ylabel("Number of penguins")
ax.set_title("Most penguins weigh 3,500 to 4,500 g")

# Bar chart: how do categories compare on one number?
counts = penguins["species"].value_counts()
fig, ax = plt.subplots(figsize=(5, 4))
ax.bar(counts.index, counts.values)
ax.set_ylabel("Number of penguins")

# Scatter plot: how do two numeric columns relate?
fig, ax = plt.subplots(figsize=(6, 4))
for species, group in penguins.groupby("species"):
    ax.scatter(group["flipper_length_mm"], group["body_mass_g"],
               label=species, s=15, alpha=0.7)
ax.set_xlabel("Flipper length (mm)")
ax.set_ylabel("Body mass (g)")
ax.legend(title="Species")

# Line chart: how does a number change over an ordered axis, usually time?
yearly = penguins.groupby(["year", "species"])["body_mass_g"].mean().unstack()
fig, ax = plt.subplots(figsize=(6, 4))
for species in yearly.columns:
    ax.plot(yearly.index, yearly[species], marker="o", label=species)
ax.set_xticks(yearly.index)  # show 2007, 2008, 2009, not 2007.5
ax.set_xlabel("Year")
ax.set_ylabel("Mean body mass (g)")
ax.legend()
```

A few details are worth knowing:

- In the histogram, `bins` sets how many bars the range is split into. Too few hides the shape and too many makes noise. Try a couple of values; there's no single right answer.
- In the scatter plot, looping over `groupby` draws each species as its own series, and `label=` gives `ax.legend()` something to show. `alpha=0.7` makes points slightly transparent so overlapping ones stay visible, and `s` is the marker size.
- In the line chart, `.unstack()` turns the `species` level of the group labels into columns, giving one column per line. You'll reshape data this way often before plotting.

pandas can also draw charts directly, as in `counts.plot.bar()`. It calls matplotlib for you and returns the same kind of `ax`, so you can still call `ax.set_title` on the result. It's a handy shortcut once you know what it's doing underneath.

### Labels and saving figures

A chart that someone else will read needs, at minimum:

- **Axis labels with units.** "Body mass (g)", not "body_mass_g". A column name is not a label.
- **A title that says the point**, when the chart is in a report. "Gentoo penguins are about 1.3 kg heavier" tells the reader what to see; "Body mass by species" makes them work it out.
- **A legend** whenever there's more than one series, so identity never depends on color alone.

To save a chart, call `savefig` on the figure:

```python
fig.savefig("charts/mass_by_species.png", dpi=150, bbox_inches="tight")
plt.close(fig)
```

The file format comes from the extension. PNG is the safe choice for READMEs and reports; SVG and PDF are vector formats that stay sharp at any size. `dpi` (dots per inch) controls the resolution of PNGs, and 150 is sharp enough for a screen. `bbox_inches="tight"` trims empty margins so labels aren't cut off. If labels still overlap, create the figure with `plt.subplots(layout="constrained")`, which makes matplotlib arrange things to fit. In a script that makes many charts, `plt.close(fig)` frees the memory once each one is saved. Note that `savefig` doesn't create folders, so make `charts/` first.

### Error bars

Here is the mean body mass of each species:

| Species | Mean mass (g) | Birds weighed |
| --- | --- | --- |
| Adelie | 3,701 | 151 |
| Chinstrap | 3,733 | 68 |
| Gentoo | 5,076 | 123 |

Is a Chinstrap really heavier than an Adelie, or is a 32 g difference just luck in which birds happened to be measured? A bar chart of the means alone can't tell you. **Error bars** show how uncertain each number is, and they matter just as much when the bars are eval scores for two prompts.

Error bars can mean different things, and that's the trap. The two you'll see most:

- The **standard deviation** describes how spread out the individual values are. Adelie penguins vary by about 460 g from bird to bird. This doesn't shrink as you collect more data.
- The **standard error** describes how uncertain the *mean* is. It's the standard deviation divided by the square root of the count, so it shrinks as you collect more data. A range of about 1.96 standard errors either side of the mean is an approximate **95% confidence interval**: if you repeated the whole study many times, intervals built this way would contain the true mean about 95% of the time.

When the question is "do these groups differ on average?", the standard error is the one you want:

```python
import matplotlib.pyplot as plt
import pandas as pd

URL = "https://raw.githubusercontent.com/allisonhorst/palmerpenguins/main/inst/extdata/penguins.csv"
penguins = pd.read_csv(URL)

stats = penguins.groupby("species")["body_mass_g"].agg(["mean", "std", "count"])
stats["sem"] = stats["std"] / stats["count"] ** 0.5   # standard error of the mean

fig, ax = plt.subplots(figsize=(5, 4))
ax.bar(stats.index, stats["mean"], yerr=1.96 * stats["sem"], capsize=6)
ax.set_ylabel("Mean body mass (g)")
ax.set_title("Mean body mass by species (95% CI)")
fig.savefig("mass_by_species.png", dpi=150, bbox_inches="tight")
```

`yerr` adds an error bar to each bar, and `capsize` draws the little caps at the ends. For points or lines instead of bars, `ax.errorbar(x, y, yerr=...)` does the same job.

The Adelie and Chinstrap intervals overlap a lot, so this data gives no good reason to think their average weights differ. Gentoo's interval is far from both. Whatever you choose, **say in the title or caption what the error bars show**. A bar of ±1 standard deviation and a bar of ±1.96 standard errors look identical and mean very different things. The Eval Statistics lesson later in the curriculum goes much further, with confidence intervals for accuracy scores and the bootstrap; this is the first step.

### Choosing the right chart

Start from the question, not the chart type:

- **How is one variable distributed?** Histogram. (A box plot, `ax.boxplot`, compares distributions across groups compactly.)
- **How do categories compare?** Bar chart, with error bars when the values are averages or rates from samples. Sort the bars by value unless the categories have a natural order, and use horizontal bars (`ax.barh`) when the labels are long.
- **How does something change over time?** Line chart. Lines imply continuity, so don't use them to connect unrelated categories.
- **Are two numeric variables related?** Scatter plot.
- **Is there only one number?** Don't make a chart. Write the number in a sentence.

If you have too many series for one chart to stay readable (more than four or five lines, say), split them into a grid of small charts with `fig, axes = plt.subplots(1, 3, sharey=True)`. Each chart in the grid is an ordinary `ax`, so `axes[0].hist(...)` works the same way. `sharey=True` gives them a common y-axis so they can be compared at a glance.

### Keeping charts honest

A chart can be technically correct and still mislead. A few rules prevent most of it:

- **Bars start at zero.** A bar's length *is* its value, so a y-axis that starts at 3,500 makes a 1% difference look like a doubling. matplotlib starts bars at zero by default; don't override it. Line charts and scatter plots may zoom in, because there the position matters, not the length.
- **One y-axis per chart.** Putting two measures with different scales on the left and right of one chart (a "dual axis" chart) lets you make any two lines look related by choosing the scales. Use two charts instead.
- **Use a log scale when values span many orders of magnitude**, and label it. `ax.set_yscale("log")` puts 10, 100 and 1,000 equally far apart. Without it, everything but the biggest values gets squashed flat against the axis.
- **Say how many data points stand behind each number**, and show error bars for averages from samples.
- **Don't rely on color alone.** About 1 in 12 men has some color vision deficiency. matplotlib's default colors are reasonably distinguishable, but direct labels or a legend, and different marker shapes for print, make sure everyone can read the chart.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [matplotlib's quick start guide](https://matplotlib.org/stable/users/explain/quick_start.html). It explains figures, axes and the two coding styles with pictures.
   - Read up to and including "Labelling plots". Skim the rest.
1. Browse [matplotlib's plot types overview](https://matplotlib.org/stable/plot_types/index.html), a one-page gallery of every basic chart with the code to make it. Bookmark it; it's the fastest way to find the right function.
1. Read two chapters of Claus Wilke's free book "Fundamentals of Data Visualization": the [directory of visualizations](https://clauswilke.com/dataviz/directory-of-visualizations.html), which maps kinds of questions to kinds of charts, and [visualizing uncertainty](https://clauswilke.com/dataviz/visualizing-uncertainty.html), which goes deeper on error bars and how people misread them.
1. Practice in a notebook with the penguins data:
   - Make each of the four everyday charts, with axis labels that include units and a title that states the point.
   - Make a bar chart of mean flipper length per island with 95% error bars, and write one sentence about whether the islands differ.
   - Make the same bar chart with the y-axis starting at 180 (`ax.set_ylim(180, 220)`) and look at how much bigger the differences seem. Then delete that line.
   - Save one chart as a PNG with `dpi=150` and `bbox_inches="tight"`, and check that nothing is cut off.
1. If you haven't yet, finish the [data exercise set](https://github.com/espiNovah/project-mimir/tree/main/exercises/data), since the Data Explorer project builds on the same pandas skills.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What is the difference between a Figure and an Axes?](#figures-and-axes)
- [Which chart would you use to see how one numeric column is distributed, and which to see how two columns relate?](#the-four-everyday-charts)
- [What does `bbox_inches="tight"` do when saving a figure?](#labels-and-saving-figures)
- [What is the difference between a standard deviation error bar and a standard error error bar?](#error-bars)
- [When should you not make a chart at all?](#choosing-the-right-chart)
- [Why must a bar chart's y-axis start at zero, when a line chart's doesn't have to?](#keeping-charts-honest)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The pandas chart visualization guide](https://pandas.pydata.org/docs/user_guide/visualization.html) shows the `.plot` shortcuts and how they map to matplotlib.
- [matplotlib's guide to choosing colormaps](https://matplotlib.org/stable/users/explain/colors/colormaps.html) explains why some color scales are easier to read, including for colorblind readers.
- [seaborn](https://seaborn.pydata.org/tutorial/introduction.html) is a library built on matplotlib that makes grouped charts and confidence intervals one-liners, once you understand what it's drawing.
