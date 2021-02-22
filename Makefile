NAME=ArefRuqaa
VERSION=1.002
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
MERGE=$(TOOLDIR)/merge.py
SFDLINT=$(TOOLDIR)/sfdlint.py

FONTS=Regular Bold

SFD=$(FONTS:%=$(SRCDIR)/$(NAME)-%.sfdir)
OTF=$(FONTS:%=$(NAME)-%.$(EXT))

LNT=$(FONTS:%=$(TESTDIR)/$(NAME)-%.lnt)

MAKEFLAGS := -r -s

export SOURCE_DATE_EPOCH := 0

.PRECIOUS: $(BLDDIR)/$(LATIN)-%.$(EXT) $(BLDDIR)/$(NAME)-%.$(EXT)

all: $(EXT)

$(EXT): $(OTF)
lint: $(LNT)
check: lint

$(BLDDIR)/$(LATIN)-%.$(EXT): $(SRCDIR)/$(LATIN)-%.ufo
	echo "   FM     $(@F)"
	mkdir -p $(BLDDIR)
	$(PY) -m fontmake --verbose WARNING -u $< -o $(EXT) --output-path $@

$(BLDDIR)/$(NAME)-%.$(EXT): $(SRCDIR)/$(NAME)-%.sfdir $(SRCDIR)/$(NAME).fea
	echo "   FF     $(@F)"
	mkdir -p $(BLDDIR)
	$(PY) $(BUILD) --version=$(VERSION) --out-file=$@ --feature-file=$(word 2,$+) $<

$(NAME)-%.$(EXT): $(BLDDIR)/$(NAME)-%.$(EXT) $(BLDDIR)/$(LATIN)-%.$(EXT)
	echo "   MERGE  $@"
	$(PY) $(MERGE) --out-file=$@ $+

$(TESTDIR)/%.lnt: $(SRCDIR)/%.sfdir $(SFDLINT)
	echo "   LNT	$<"
	mkdir -p $(TESTDIR)
	$(PY) $(SFDLINT) $< $@

dist:
	mkdir -p $(NAME)-$(VERSION)
	cp $(OTF) $(NAME)-$(VERSION)
	cp OFL.txt $(NAME)-$(VERSION)
	sed -e "/^!\[Sample\].*./d" README.md > $(NAME)-$(VERSION)/README.txt
	zip -r $(NAME)-$(VERSION).zip $(NAME)-$(VERSION)

clean:
	rm -rf $(BLDDIR) $(OTF) $(NAME)-$(VERSION) $(NAME)-$(VERSION).zip
