NAME=ArefRuqaa
VERSION=1.003
LATIN=EulerText

BLDDIR=build
DIST=$(NAME)-$(VERSION)

PY := python3

FONTS=Regular Bold

OTF=$(FONTS:%=$(NAME)-%.otf)
TTF=$(FONTS:%=$(NAME)-%.ttf)

MAKEFLAGS := -r -s

export SOURCE_DATE_EPOCH := 0
export FONTTOOLS_LOOKUP_DEBUGGING := 1

.PRECIOUS: $(BLDDIR)/$(LATIN)-%.otf $(BLDDIR)/$(NAME)-%.otf

all: otf
otf: $(OTF)
ttf: $(TTF)

FM_OPTS = --verbose WARNING \
	  --flatten-components \
	  --no-production-names \
	  --master-dir="{tmp}" \
	  --instance-dir="{tmp}"

$(BLDDIR)/$(NAME).glyphs: $(NAME).glyphs
	echo "   PREPARE  $(@F)"
	mkdir -p $(BLDDIR)
	$(PY) setversion.py $< $@ $(VERSION)

$(BLDDIR)/$(LATIN)-%: $(LATIN).glyphs
	echo "   BUILD  $(@F)"
	mkdir -p $(BLDDIR)
	$(PY) -m fontmake $(FM_OPTS) -g $< -i ".* $(basename $*)" -o $(subst .,,$(suffix $(@F))) --output-path $@

$(BLDDIR)/$(NAME)-%: $(BLDDIR)/$(NAME).glyphs
	echo "   BUILD  $(@F)"
	mkdir -p $(BLDDIR)
	$(PY) -m fontmake $(FM_OPTS) -g $< -i ".* $(basename $*)" -o $(subst .,,$(suffix $(@F))) --output-path $@

$(NAME)-%: $(BLDDIR)/$(NAME)-% $(BLDDIR)/$(LATIN)-%
	echo "   MERGE  $@"
	$(PY) merge.py --out-file=$@ $+

dist:
	install -Dm644 -t $(DIST) $(OTF)
	install -Dm644 -t $(DIST)/ttf $(TTF)
	install -Dm644 -t $(DIST) OFL.txt
	install -Dm644 -t $(DIST) README.md
	zip -r $(DIST).zip $(DIST)

clean:
	rm -rf $(BLDDIR) $(OTF) $(NAME)-$(VERSION) $(NAME)-$(VERSION).zip
