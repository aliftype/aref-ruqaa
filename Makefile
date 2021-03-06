NAME=ArefRuqaa
VERSION=1.002
LATIN=EulerText

SRCDIR=sources
BLDDIR=build
DIST=$(NAME)-$(VERSION)

PY := python

FONTS=Regular Bold

OTF=$(FONTS:%=$(NAME)-%.ttf)

MAKEFLAGS := -r -s

export SOURCE_DATE_EPOCH := 0
export FONTTOOLS_LOOKUP_DEBUGGING := 1

.PRECIOUS: $(BLDDIR)/$(LATIN)-%.ttf $(BLDDIR)/$(NAME)-%.ttf

all: $(OTF)

$(BLDDIR)/$(LATIN)-%.ttf: $(SRCDIR)/$(LATIN)-%.ufo
	echo "   BUILD  $(@F)"
	mkdir -p $(BLDDIR)
	$(PY) -m fontmake --verbose WARNING -u $< -o ttf --output-path $@

$(BLDDIR)/$(NAME)-%.ttf: $(SRCDIR)/$(NAME)-%.sfdir $(SRCDIR)/$(NAME).fea
	echo "   BUILD  $(@F)"
	mkdir -p $(BLDDIR)
	$(PY) build.py --version=$(VERSION) --out-file=$@ --feature-file=$(word 2,$+) $<

$(NAME)-%.ttf: $(BLDDIR)/$(NAME)-%.ttf $(BLDDIR)/$(LATIN)-%.ttf
	echo "   MERGE  $@"
	$(PY) merge.py --out-file=$@ $+

dist:
	install -Dm644 -t $(DIST) $(OTF)
	install -Dm644 -t $(DIST) OFL.txt
	install -Dm644 -t $(DIST) README.md
	zip -r $(DIST).zip $(DIST)

clean:
	rm -rf $(BLDDIR) $(OTF) $(NAME)-$(VERSION) $(NAME)-$(VERSION).zip
