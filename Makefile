NAME=arefruqaa
VERSION=0.2

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

FONTS=regular bold
TESTS=wb yeh-ragaa

SFD=$(FONTS:%=$(SRCDIR)/$(NAME)-%.sfdir)
TTF=$(FONTS:%=$(NAME)-%.ttf)
PDF=$(DOCDIR)/$(NAME)-table.pdf

TST=$(TESTS:%=$(TESTDIR)/%.txt)
SHP=$(TESTS:%=$(TESTDIR)/%.shp)
RUN=$(TESTS:%=$(TESTDIR)/%.run)

ttx?=true
crunch?=false
glyphnames?=true

all: ttf doc

ttf: $(TTF)
doc: $(PDF)
check: $(RUN)

arefruqaa-%.ttf: $(SRCDIR)/arefruqaa-%.sfdir $(SRCDIR)/eulertext-%.sfdir $(SRCDIR)/arefruqaa.fea Makefile $(BUILD)
	@echo "   FF	$@"
ifeq ($(glyphnames), true)
	@FILES=($+); $(PY) $(BUILD) --version=$(VERSION) --out-file=$@ --feature-file=$${FILES[2]} $${FILES[0]} $${FILES[1]}
else
	@FILES=($+); $(PY) $(BUILD) --version=$(VERSION) --out-file=$@ --feature-file=$${FILES[2]} --no-glyphnames $${FILES[0]} $${FILES[1]}
endif
ifeq ($(ttx), true)
	@echo "   TTX	$@"
	@ttx -q -o temp.ttx $@
	@ttx -q -o $@ temp.ttx
	@rm -f temp.ttx
endif
ifeq ($(crunch), true)
	@echo "   FC	$@"
	@font-crunch -q -j8 -o $@.tmp $@
	@mv $@.tmp $@
endif

$(TESTDIR)/%.run: $(TESTDIR)/%.txt $(TESTDIR)/%.shp $(NAME)-regular.ttf
	@echo "   TST	$*"
	@$(PY3) $(RUNTEST) $(NAME)-regular.ttf $(@D)/$*.txt $(@D)/$*.shp $(@D)/$*.run

$(DOCDIR)/$(NAME)-table.pdf: $(NAME)-regular.ttf
	@echo "   GEN	$@"
	@mkdir -p $(DOCDIR)
	@fntsample --font-file $< --output-file $@.tmp --print-outline > $@.txt
	@pdfoutline $@.tmp $@.txt $@.comp
	@pdftk $@.comp output $@ uncompress
	@rm -f $@.tmp $@.comp $@.txt

build-encoded-glyphs: $(SFD)
	@$(foreach sfd, $(SFD), \
	     echo "   CMP	"`basename $(sfd)`; \
	     $(PY) $(COMPOSE) $(sfd); \
	  )

dist:
	@make -B ttx=true chrunch=false glyphnames=false
	@mkdir -p $(NAME)-$(VERSION)
	@cp $(TTF) $(PDF) $(NAME)-$(VERSION)
	@markdown README.md | w3m -dump -T text/html > $(NAME)-$(VERSION)/README.txt
	@zip -r $(NAME)-$(VERSION).zip $(NAME)-$(VERSION)

clean:
	@rm -rf $(TTF) $(PDF) $(NAME)-$(VERSION) $(NAME)-$(VERSION).zip
