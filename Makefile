# Build the TwAI dictionary as a PDF and as a Sphinx website.
# Requires Python (see requirements.txt) and TeX Live with latexmk and biber.
.PHONY: all pdf site data clean distclean

DATA := $(wildcard dictionary/*.yaml) references.bib tools/build.py

all: pdf site

data:
	python3 tools/build.py all

pdf: twai-dictionary.pdf

twai-dictionary.pdf: twai-dictionary.tex twaidict.sty $(DATA)
	python3 tools/build.py latex
	latexmk -interaction=nonstopmode -halt-on-error twai-dictionary.tex

# The site links to the PDF, so build that first when LaTeX is available.
site:
	python3 tools/build.py site
	mkdir -p docs/_extra
	if [ -f twai-dictionary.pdf ]; then cp twai-dictionary.pdf docs/_extra/; fi
	sphinx-build -W --keep-going -b html docs docs/_build/html

clean:
	latexmk -c
	rm -rf docs/_build

distclean: clean
	latexmk -C
	rm -rf entries docs/generated docs/_extra
