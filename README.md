# BifiOutboard README

This repository contains a python package and Quarto paper describing a
method for deriving a simulated irradiance sensor reading usable for
testing the power capacity of photovoltaic power systems.

Developed with Quarto 1.4.554, and a miniconda-managed Python
environment defined in `environment_pinned.yml`.

Install miniconda or Anaconda and activate the environment:

```{sh}
# developed on Windows. environment_pinned.yml may be specific to this operating system.
# environment_from-history.yml file may work on Linux or Mac.
conda env create --name bifioutboard -f environment_pinned.yml -v
conda activate bifioutboard
# if you wish to add extra conda package dependencies then install them here before using pip
# bifi-outboard package is installed in source editing mode
pip install -e src
```

Once the environment is setup with bifi-outboard pip-installed:
  - do not add more conda packages. Create a new environment and add them before using pip.
  - To re-activate the environment, it is not necessary to use pip again.

Note that Quarto and LaTeX are assumed to be pre-installed on your system... refer to documentation for those software packages for installation instructions relevant to your operating system.

Use Quarto to build the pdf:

```{sh}
cd pvsc52
quarto render Pvsc52.qmd
```

or the presentation:

```{sh}
cd pvsc52_presentation
quarto render Newmiller_BifiASTMCapTestOutboardOral_2024.qmd
```

The analysis/prelim.qmd file may be useful if you explore this package.
