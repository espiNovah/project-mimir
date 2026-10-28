### Introduction

Almost every AI system you build will produce tables. A log of model calls has one row per call, with columns for latency, tokens and cost. An eval run has one row per test case, with the input, the model's answer and a score. A dataset you fine-tune on, a spreadsheet a client sends you, an export from a database: all tables. You could process them with the lists, dicts and `csv` module you already know, as you did in the Expense Tracker, but every question ("what's the average cost per model?") would become a loop you write by hand.

Two libraries make this work fast and short. **NumPy** gives Python arrays of numbers you can do math on all at once. **pandas** builds on NumPy to give you labeled tables, called DataFrames, with tools for loading, filtering, grouping and joining. Together they're the standard toolkit for data work in Python, and nearly every AI library you'll meet later accepts or returns their objects.

This lesson uses a small, real dataset: measurements of 344 penguins from three islands in Antarctica, the [Palmer Penguins](https://allisonhorst.github.io/palmerpenguins/) data. It's small enough to understand completely and messy enough (it has missing values) to be realistic.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- NumPy arrays and why vectorized code beats loops.
- DataFrames, Series and column types.
- Loading a CSV file and taking a first look at it.
- Selecting columns and filtering rows with boolean masks.
- Finding and handling missing values.
- Summarizing groups with `groupby`.
- Joining two tables with `merge`.

### Setting up

Work in a notebook, as you learned in the Notebooks and Colab lesson. Create a project and add the libraries:

```bash
uv init data-practice
cd data-practice
uv add numpy pandas
uv run --with jupyter jupyter lab
```

The examples here were checked against pandas 3.1 and NumPy 2.5. pandas 3 changed a few long-standing behaviors, which this lesson points out where they matter, so a tutorial written before 2026 may show slightly different output.

### NumPy arrays and vectorization

A Python list can hold anything: numbers, strings, other lists. That flexibility costs speed, because Python has to check what each item is every time it touches it. A **NumPy array** holds items of one type (all 64-bit integers, say) packed side by side in memory, so NumPy can run fast compiled code over the whole thing at once.

The bigger win is how you write code. With an array, you don't loop. You write the operation once, and it applies to every element. This is called **vectorization**.

```python
import numpy as np

# Latency of six model calls, in milliseconds
latencies_ms = np.array([820, 1340, 640, 2950, 910, 1120])
print(latencies_ms.dtype, latencies_ms.shape)  # int64 (6,)

# Math applies to every element. No loop.
seconds = latencies_ms / 1000
print(seconds)  # [0.82 1.34 0.64 2.95 0.91 1.12]

# Summary statistics are methods or functions
print(latencies_ms.mean(), np.median(latencies_ms), latencies_ms.max())

# A comparison gives an array of True/False values: a boolean mask
slow = latencies_ms > 1000
print(slow)                # [False  True False  True False  True]
print(latencies_ms[slow])  # [1340 2950 1120]: only the True positions
print(slow.sum())          # 3, because True counts as 1

# Two arrays of the same shape combine element by element
input_tokens = np.array([1200, 3400, 800, 9100, 1500, 2600])
cost = input_tokens * 0.000003   # a made-up price per token
print(cost.round(4), cost.sum())
```

Each line replaces a loop you'd otherwise write. `latencies_ms[slow]` in particular is worth remembering: you pick out elements with a mask of the same length, and the same trick is how you filter rows in pandas.

`dtype` is the array's element type and `shape` its size along each dimension. Arrays can have more than one dimension (a 2D array is a grid, like a matrix), which you'll use heavily when you get to embeddings and vectors. For now, one dimension is enough.

NumPy marks a missing number with the special value `np.nan` ("not a number"). Any math involving `nan` gives `nan`, so `np.array([820, np.nan, 640]).mean()` is `nan`. That is deliberate: NumPy refuses to quietly pretend the gap isn't there. Use `np.nanmean` when you really do want to ignore it. pandas, as you'll see, makes the opposite choice by default.

### DataFrames and Series

A **DataFrame** is a table: rows and named columns, where each column has one type. Each column on its own is a **Series**, a one-dimensional labeled array, basically a NumPy array with a name and an **index** (the row labels, which default to 0, 1, 2, ...).

`pd.read_csv` reads a CSV file into a DataFrame. It accepts a local path or a URL:

```python
import pandas as pd

URL = "https://raw.githubusercontent.com/allisonhorst/palmerpenguins/main/inst/extdata/penguins.csv"
penguins = pd.read_csv(URL)

penguins.shape      # (344, 8): rows, columns
penguins.head()     # the first five rows
penguins.info()     # each column's type and how many non-missing values it has
penguins.describe() # count, mean, std, min, quartiles and max of numeric columns
penguins["species"].value_counts()  # how many rows have each value
```

Run those five lines on every new dataset before you do anything else. `info()` is the most important. Here it shows three text columns with type `str`, four `float64` measurement columns and an `int64` year, and it shows that `body_mass_g` has 342 non-missing values out of 344. Two penguins were never weighed. You'd never spot that by scrolling.

<div class="lesson-note" markdown="1">

#### Why are the measurements floats?

`body_mass_g` holds whole numbers like 3750, yet pandas made it `float64`. That's because the column has missing values, and the classic missing marker, `NaN`, only exists for floats. When an integer column you expected comes back as floats, check it for gaps.

</div>

### Selecting and filtering

Square brackets with one column name give you a Series. With a list of names, you get a smaller DataFrame:

```python
mass = penguins["body_mass_g"]                         # a Series
mass.mean()                                            # 4201.75...
small = penguins[["species", "island", "body_mass_g"]] # a DataFrame
```

Filtering rows works exactly like the NumPy mask. A comparison on a column gives a Series of `True`/`False`, and indexing the DataFrame with it keeps the `True` rows:

```python
heavy = penguins[penguins["body_mass_g"] > 5000]   # 61 rows

# Combine conditions with & (and), | (or) and ~ (not).
# The parentheses are required.
gentoo_on_biscoe = penguins[
    (penguins["species"] == "Gentoo") & (penguins["island"] == "Biscoe")
]

# .isin checks membership in a list
two_islands = penguins[penguins["island"].isin(["Dream", "Torgersen"])]
```

Use `&` and `|`, not Python's `and` and `or`, which don't work on whole columns.

When you want rows and columns at the same time, use `.loc[rows, columns]`:

```python
penguins.loc[penguins["island"] == "Dream", ["species", "bill_length_mm"]]
```

You add a column by assigning to it, and the right-hand side is vectorized just as in NumPy:

```python
penguins["body_mass_kg"] = penguins["body_mass_g"] / 1000
penguins.sort_values("body_mass_kg", ascending=False).head(3)
```

To change only some rows of a column, also use `.loc`: `penguins.loc[penguins["body_mass_g"] > 6000, "size_class"] = "huge"`. Older tutorials sometimes write `penguins["size_class"][mask] = "huge"`. This is called **chained assignment**, and in pandas 3 it never changes the original DataFrame. pandas 3 also made every filtered result behave like an independent copy, so changing `heavy` above never changes `penguins`. If you see advice about `SettingWithCopyWarning`, it's from the pandas 2 era and you can skip it.

### Missing values

Real data has holes. A sensor failed, a user skipped a field, a model call timed out and never recorded its cost. pandas shows a missing number as `NaN` and missing text as `NaN` too, and `isna()` finds them:

```python
penguins.isna().sum()                       # missing values per column
penguins[penguins["body_mass_g"].isna()]    # the rows themselves
```

For the penguins, two birds are missing every measurement and eleven more are missing `sex`. Here's the part that trips people up: **pandas skips missing values by default.** `penguins["body_mass_g"].mean()` is the mean of the 342 weighed birds, and `.count()` returns 342, not 344. That's usually what you want, but it means a column that is 50% missing will still give you a confident-looking average. Always check `isna().sum()` before trusting a summary, and say how many rows it's based on.

You have three main options:

- **Drop** the rows: `penguins.dropna(subset=["body_mass_g"])` removes rows missing that column. Name the columns with `subset`; a bare `dropna()` drops a row if *any* column is missing, which can throw away far more than you meant to.
- **Fill** with a value: `penguins["sex"] = penguins["sex"].fillna("unknown")` turns gaps into an explicit category, so they show up in counts instead of vanishing.
- **Leave them**, and let pandas skip them, while reporting the counts.

Filling numbers with the mean or zero is tempting and often wrong. Filling missing costs with zero makes your system look cheaper than it is. Whatever you choose, write down why.

### Grouping and aggregating

Most questions about a table are "per something": average mass per species, total cost per model, error rate per prompt version. That's **groupby**: split the rows into groups by the values in a column, apply a calculation to each group, and combine the results into a new table. People call this split-apply-combine.

```python
penguins.groupby("species")["body_mass_g"].mean()
# species
# Adelie       3700.66
# Chinstrap    3733.09
# Gentoo       5076.02

summary = (
    penguins.groupby(["species", "sex"])
    .agg(
        birds=("body_mass_g", "size"),       # rows in the group, missing or not
        weighed=("body_mass_g", "count"),    # non-missing values only
        mean_mass_g=("body_mass_g", "mean"),
        max_flipper_mm=("flipper_length_mm", "max"),
    )
    .round(1)
    .reset_index()   # turn the group labels back into ordinary columns
)
```

The `.agg(new_name=(column, function))` form is called **named aggregation**, and it's the clearest way to compute several summaries at once. The result has one row per species and sex combination. Notice the `birds` and `weighed` columns: for Adelie penguins of unknown sex, there are 6 birds but only 5 were weighed. Putting both counts in your summary is a cheap habit that keeps you honest about missing data.

Wrapping a chain of methods in parentheses, one step per line, is the usual pandas style. It reads top to bottom like a recipe.

### Joining tables

Information often arrives in separate tables. Your call log has a `model` column, and a separate price list has one row per model with its price. To combine them, you **join** (pandas calls it **merge**) on the shared column:

```python
species_info = pd.DataFrame({
    "species": ["Adelie", "Chinstrap", "Gentoo"],
    "scientific_name": ["Pygoscelis adeliae", "Pygoscelis antarcticus", "Pygoscelis papua"],
})

merged = penguins.merge(
    species_info,
    on="species",            # the column both tables share
    how="left",              # keep every penguin, even without a match
    validate="many_to_one",  # many penguins per species, one row per species
)
merged["scientific_name"].isna().sum()  # 0: every penguin found a match
```

`how` decides what happens to rows without a match. `"left"` keeps all rows from the left table and fills `NaN` where there was no match; `"inner"` keeps only rows that matched on both sides. The `validate` argument is your safety net: if `species_info` accidentally had two rows for Gentoo, every Gentoo penguin would be duplicated and your counts would silently double. With `validate="many_to_one"`, pandas raises an error instead. After any merge, check the row count and look for unexpected `NaN`s.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [NumPy: the absolute basics for beginners](https://numpy.org/doc/stable/user/absolute_beginners.html). It covers creating arrays, shapes, indexing and broadcasting in more depth than this lesson.
   - Read up to and including "Basic array operations" and "Broadcasting". Skip the sections on saving arrays and matrices for now.
1. Work through the [pandas getting started tutorials](https://pandas.pydata.org/docs/getting_started/intro_tutorials/index.html), the official, beginner-friendly walkthrough with pictures of what each operation does.
   - Do the first three tutorials, plus "How to calculate summary statistics" and "How to combine data from multiple tables". "How to handle time series data with ease" is useful for the Data Explorer project.
1. Read the "Python for Data Analysis" chapters on [getting started with pandas](https://wesmckinney.com/book/pandas-basics) and [data cleaning and preparation](https://wesmckinney.com/book/data-cleaning). The book is free online and written by the creator of pandas. It predates pandas 3, so ignore anything about chained assignment.
1. Skim the pandas user guide on [group by: split-apply-combine](https://pandas.pydata.org/docs/user_guide/groupby.html), focusing on "Aggregation" and "Named aggregation", and on [merge, join and concatenate](https://pandas.pydata.org/docs/user_guide/merging.html), focusing on `merge` and its `validate` argument.
1. Practice in a notebook with the penguins data:
   - Find which island has the heaviest average penguin, and how many weighed penguins that average is based on.
   - Make a summary table with one row per species and year, showing the number of birds and the mean flipper length.
   - Count missing values per column, then decide what to do with each column that has gaps, and write one sentence explaining each choice in a Markdown cell.
1. Then do the [data exercise set](https://github.com/espiNovah/project-mimir/tree/main/exercises/data). Each exercise is a function with failing tests; run `uv run pytest data/<exercise>` from the `exercises/` folder until they pass.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What is vectorization, and what does indexing an array with a boolean mask do?](#numpy-arrays-and-vectorization)
- [What is the difference between a DataFrame and a Series?](#dataframes-and-series)
- [Why should you use `&` instead of `and` when combining filters?](#selecting-and-filtering)
- [Does pandas include missing values when it computes a mean, and why does that matter?](#missing-values)
- [What do the three steps of split-apply-combine mean?](#grouping-and-aggregating)
- [What does `validate="many_to_one"` protect you from in a merge?](#joining-tables)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [10 minutes to pandas](https://pandas.pydata.org/docs/user_guide/10min.html) is a fast tour of the whole library, good for review once the basics feel familiar.
- [The pandas guide to working with missing data](https://pandas.pydata.org/docs/user_guide/missing_data.html) explains `NaN`, `NA` and how each operation treats gaps.
- [The pandas copy-on-write guide](https://pandas.pydata.org/docs/user_guide/copy_on_write.html) explains the pandas 3 change to copies and chained assignment, if you meet older code that relies on it.
