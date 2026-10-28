### Introduction

You've learned to explore data in a notebook, wrangle it with pandas and draw honest charts with matplotlib. In this project you'll put the three together the way you'll do it at work: take a real public dataset you didn't make, ask it a handful of specific questions, and publish a short report with charts that a stranger can read in five minutes and reproduce from a fresh clone.

The suggested dataset is a good fit for someone heading into AI engineering: [Epoch AI's database of notable AI models](https://epoch.ai/data/ai-models). It has one row per model, from the 1950s to models released a few weeks ago, with columns for the organization, publication date, domain, number of parameters, training compute, training cost and how the model was released. It's real, it's updated regularly, and it's messy in instructive ways. About half the rows have no training compute figure, and the newest, biggest models are the most likely to be missing it, because their makers don't publish it. Noticing and explaining that kind of gap is a core skill in this project.

The project also practices the code habits from Python Fundamentals. Cleaning and analysis live in a tested Python package, not only in notebook cells, and GitHub Actions checks every push, as it has since the Expense Tracker.

### Before you start

- Create a new GitHub repository named `mimir-data-explorer` and set it up as a `uv` project with `pandas` and `matplotlib` as dependencies, and `pytest`, `ruff` and `jupyterlab` as dev dependencies. Use the package layout from the Notebooks and Colab lesson: code in `src/explorer/`, tests in `tests/`, notebooks in `notebooks/`.
- Download the data. The notable models CSV is free under a Creative Commons Attribution license, so you may use it as long as you credit Epoch AI:

  ```bash
  mkdir -p data
  curl -L -o data/notable_ai_models.csv https://epoch.ai/data/notable_ai_models.csv
  ```

  Add `data/` to `.gitignore`. The file is a couple of megabytes and changes as Epoch adds models, so instead of committing it, put the download command in your README and record the date you downloaded it. Your numbers are only reproducible against a dated snapshot.
- Read the [dataset documentation](https://epoch.ai/data/ai-models-documentation) for the columns you plan to use. You need to know what "Training compute (FLOP)" measures, and what Epoch means by "notable", before you draw conclusions from them.
- **Choosing a different dataset** is allowed if it's public, free to download without signing in, licensed for reuse, has at least 500 rows, includes at least one date or category column, and has some missing values. [Our World in Data's CO2 dataset](https://github.com/owid/co2-data) is a good alternative. Don't use the penguins data from the lessons. Adapt the Epoch-specific hints below to your dataset.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Look before you plan

Spend your first hour in a notebook with `info()`, `isna().sum()`, `describe()` and `value_counts()` on a few columns before you write any package code. You'll find surprises: a `Domain` value like `Language,Vision,Multimodal` that packs several categories into one cell, numbers like `3.8e25` that only make sense on a log scale, and columns that are mostly empty. Your questions should come from what you find.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

#### The questions

1. Write down three to five specific questions you'll answer, at the top of your report. "How has training compute for notable language models grown since 2015?" is specific. "What's interesting about AI models?" is not. At least one question must compare groups (for example, open-weights versus API-only models) and at least one must look at change over time.

#### The package

1. Write a loading function, for example `load_models(path) -> pd.DataFrame` in `src/explorer/clean.py`, that reads the CSV and returns a clean DataFrame: only the columns you use, renamed to short `snake_case` names (`training_compute_flop`, not `Training compute (FLOP)`), with dates parsed and numbers stored as numbers.
   - Hint: `pd.read_csv(path, parse_dates=["Publication date"])` parses the dates, and `df["published"].dt.year` then gives you the year as a column. The "How to handle time series data with ease" tutorial, linked from the NumPy and pandas Basics lesson, covers dates.
1. Handle missing values deliberately. For each column you use, decide whether to drop, fill or keep the gaps, following the Missing values section of the NumPy and pandas Basics lesson, and write a docstring or comment that says why. Never fill missing compute, parameter or cost values with zero.
1. If you analyze a column that packs several values into one cell, like `Domain`, split it so each value is counted properly.
   - Hint: `df.assign(domain=df["domain"].str.split(",")).explode("domain")` turns one row with three domains into three rows, one per domain. Say in your report that a multimodal model is counted once in each of its domains.
1. Put each analysis in its own function that takes a DataFrame and returns a DataFrame, for example `models_per_year(df)` or `compute_by_access(df, since=2020)`, in `src/explorer/analysis.py`. Every summary table it returns must include the number of rows behind each figure, as in the `birds` and `weighed` columns in the lesson.
1. Write a script, for example `src/explorer/charts.py`, that loads the data, runs your analysis functions and saves every chart in the report to `charts/` as a PNG. Running one command, such as `uv run python -m explorer.charts data/notable_ai_models.csv`, must regenerate all of them. Accept the CSV path as a command-line argument with `argparse`, as in the Command-Line Apps lesson.

#### The charts

1. Make at least four charts that each answer one of your questions, using at least three different chart types from the Plotting With matplotlib lesson. Each must have axis labels with units, a title that states the finding, and a legend whenever there's more than one series.
1. At least one chart must compare group averages or rates with error bars, and its title or caption must say what the error bars show (for example, "95% CI of the mean").
   - Hint: for compute, average the logarithm rather than the raw values. `np.log10(df["training_compute_flop"])` turns `3.8e25` into `25.6`, so one giant model doesn't swamp the mean. Label the axis accordingly, for example "Training compute (log10 FLOP)".
1. Use a log scale (`ax.set_yscale("log")`) for any chart of a quantity that spans several orders of magnitude, such as compute or parameters, and label it.

#### Testing and CI

1. Write at least five pytest tests for your cleaning and analysis functions. They must run on small DataFrames or CSV files you build by hand inside the test (a CSV written to `tmp_path` works well), never on the real download, so they're fast and their correct answers are known. Include:
   - a test that your loader parses dates and numbers into the right types;
   - a test that rows with missing values are handled the way your docstring says;
   - a test of one summary function against totals you've worked out by hand.
   - Hint: `pd.testing.assert_frame_equal(result, expected)` compares two DataFrames and prints exactly where they differ.
1. Add a GitHub Actions workflow that runs `uv run ruff check .`, `uv run ruff format --check .` and `uv run pytest` on every push, as in the Linting, Formatting and CI lesson.

#### The report

1. Write the report as `REPORT.md`, or as a notebook in `notebooks/` that you restart and run from top to bottom before committing, as in the Notebooks and Colab lesson. Either way it should take about five minutes to read. For each question, give the chart, the answer in one or two plain sentences, and the numbers behind it.
1. Include a section on the data's limits: how many rows had missing values in each column you used, which kinds of models are most likely to be missing data, and how that could bias your answers. For example, if recent frontier models rarely publish their training compute, what does that do to a chart of compute over time?
1. Credit the dataset in the report and README with its name, Epoch AI as the source, a link and your download date.
1. Push your project to GitHub with a README that explains what it does, how to download the data, how to regenerate the charts and run the tests, and what you learned. Link to the report from the top of the README.

#### Evidence

- A passing GitHub Actions run of ruff and pytest on your latest commit, with the workflow's status badge at the top of the README.
- The output of `uv run pytest` pasted into the README, showing at least five passing tests.
- The commands to go from a fresh clone to regenerated charts, with your data's download date. A reviewer who runs them should get the same charts, and your committed PNGs in `charts/` should match what the script produces.

#### Extra credit

- Add a `--since` or `--domain` option to your chart script and show two versions of one chart in the report, such as all models versus language models only.
- Fit a straight line to log compute over time with `np.polyfit` and report the growth rate as "compute multiplies by X per year". Say how much your answer changes when you start the fit in 2010 instead of 2015.
- Replace the 1.96-standard-error interval on one chart with a bootstrap confidence interval: resample the rows with replacement 1,000 times, recompute the mean each time, and take the 2.5th and 97.5th percentiles. Compare the two intervals. You'll meet the bootstrap properly in the Eval Statistics lesson.
- Open your report notebook in Colab from GitHub, as in the Notebooks and Colab lesson, and add a "Run in Colab" link to the README.

</div>

### Submitting your work

A strong submission is a report a busy person would actually read. Each question gets a chart whose title already tells them the answer, a sentence or two in plain English, and an honest note on how sure you are. The limits section is often the best part: "two thirds of the models in my snapshot released since 2025 have no published training compute, so the trend after 2024 rests on a few dozen models" is a more valuable sentence than any chart, because it shows you checked whether the data could answer the question before you answered it.

On the code side, a reviewer should find small, named analysis functions with tests that check real numbers, a green CI badge, and one command that rebuilds every chart. Keep this repository. You'll analyze far messier tables later, such as logs of your own model calls and eval results, and the structure you build here (a tested package for the logic, a notebook or report for the story) carries over directly.
