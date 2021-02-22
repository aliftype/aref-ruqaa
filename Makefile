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

PY := python

FONTS=Regular Bold

SFD=$(FONTS:%=$(SRCDIR)/$(NAME)-%.sfdir)
OTF=$(FONTS:%=$(NAME)-%.$(EXT))

MAKEFLAGS := -r -s

export SOURCE_DATE_EPOCH := 0

.PRECIOUS: $(BLDDIR)/$(LATIN)-%.$(EXT) $(BLDDIR)/$(NAME)-%.$(EXT)

all: $(EXT)

$(EXT): $(OTF)

$(BLDDIR)/$(LATIN)-%.$(EXT): $(SRCDIR)/$(LATIN)-%.ufo
	echo "   FM     $(@F)"
	mkdir -p $(BLDDIR)
	$(PY) -m fontmake --verbose WARNING -u $< -o $(EXT) --output-path $@

$(BLDDIR)/$(NAME)-%.$(EXT): $(SRCDIR)/$(NAME)-%.sfdir $(SRCDIR)/$(NAME).fea
	echo "   FF     $(@F)"
	mkdir -p $(BLDDIR)
	$(PY) build.py --version=$(VERSION) --out-file=$@ --feature-file=$(word 2,$+) $<

$(NAME)-%.$(EXT): $(BLDDIR)/$(NAME)-%.$(EXT) $(BLDDIR)/$(LATIN)-%.$(EXT)
	echo "   MERGE  $@"
	$(PY) merge.py --out-file=$@ $+

dist:
	mkdir -p $(NAME)-$(VERSION)
	cp $(OTF) $(NAME)-$(VERSION)
	cp OFL.txt $(NAME)-$(VERSION)
	sed -e "/^!\[Sample\].*./d" README.md > $(NAME)-$(VERSION)/README.txt
	zip -r $(NAME)-$(VERSION).zip $(NAME)-$(VERSION)

clean:
	rm -rf $(BLDDIR) $(OTF) $(NAME)-$(VERSION) $(NAME)-$(VERSION).zip
