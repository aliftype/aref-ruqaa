NAME=arefruqaa
VERSION=0.5
EXT=ttf
LATIN=eulertext

SRCDIR=sources
DOCDIR=documentation
TOOLDIR=tools
TESTDIR=tests
DIST=$(NAME)-$(VERSION)

PY=python2
PY3=python3
BUILD=$(TOOLDIR)/build.py
COMPOSE=$(TOOLDIR)/build-encoded-glyphs.py
RUNTEST=$(TOOLDIR)/runtest.py
SFDLINT=$(TOOLDIR)/sfdlint.py

FONTS=regular bold
TESTS=wb yeh-ragaa

SFD=$(FONTS:%=$(SRCDIR)/$(NAME)-%.sfdir)
OTF=$(FONTS:%=$(NAME)-%.$(EXT))
PDF=$(DOCDIR)/$(NAME)-table.pdf

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

$(NAME)-%.$(EXT): $(SRCDIR)/$(NAME)-%.sfdir $(SRCDIR)/$(LATIN)-%.sfdir $(SRCDIR)/$(NAME).fea Makefile $(BUILD)
	@echo "   FF	$@"
	@FILES=($+); $(PY) $(BUILD) --version=$(VERSION) --out-file=$@ --feature-file=$${FILES[2]} $${FILES[0]} $${FILES[1]}
ifeq ($(ttx), true)
	@echo "   TTX	$@"
	@pyftsubset $@ --output-file=$@ --unicodes='*' --layout-features='*' --name-IDs='*'
endif
ifeq ($(crunch), true)
	@echo "   FC	$@"
	@font-crunch -q -j8 -o $@ $@
endif

$(TESTDIR)/%.run: $(TESTDIR)/%.txt $(TESTDIR)/%.shp $(NAME)-regular.$(EXT)
	@echo "   TST	$*"
	@$(PY3) $(RUNTEST) $(NAME)-regular.$(EXT) $(@D)/$*.txt $(@D)/$*.shp $(@D)/$*.run

$(TESTDIR)/%.lnt: $(SRCDIR)/%.sfdir $(SFDLINT)
	@echo "   LNT	$<"
	@$(PY) $(SFDLINT) $< $@

$(DOCDIR)/$(NAME)-table.pdf: $(NAME)-regular.$(EXT)
	@echo "   GEN	$@"
	@mkdir -p $(DOCDIR)
	@fntsample --font-file $< --output-file $@.tmp --print-outline > $@.txt
	@pdfoutline $@.tmp $@.txt $@.comp
	@pdftk $@.comp output $@ uncompress
	@rm -f $@.tmp $@.comp $@.txt

build-encoded-glyphs: $(SFD) $(SRCDIR)/$(NAME).fea
	@$(foreach sfd, $(SFD), \
	     echo "   CMP	"`basename $(sfd)`; \
	     $(PY) $(COMPOSE) $(sfd) $(SRCDIR)/$(NAME).fea; \
	  )

dist:
	@make -B ttx=true crunch=false
	@mkdir -p $(NAME)-$(VERSION)
	@cp $(OTF) $(PDF) $(NAME)-$(VERSION)
	@cp OFL.txt $(NAME)-$(VERSION)
	@markdown README.md | w3m -dump -T text/html | sed -e "/^Sample$$/d" > $(NAME)-$(VERSION)/README.txt
	@zip -r $(NAME)-$(VERSION).zip $(NAME)-$(VERSION)

clean:
	@rm -rf $(OTF) $(PDF) $(NAME)-$(VERSION) $(NAME)-$(VERSION).zip
