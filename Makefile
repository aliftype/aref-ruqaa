NAME=ArefRuqaa
VERSION=0.10
EXT=ttf
LATIN=EulerText

SRCDIR=sources
BLDDIR=build
DOCDIR=documentation
TOOLDIR=tools
TESTDIR=tests
DIST=$(NAME)-$(VERSION)

PY ?= python
BUILD=$(TOOLDIR)/build.py
SFDLINT=$(TOOLDIR)/sfdlint.py

FONTS=Regular Bold

SFD=$(FONTS:%=$(SRCDIR)/$(NAME)-%.sfdir)
OTF=$(FONTS:%=$(NAME)-%.$(EXT))
PDF=$(DOCDIR)/$(NAME)-Table.pdf

LNT=$(FONTS:%=$(TESTDIR)/$(NAME)-%.lnt)

export SOURCE_DATE_EPOCH ?= 0

.PRECIOUS: $(BLDDIR)/master_otf/$(LATIN)-%.otf

all: otf doc

otf: $(OTF)
doc: $(PDF)
lint: $(LNT)
check: lint

$(BLDDIR)/master_otf/$(LATIN)-%.otf: $(SRCDIR)/$(LATIN)-%.ufo
	@echo "   FM	$(@F)"
	@mkdir -p $(BLDDIR)
	@cd $(BLDDIR); fontmake                                                \
	                        --verbose WARNING                              \
	                        --production-names                             \
	                        -u $(realpath $<)                              \
	                        -o otf                                         \
	                ;

$(NAME)-%.$(EXT): $(SRCDIR)/$(NAME)-%.sfdir $(BLDDIR)/master_otf/$(LATIN)-%.otf $(SRCDIR)/$(NAME).fea Makefile $(BUILD)
	@echo "   FF	$@"
	@$(PY) $(BUILD) --version=$(VERSION) --out-file=$@ --feature-file=$(word 3,$+) $< $(word 2,$+)

$(TESTDIR)/%.lnt: $(SRCDIR)/%.sfdir $(SFDLINT)
	@echo "   LNT	$<"
	@$(PY) $(SFDLINT) $< $@

$(DOCDIR)/$(NAME)-Table.pdf: $(NAME)-Regular.$(EXT)
	@echo "   GEN	$@"
	@mkdir -p $(DOCDIR)
	@fntsample --font-file $< --output-file $@.tmp                         \
		   --write-outline --use-pango                                 \
		   --style="header-font: Noto Sans Bold 12"                    \
		   --style="font-name-font: Noto Serif Bold 12"                \
		   --style="table-numbers-font: Noto Sans 10"                  \
		   --style="cell-numbers-font:Noto Sans Mono 8"
	@mutool clean -d -i -f -a $@.tmp $@
	@rm -f $@.tmp

dist:
	@make -B
	@mkdir -p $(NAME)-$(VERSION)
	@cp $(OTF) $(PDF) $(NAME)-$(VERSION)
	@cp OFL.txt $(NAME)-$(VERSION)
	@sed -e "/^!\[Sample\].*./d" README.md > $(NAME)-$(VERSION)/README.txt
	@zip -r $(NAME)-$(VERSION).zip $(NAME)-$(VERSION)

clean:
	@rm -rf $(BLDDIR) $(OTF) $(PDF) $(NAME)-$(VERSION) $(NAME)-$(VERSION).zip
