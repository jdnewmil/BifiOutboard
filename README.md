# BifiOutboard README

This repository contains a python package and Quarto paper describing a
method for deriving a simulated irradiance sensor reading usable for
testing the power capacity of photovoltaic power systems.

Developed with Quarto 1.3.450, and a miniconda-managed Python
environment defined in `environment.yml`.

While the intent was to make the `bifi_outboard` package work in conjunction
with the python `captest` package [^https://github.com/pvcaptest/pvcaptest],
the current version 0.12.1 injects JavaScript code that interferes with
building a combined code-execution-and-document Quarto file into a PDF.
Thus, a copy of v0.12.1 was incorporated into the `bifi_outboard.captest`
package with references to `holoviews` commented out and absolute import
references to `captest` changed to relative "dot" references. This vendored
copy of `captest` can be ignored if you do not plan to use Quarto, but some
other functions were modified in a more structural manner to allow for
adding computed columns to imported files... see `bifi_outboard.pvcaptest`
and the relevant code chunks in `pvsc52/Pvsc52.qmd`.

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
