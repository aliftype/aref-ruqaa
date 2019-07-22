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

LNT=$(FONTS:%=$(TESTDIR)/$(NAME)-%.lnt)

export SOURCE_DATE_EPOCH ?= 0

.PRECIOUS: $(BLDDIR)/master_otf/$(LATIN)-%.otf

all: otf

otf: $(OTF)
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

dist:
	@make -B
	@mkdir -p $(NAME)-$(VERSION)
	@cp $(OTF) $(NAME)-$(VERSION)
	@cp OFL.txt $(NAME)-$(VERSION)
	@sed -e "/^!\[Sample\].*./d" README.md > $(NAME)-$(VERSION)/README.txt
	@zip -r $(NAME)-$(VERSION).zip $(NAME)-$(VERSION)

clean:
	@rm -rf $(BLDDIR) $(OTF) $(NAME)-$(VERSION) $(NAME)-$(VERSION).zip
