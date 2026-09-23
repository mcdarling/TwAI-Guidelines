# Build the TwAI dictionary PDF. Requires TeX Live with latexmk and biber.
.PHONY: all clean distclean

all: twai-dictionary.pdf

twai-dictionary.pdf: twai-dictionary.tex twaidict.sty references.bib entries/*.tex
	latexmk -interaction=nonstopmode -halt-on-error twai-dictionary.tex

clean:
	latexmk -c

distclean:
	latexmk -C
