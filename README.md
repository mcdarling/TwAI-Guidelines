# TwAI Guidelines

## TwAI Dictionary

`twai-dictionary.tex` is a LaTeX dictionary of artificial intelligence, machine
learning, and trustworthy AI terms. Each term has **several definitions**, each
attributed to its source, such as NIST, ISO/IEC, the EU AI Act, the OECD, the
EU High-Level Expert Group, textbooks, and research papers. Many entries end
with a note on how the definitions differ.

The dictionary has three domains:

| File | Domain |
| --- | --- |
| `entries/ai.tex` | General AI: AI system, agentic AI, foundation model, LLM, hallucination, … |
| `entries/ml.tex` | Machine learning: supervised learning, overfitting, transformer, RLHF, … |
| `entries/trustworthy.tex` | Trustworthy AI: fairness, explainability, robustness, human oversight, … |

The PDF ends with a list of sources and an index of all terms and
abbreviations.

### Building

You need TeX Live with `latexmk`, `biber`, and `makeindex`.

```sh
make            # builds twai-dictionary.pdf
make clean      # removes intermediate files
```

On every push to `main` and on every pull request, GitHub Actions builds the
PDF. You can download it from the workflow run's artifacts.

### Adding or editing a term

Entries use the macros in `twaidict.sty`:

```latex
\begin{entry}{model-card}{Model Card}[datasheet]    % key, term, optional alias
  \defn{mitchell-2019}{Paraphrased definition ...}   % "adapted from" a source
  \defn*[Art.~13]{eu-ai-act}{Verbatim quotation ...} % quoted, with a pinpoint
  \note{How these definitions differ ...}            % optional
  \related{transparency,auditability}                % keys of related entries
\end{entry}
```

- Keep entries in alphabetical order within each file.
- Add each new source to `references.bib`. Give it a `shorthand` if it is a
  standard or policy document.
- Use `\defn*` only for text copied exactly from the source. Otherwise use
  `\defn`, which prints *adapted from*.
- Use `\xref{key}` to link to another entry in running text.

### Accuracy

Definitions marked *adapted from* are paraphrases. Check the wording against
the original before quoting any definition in a formal document, especially
for standards (ISO/IEC) and regulation (EU AI Act), which may be amended.
