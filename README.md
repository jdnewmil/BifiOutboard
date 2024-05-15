# BifiOutboard README

This repository contains a python package and Quarto paper describing a
method for deriving a simulated irradiance sensor reading usable for
testing the power capacity of photovoltaic power systems.

Developed with Quarto 1.3.450, and a miniconda-managed Python
environment defined in `environment.yml`.

Install miniconda or Anaconda and activate the environment:

```{sh}
conda env create -f environment.yml -v
conda activate pvcaptest
```

Use Quarto to build the pdf:

```{sh}
cd pvsc52
quarto render Pvsc52.qmd
```
