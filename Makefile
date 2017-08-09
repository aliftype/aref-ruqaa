NAME=ArefRuqaa
VERSION=0.7
EXT=ttf
LATIN=EulerText

SRCDIR=sources
BLDDIR=build
DOCDIR=documentation
TOOLDIR=tools
TESTDIR=tests
DIST=$(NAME)-$(VERSION)

PY=python2
PY3=python3
BUILD=$(TOOLDIR)/build.py
RUNTEST=$(TOOLDIR)/runtest.py
SFDLINT=$(TOOLDIR)/sfdlint.py

FONTS=Regular Bold
TESTS=wikipedia-dotless yeh-ragaa

SFD=$(FONTS:%=$(SRCDIR)/$(NAME)-%.sfdir)
OTF=$(FONTS:%=$(NAME)-%.$(EXT))
PDF=$(DOCDIR)/$(NAME)-Table.pdf

TST=$(TESTS:%=$(TESTDIR)/%.txt)
SHP=$(TESTS:%=$(TESTDIR)/%.shp)
RUN=$(TESTS:%=$(TESTDIR)/%.run)
LNT=$(FONTS:%=$(TESTDIR)/$(NAME)-%.lnt)

ttx?=false
crunch?=false

all: otf doc

otf: $(OTF)
doc: $(PDF)
lint: $(LNT)
check: lint $(RUN)

$(BLDDIR)/master_otf/$(LATIN)-%.otf: $(SRCDIR)/$(LATIN)-%.ufo
	@echo "   FM	$(@F)"
	@mkdir -p $(BLDDIR)
	@INPUT=$(realpath $<);                                                 \
	 pushd $(BLDDIR) 1>/dev/null;                                          \
	 fontmake -u $$INPUT -o otf --verbose WARNING;                         \
	 popd 1>/dev/null;

$(NAME)-%.$(EXT): $(SRCDIR)/$(NAME)-%.sfdir $(BLDDIR)/master_otf/$(LATIN)-%.otf $(SRCDIR)/$(NAME).fea Makefile $(BUILD)
	@echo "   FF	$@"
	@FILES=($+); $(PY) $(BUILD) --version=$(VERSION) --out-file=$@ --feature-file=$${FILES[2]} $${FILES[0]} $${FILES[1]}
ifeq ($(ttx), true)
	@echo "   TTX	$@"
	@pyftsubset $@ --output-file=$@.tmp --unicodes='*' --layout-features='*' --name-IDs='*' --notdef-outline
	@mv $@.tmp $@
endif
ifeq ($(crunch), true)
	@echo "   FC	$@"
	@font-crunch -q -j8 -o $@ $@
endif

$(TESTDIR)/%.run: $(TESTDIR)/%.txt $(TESTDIR)/%.shp $(NAME)-Regular.$(EXT)
	@echo "   TST	$*"
	@$(PY3) $(RUNTEST) $(NAME)-Regular.$(EXT) $(@D)/$*.txt $(@D)/$*.shp $(@D)/$*.run

$(TESTDIR)/%.lnt: $(SRCDIR)/%.sfdir $(SFDLINT)
	@echo "   LNT	$<"
	@$(PY) $(SFDLINT) $< $@

$(DOCDIR)/$(NAME)-Table.pdf: $(NAME)-Regular.$(EXT)
	@echo "   GEN	$@"
	@mkdir -p $(DOCDIR)
	@fntsample --font-file $< --output-file $@.tmp --print-outline > $@.txt
	@pdfoutline $@.tmp $@.txt $@.comp
	@mutool clean -d -i -f -a $@.comp $@
	@rm -f $@.tmp $@.comp $@.txt

dist:
	@make -B ttx=true crunch=false
	@mkdir -p $(NAME)-$(VERSION)
	@cp $(OTF) $(PDF) $(NAME)-$(VERSION)
	@cp OFL.txt $(NAME)-$(VERSION)
	@markdown README.md | w3m -dump -T text/html | sed -e "/^Sample$$/d" > $(NAME)-$(VERSION)/README.txt
	@zip -r $(NAME)-$(VERSION).zip $(NAME)-$(VERSION)

clean:
	@rm -rf $(OTF) $(PDF) $(NAME)-$(VERSION) $(NAME)-$(VERSION).zip
