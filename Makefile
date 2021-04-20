NAME=ArefRuqaa
VERSION=1.003
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

$(BLDDIR)/$(LATIN)-%.ttf: $(SRCDIR)/$(LATIN).glyphs
	echo "   BUILD  $(@F)"
	mkdir -p $(BLDDIR)
	$(PY) -m fontmake --verbose WARNING --flatten-components -g $< -i ".* $*" -o ttf --output-path $@ --master-dir="{tmp}" --instance-dir="{tmp}"

$(BLDDIR)/$(NAME)-%.ttf: $(SRCDIR)/$(NAME).glyphs
	echo "   BUILD  $(@F)"
	mkdir -p $(BLDDIR)
	$(PY) build.py --version=$(VERSION) --master=$* --out-file=$@ $<

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
