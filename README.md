## SciAssist
==============================

### Project Overview

Article Analysis & Research Assistant – A locally-hosted chatbot application powered by QWEN3 for intelligent article processing and analysis.
Full Description

This project is an in-development tool designed to help users work with and analyze articles efficiently. Built with the QWEN3 language model, it provides an interactive chat-based interface for document understanding, summarization, question-answering, and content analysis.

==============================

### Key Features:

- Local-First Architecture – Runs entirely on your machine with no cloud dependencies
- QWEN3 Intelligence – Utilizes the qcwind/qwen3-8b-instruct-Q4-K-M:latest model via Ollama for powerful language understanding
- Chat Interface – User-friendly conversational UI for seamless interaction with articles
- Custom Interface – Dedicated interface designed specifically for article analysis workflows
- Lightweight & Fast – Quantized model (Q4-K-M) for efficient local execution


Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── Agent.py           <- Main logic of the agent
    │   │  
    │   ├── AgentState.py       <- Store agent's status
    │   │
    │   ├── AgentTools.py         <- Tools for agent: search and agregation
    │   │   
    │   └── ui.py  <- User interface for working with the agent
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
