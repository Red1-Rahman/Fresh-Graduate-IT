---
name: latex-writer
description: "Use this skill whenever writing, editing, or fixing a LaTeX (.tex) preparation guide for this repository: MSc/postgraduate admission prep, BCS or other competitive exam prep, lecturer recruitment guides, technical interview or aptitude material, and general CS/IT/networking/database/AI reference books. Trigger it when starting a new chapter or booklet from scratch, when a contributor reports a compile error, an overfull or underfull box warning, a figure or table landing on the wrong page or its own float page, ragged or unjustified body text, or a missing or blank Table of Contents, List of Figures, or List of Tables. Also consult it before opening a Pull Request that touches any .tex or .pdf file. The guidance here is editor and tool independent: it applies the same way in Overleaf, a local TeX installation, or any AI assistant helping with the repository."
compatibility: "pdflatex, xelatex, and lualatex, tested on Ubuntu, Windows, and macOS via TeX Live, MiKTeX, and MacTeX"
license: "Documents produced with this skill follow the repository default license, CC BY-SA 4.0"
---

# LaTeX Writer

This skill describes how to write and edit LaTeX preparation guides for Fresh Graduate IT so that a single `.tex` source compiles cleanly under `pdflatex`, `xelatex`, and `lualatex`, reads like a properly typeset book, and passes the repository's LaTeX Build workflow on the first try. It is written for any contributor or AI assistant working on this repository, not for one particular tool.

## 1. Where a new document belongs

The LaTeX Build workflow discovers documents automatically: it walks the repository for every `.tex` file (skipping `.git`, `.github`, `build`, and `dist`) and compiles the ones that contain both `\documentclass` and `\begin{document}`. A file without that pair is treated as an included section, not an entrypoint, so it is never compiled on its own.

Follow this convention for new material:

```
<track>/<topic-slug>/<topic-slug>.tex        % entrypoint: has \documentclass and \begin{document}
<track>/<topic-slug>/<topic-slug>.pdf        % compiled output, committed alongside the source
<track>/<topic-slug>/sections/*.tex          % optional \input files: no \documentclass, no \begin{document}
<track>/<topic-slug>/figures/*.pdf|*.png|*.svg
```

For example, `msc-cse-admission/computer-networks/computer-networks.tex`. Keep exactly one `\documentclass`/`\begin{document}` pair per book. If a guide grows past a few chapters, split each chapter into its own file under `sections/` and pull them in from the entrypoint with `\input{sections/01-introduction}`. This keeps the discovery step accurate and keeps Pull Request diffs focused on the chapter that actually changed.

Start every entrypoint with a short comment header so reviewers know what they are looking at without opening the PDF:

```latex
% Title:    Computer Networks, MSc CSE Admission Preparation
% Scope:    OSI/TCP-IP model, routing, congestion control, practice questions
% Engines:  verified with pdflatex, xelatex, lualatex
```

## 2. The book pattern

Use the `book` document class. It is the only standard class with `\frontmatter`, `\mainmatter`, and `\backmatter`, which is what gives a preparation guide its front matter (title page, contents, lists), body chapters, and back matter (appendices, answer keys, references) instead of a flat article.

```latex
\documentclass[12pt, a4paper, twoside]{book}
```

Use `oneside` instead of `twoside` for a guide that will mainly be read on screen rather than printed and bound. Both options compile identically on all three engines.

Structure follows the class's own hierarchy:

| Matter | Commands | Contains |
|---|---|---|
| Front matter | `\frontmatter` | Title page, license notice, `\tableofcontents`, `\listoffigures`, `\listoftables` |
| Main matter | `\mainmatter`, then `\chapter`, `\section`, `\subsection` | The actual study content, one `\chapter` per major topic |
| Back matter | `\backmatter`, `\appendix` | Answer keys, glossaries, references |

`\frontmatter` and `\backmatter` switch page numbering to roman numerals and suppress chapter numbering; `\mainmatter` resets numbering to arabic at page 1. Do not call `\pagenumbering` manually, the class already handles it.

## 3. One preamble, three engines

`pdflatex` reads 8-bit input and needs `inputenc`/`fontenc`. `xelatex` and `lualatex` are natively Unicode and use `fontspec` instead; loading `inputenc` under either of them will warn or error. Detect the engine once, at the top of the preamble, with the `iftex` package, and branch:

```latex
\usepackage{iftex}
\ifPDFTeX
  \usepackage[utf8]{inputenc}
  \usepackage[T1]{fontenc}
  \usepackage{lmodern}
\else
  % this branch runs for both xelatex and lualatex, fontspec works identically under both
  \usepackage{fontspec}
  \setmainfont{Latin Modern Roman}
\fi
```

`Latin Modern Roman` under `fontspec` keeps the same type family as `lmodern` under `pdflatex`, so the printed page looks the same no matter which engine produced it. This is the only part of the preamble that needs to differ by engine. Everything else below (`microtype`, `graphicx`, `hyperref`, and so on) loads the same way regardless of the compiler, which is what lets the same source build three times in the CI matrix with no per-engine edits.

## 4. Justified text without breaking the build

LaTeX justifies body paragraphs by default, so most long-paragraph content needs no special markup. Two things do need attention because the build workflow treats every `Overfull \hbox` and `Overfull \vbox` as a failure, not a warning.

Load `microtype` early in the preamble. It improves justification through character protrusion on every engine, and through font expansion, which is strongest under `pdflatex` and `lualatex` and more limited under `xelatex`, so justified paragraphs need less forced stretching to begin with. Set an emergency stretch as a last resort so a single tight line becomes underfull rather than overfull:

```latex
\usepackage{microtype}
\setlength{\emergencystretch}{3em}
```

Content that would otherwise default to ragged alignment (table cells set with `p{}` columns, block quotes, footnotes in a narrow column) does not automatically inherit the body's justification. Wrap it explicitly with `ragged2e`:

```latex
\usepackage{ragged2e}
...
\begin{justify}
A long explanatory note that should read like the surrounding body text
instead of a ragged block quote.
\end{justify}
```

Do not force justification onto content that reads better ragged: short captions, code listings, addresses, and anything already narrow enough that justifying it would open large gaps between words.

Long inline URLs and unbroken identifiers are a common source of an overfull line. Wrap them with `\url{}` from `hyperref` (loaded in Section 8) rather than typing them as plain text, and set code listings to `breaklines=true` (`listings` or `minted`) instead of letting a long line run off the page.

## 5. Figures and tables that will not break the build

LaTeX tries placement specifiers in the order given: `h` (here), `t` (top of a page), `b` (bottom), `p` (a dedicated float page), with `!` relaxing LaTeX's internal fit thresholds and `H` (from the `float` package) forcing the float to the exact point in the source.

```latex
\usepackage{graphicx}
\usepackage{float}
\usepackage[section]{placeins}
```

Rules that keep the placement sane and the build green:

- Default to `[htbp]`, never a bare `[h]`. A single specifier gives LaTeX only one option and is the most common reason a figure ends up somewhere unexpected.
- Always `\centering` inside the float, and size images relative to the text block, never with an absolute unit: `\includegraphics[width=0.8\linewidth]{...}`. A fixed `cm`/`pt`/`in` width wider than the text block is a guaranteed overfull `\hbox`.
- Put `\caption{}` then `\label{fig:...}`, in that order, so the label picks up the right number, and refer to the float from the prose with `\cref{fig:...}` (from `cleveref`, see Section 8) rather than "the figure below". LaTeX may still move the float; the cross-reference will not.
- Reserve `[H]` for small floats you have visually confirmed fit on the current page. `[H]` bypasses the placement algorithm entirely, so a float that does not quite fit will not fall through to the next page. It gets crammed into the remaining space instead, which is one of the most reliable ways to trigger the `Overfull \vbox` that this repository's build fails on.
- Add `\usepackage[section]{placeins}` so a float can never drift past a `\section` boundary. Chapters already flush pending floats on their own (a new `\chapter` forces a page break), but sections do not, and a diagram meant for one topic drifting into the next one is confusing in a study guide that readers skim by section.
- If floats still keep escaping to a dedicated float page, relax LaTeX's internal float-per-page limits rather than fighting them one figure at a time:

```latex
\renewcommand{\topfraction}{0.9}
\renewcommand{\bottomfraction}{0.9}
\renewcommand{\textfraction}{0.1}
\setcounter{topnumber}{4}
\setcounter{bottomnumber}{4}
```

- For two related diagrams side by side, use `subcaption`'s `subfigure` environment inside a single `figure`, rather than two separate floats competing for the same slot.
- Size tables the same way as images: use `p{width}` columns for anything that wraps, not fixed `l`/`c`/`r` columns holding long text, and prefer `booktabs` (`\toprule`, `\midrule`, `\bottomrule`) over a full grid of vertical and horizontal rules for a cleaner, book-like table.

### Reading the build log

| Symptom | Likely cause | Fix |
|---|---|---|
| `Overfull \hbox` in body text | A long word, URL, or inline code span, or not enough stretch available | `microtype` plus `\emergencystretch`; wrap URLs with `\url{}`; `breaklines=true` for listings |
| `Overfull \hbox` inside a table | Fixed `l`/`c`/`r` column holding long text | Switch that column to `p{width}` (or `>{\raggedright\arraybackslash}p{width}`) |
| `Overfull \hbox` around an image | Width given in an absolute unit wider than the text block | `width=0.8\linewidth` or `\textwidth`, never a hardcoded `cm`/`pt`/`in` |
| `Overfull \vbox` right after a `[H]` figure | `[H]` crammed a float into a page it did not fit on | Switch to `[htbp]`; keep `[H]` only for confirmed small floats |
| Figure or table several pages from where it is discussed | Too many queued floats, or the float-per-page limit reached | `placeins`, relaxed `\topfraction`/`\bottomfraction`/`\textfraction`, and `\cref{}` instead of "above/below" |
| `Underfull \hbox (badness ...)` | A ragged or narrow column with a long word and no hyphenation point | Confirm `babel` is loaded for the right language; add a manual `\-` as a last resort |

Overfull boxes are a hard failure in the build workflow. Underfull ones are only a warning, but they are still worth fixing before opening a Pull Request.

## 6. Table of Contents, List of Figures, List of Tables

All three are single commands, placed in front matter after the title page and before `\mainmatter`:

```latex
\frontmatter
% title page here
\tableofcontents
\listoffigures
\listoftables
\mainmatter
```

Every entry needs a `\caption{}` on the corresponding figure or table; LaTeX cannot list what has no caption. If the two lists should themselves appear as entries inside the Table of Contents (rather than only the chapters), add `\usepackage[nottoc]{tocbibind}`.

Cross-references, and the Table of Contents itself, need the auxiliary files from a previous run to resolve. A single compiler pass produces a Table of Contents and figure numbers, but they read `??` or reflect a stale run. Compile locally with `latexmk -pdf`, `latexmk -xelatex`, or `latexmk -lualatex` (it reruns the engine automatically until the references settle), or run the plain engine two or three times by hand, before committing the PDF. The LaTeX Build workflow only compiles once per engine to catch fatal errors; it is not what produces the final, reference-complete PDF you commit.

## 7. Colourblind-safe, accessible figures

CONTRIBUTING.md asks for the Okabe-Ito palette, sufficient contrast, and never relying on color alone. Define the palette once and reuse it in every figure and diagram:

```latex
\usepackage{xcolor}
\definecolor{OIorange}{RGB}{230,159,0}
\definecolor{OIskyblue}{RGB}{86,180,233}
\definecolor{OIgreen}{RGB}{0,158,115}
\definecolor{OIyellow}{RGB}{240,228,66}
\definecolor{OIblue}{RGB}{0,114,178}
\definecolor{OIvermillion}{RGB}{213,94,0}
\definecolor{OIpurple}{RGB}{204,121,167}
```

Pair every color distinction with a second cue: a line style, a fill pattern, a marker shape, or a direct label, so the figure still reads correctly in grayscale or to a colorblind reader. `TikZ` (works unmodified under all three engines) is a good default for diagrams that need this kind of precise, reproducible styling instead of a raster screenshot.

## 8. Licensing every document

Every entrypoint should carry a short, visible license notice on its title page, plus matching PDF metadata:

```latex
\usepackage{hyperref}
\usepackage{bookmark}
\usepackage{cleveref}
\hypersetup{
  pdftitle={Computer Networks: MSc CSE Admission Preparation},
  pdfauthor={Fresh Graduate IT contributors},
  pdfsubject={Preparation guide},
  pdfkeywords={CSE, MSc admission, computer networks},
  colorlinks=true,
  linkcolor=OIblue,
  citecolor=OIgreen,
  urlcolor=OIvermillion
}

\begin{titlepage}
  \centering
  {\LARGE\bfseries Computer Networks\par}
  \vspace{0.5cm}
  {\large MSc CSE Admission Preparation\par}
  \vfill
  {\small
    Copyright \textcopyright{} the contributors of Fresh Graduate IT.\\
    Licensed under the Creative Commons Attribution-ShareAlike 4.0
    International License (CC BY-SA 4.0).\\
    \url{https://creativecommons.org/licenses/by-sa/4.0/}
  \par}
\end{titlepage}
```

Load `hyperref` after the other packages in the preamble (it patches many of them), then `bookmark`, then `cleveref`, in that order. If a chapter reuses third-party material (a past exam question, a diagram from another source), keep that material's own license and attribution intact next to it instead of relying on the repository-wide notice, exactly as CONTRIBUTING.md requires.

## 9. A complete, ready-to-copy skeleton

The following compiles unmodified with `pdflatex`, `xelatex`, and `lualatex`.

```latex
\documentclass[12pt, a4paper, twoside]{book}

\usepackage{iftex}
\ifPDFTeX
  \usepackage[utf8]{inputenc}
  \usepackage[T1]{fontenc}
  \usepackage{lmodern}
\else
  \usepackage{fontspec}
  \setmainfont{Latin Modern Roman}
\fi

\usepackage[english]{babel}
\usepackage{microtype}
\usepackage{ragged2e}
\setlength{\emergencystretch}{3em}

\usepackage{graphicx}
\usepackage{float}
\usepackage{caption}
\captionsetup{margin=10pt, font=small, labelfont=bf}
\usepackage{subcaption}
\usepackage[section]{placeins}
\usepackage{booktabs}
\renewcommand{\topfraction}{0.9}
\renewcommand{\bottomfraction}{0.9}
\renewcommand{\textfraction}{0.1}
\setcounter{topnumber}{4}
\setcounter{bottomnumber}{4}

\usepackage{xcolor}
\definecolor{OIorange}{RGB}{230,159,0}
\definecolor{OIblue}{RGB}{0,114,178}
\definecolor{OIgreen}{RGB}{0,158,115}
\definecolor{OIvermillion}{RGB}{213,94,0}

\usepackage{hyperref}
\usepackage{bookmark}
\usepackage{cleveref}
\hypersetup{
  pdftitle={Example Preparation Guide},
  pdfauthor={Fresh Graduate IT contributors},
  colorlinks=true,
  linkcolor=OIblue,
  citecolor=OIgreen,
  urlcolor=OIvermillion
}

\begin{document}

\frontmatter
\begin{titlepage}
  \centering
  {\LARGE\bfseries Example Preparation Guide\par}
  \vspace{0.5cm}
  {\large A Fresh Graduate IT study guide\par}
  \vfill
  {\small
    Copyright \textcopyright{} the contributors of Fresh Graduate IT.\\
    Licensed under CC BY-SA 4.0.\\
    \url{https://creativecommons.org/licenses/by-sa/4.0/}
  \par}
\end{titlepage}

\tableofcontents
\listoffigures
\listoftables

\mainmatter

\chapter{Example Topic}
\label{ch:example}

Write the explanation as ordinary justified paragraphs. \Cref{fig:example}
shows the accompanying diagram, and \cref{tab:example} summarises the
comparison discussed above.

\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.75\linewidth]{figures/example-diagram}
  \caption{An example diagram, scaled to the text width so it can never overflow the margin.}
  \label{fig:example}
\end{figure}

\begin{table}[htbp]
  \centering
  \caption{An example comparison table.}
  \label{tab:example}
  \begin{tabular}{@{}lll@{}}
    \toprule
    Item & Property A & Property B \\
    \midrule
    Row one & value & value \\
    Row two & value & value \\
    \bottomrule
  \end{tabular}
\end{table}

\backmatter
\appendix
\chapter{Answer Key}

\end{document}
```

## 10. Pre-submission checklist

- [ ] Compiles with `pdflatex`, `xelatex`, and `lualatex` (or trust the CI matrix, but check the log for each)
- [ ] No `Overfull \hbox` or `Overfull \vbox` in any of the three logs
- [ ] Table of Contents, List of Figures, and List of Tables all show real numbers, not `??`, after a multi-pass local build
- [ ] Every figure and table has a `\caption{}`, a `\label{}`, and is referenced from the prose with `\cref{}`
- [ ] Diagrams use the Okabe-Ito palette and a second visual cue besides color
- [ ] Title page carries the CC BY-SA 4.0 notice, and any third-party material keeps its own license
- [ ] PDF regenerated from the current `.tex` source and committed together with it
- [ ] Opened the PDF and visually checked layout, page breaks, and float placement

## 11. Further reading

- [Positioning images and tables](https://www.overleaf.com/learn/latex/Positioning_images_and_tables), Overleaf
- [Fix LaTeX Figure Placement Issues](https://trybibby.com/blog/latex-figure-placement), Bibby
- [Lists of tables and figures](https://www.overleaf.com/learn/latex/Lists_of_tables_and_figures), Overleaf
- [Supporting modern fonts with XeLaTeX](https://www.overleaf.com/learn/latex/XeLaTeX), Overleaf
- CTAN documentation for `microtype`, `placeins`, `cleveref`, and `float` covers the full option lists behind the defaults used above
