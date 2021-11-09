NAME=ArefRuqaa
VERSION=1.003
LATIN=EulerText

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

$(BLDDIR)/$(LATIN)-%.ttf: $(LATIN).glyphs
	echo "   BUILD  $(@F)"
	mkdir -p $(BLDDIR)
	$(PY) -m fontmake --verbose WARNING --flatten-components --no-production-names -g $< -i ".* $*" -o ttf --output-path $@ --master-dir="{tmp}" --instance-dir="{tmp}"

$(BLDDIR)/$(NAME).glyphs: $(NAME).glyphs
	echo "   PREPARE  $(@F)"
	$(PY) prepare.py --version=$(VERSION) --out-file=$@ $<

$(BLDDIR)/$(NAME)-%.ttf: $(BLDDIR)/$(NAME).glyphs
	echo "   BUILD  $(@F)"
	mkdir -p $(BLDDIR)
	$(PY) -m fontmake --verbose WARNING --flatten-components --no-production-names -g $< -i ".* $*" -o ttf --output-path $@ --master-dir="{tmp}" --instance-dir="{tmp}"

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
