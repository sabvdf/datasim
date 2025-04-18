# DataSim

[![Test Status](https://github.com/sabvdf/datasim/actions/workflows/python-conda-pyright-pytest.yml/badge.svg)](https://github.com/sabvdf/datasim/actions/workflows/python-conda-pyright-pytest.yml)
[![Docs Status](https://github.com/sabvdf/datasim/actions/workflows/docs-pages.yml/badge.svg)](https://github.com/sabvdf/datasim/actions/workflows/docs-pages.yml)
[![Coverage Status](https://coveralls.io/repos/github/sabvdf/datasim/badge.svg?branch=main)](https://coveralls.io/github/sabvdf/datasim?branch=main)

Quick Python data generating simulation tool with readable code and optional dashboard.

> [!WARNING]
> Work in progress: this code base is not fully functional yet. Study at your own risk, usage is highly discouraged.

The code is meant to be as short as possible without too many bells and whistles, leaving anything other than the main simulation to external proven libraries.

The simulation is optionally tied to a Streamlit dashboard.

## API Documentation
Auto-generated, on [sabvdf.github.io/datasim](https://sabvdf.github.io/datasim/)

## Usage

See sample code, the basic setup is:

- Implement entities as subclasses of `datasim.Entity` and their behavior as subclasses of `datasim.State`
- Implement a subclass of `datasim.World`
  - Add any needed entities in `__init__()` after calling `super().__init__("NAME_HERE")`
  - Add plots in `update_plots()`.

Run main.py
