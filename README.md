# TwAI Guidelines

## TwAI Dictionary

A dictionary of artificial intelligence, machine learning, and trustworthy AI
terms. Each term has **several definitions**, each attributed to its source,
such as NIST, ISO/IEC, the EU AI Act, the OECD, the EU High-Level Expert
Group, textbooks, and research papers. Many entries end with a note on how the
definitions differ.

The dictionary is published in two forms, both generated from the same data:

- **Website** (Sphinx, Furo theme): searchable term pages, an A–Z list, a
  table of which organisations define which terms, and a list of sources.
  It is published to GitHub Pages from `main`.
- **PDF** (LaTeX): a print-style dictionary with running heads and an index.
  It is linked from the website and attached to every workflow run.

### Layout

| Path | Contents |
| --- | --- |
| `dictionary/ai.yaml` | General AI terms (**source of truth**) |
| `dictionary/ml.yaml` | Machine learning terms (**source of truth**) |
| `dictionary/trustworthy.yaml` | Trustworthy AI terms (**source of truth**) |
| `references.bib` | Every cited source |
| `tools/build.py` | Checks the data and generates the LaTeX and site pages |
| `twai-dictionary.tex`, `twaidict.sty` | PDF layout |
| `docs/` | Sphinx configuration, landing page, and CSS |

`entries/` and `docs/generated/` are generated. Do not edit them.

### Building

You need Python 3 and, for the PDF, TeX Live with `latexmk` and `biber`.

```sh
pip install -r requirements.txt
make            # PDF and website
make pdf        # twai-dictionary.pdf only
make site       # website only, in docs/_build/html
make distclean  # remove all build output
```

On every pull request, GitHub Actions builds both forms. On `main`, it also
publishes the site to GitHub Pages. To enable publishing, set
**Settings → Pages → Build and deployment → Source** to **GitHub Actions**.

### Adding or editing a term

Edit the domain's YAML file, keeping terms in alphabetical order:

```yaml
- key: model-card              # unique id, used in links
  term: Model Card
  alias: datasheet             # optional
  definitions:
  - source: mitchell-2019      # key in references.bib
    text: >-
      Paraphrased definition, with *emphasis* and “quotes” if needed.
  - source: eu-ai-act
    at: Art. 11                # optional clause, article, or page
    quote: true                # only for text copied exactly from the source
    text: >-
      Verbatim definition.
  note: >-
    How these definitions differ (optional).
  related: [transparency, auditability]
```

- Add each new source to `references.bib`. Give standards and policy
  documents a `shorthand`, such as `NIST AI RMF`.
- Use `quote: true` only for text copied exactly from the source.
- Text may use `*emphasis*`, curly quotes, and `$inline math$`.
- `tools/build.py` fails the build if terms are out of order, a key is
  duplicated, a source or related term does not exist, or a term has fewer
  than two definitions.

### Accuracy

Definitions without `quote: true` are paraphrases. Check the wording against
the original before quoting any definition in a formal document, especially
for standards (ISO/IEC) and regulation (EU AI Act), which may be amended.
