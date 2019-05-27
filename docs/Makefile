# Minimal makefile for Sphinx documentation
SPHINXOPTS    = -n -W --keep-going
SPHINXBUILD   = sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

.PHONY: Makefile

html: Makefile
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
