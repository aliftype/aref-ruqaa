NAME=ArefRuqaa
VERSION=1.003
LATIN=EulerText

BLDDIR=build
INSTANCEDIR=$(BLDDIR)/instance_ufos
DIST=$(NAME)-$(VERSION)

PY := python3

FONTS=Regular Bold

OTF=$(FONTS:%=$(NAME)-%.otf) $(FONTS:%=$(NAME)Ink-%.otf)
TTF=$(FONTS:%=$(NAME)-%.ttf) $(FONTS:%=$(NAME)Ink-%.ttf)

MAKEFLAGS := -r -s

export SOURCE_DATE_EPOCH := 0
export FONTTOOLS_LOOKUP_DEBUGGING := 1

.SECONDARY:

all: otf
otf: $(OTF)
ttf: $(TTF)

FM_OPTS = --verbose WARNING \
	  --flatten-components \
	  --no-production-names

FM_OPTS2 = $(FM_OPTS) \
	  --master-dir="{tmp}" \
	  --instance-dir="{tmp}"

$(BLDDIR)/$(NAME).glyphs: $(NAME).glyphs
	echo "   PREPARE  $(@F)"
	mkdir -p $(BLDDIR)
	$(PY) setversion.py $< $@ $(VERSION)

$(BLDDIR)/$(NAME).designspace: $(BLDDIR)/$(NAME).glyphs
	echo "   UFO    $(@F)"
	mkdir -p $(BLDDIR)
	glyphs2ufo $< -m $(BLDDIR) -n "$(PWD)"/$(INSTANCEDIR) \
		   --generate-GDEF \
		   --write-public-skip-export-glyphs \
		   --no-store-editor-state \
		   --no-preserve-glyphsapp-metadata \
		   --minimal

$(BLDDIR)/$(LATIN)-%: $(LATIN).glyphs
	echo "   BUILD  $(@F)"
	mkdir -p $(BLDDIR)
	$(PY) -m fontmake $(FM_OPTS2) -g $< -i ".* $(basename $*)" -o $(subst .,,$(suffix $(@F))) --output-path $@

$(BLDDIR)/$(NAME)-%: $(BLDDIR)/$(NAME).designspace
	echo "   BUILD  $(@F)"
	mkdir -p $(BLDDIR)
	$(PY) -m fontmake $(FM_OPTS) $(BLDDIR)/$(basename $(@F)).ufo -o $(subst .,,$(suffix $(@F))) --output-path $@

$(NAME)-%: $(BLDDIR)/$(NAME)-% $(BLDDIR)/$(LATIN)-%
	echo "   MERGE  $@"
	$(PY) merge.py --out-file=$@ $+

$(NAME)Ink-%: $(BLDDIR)/$(NAME)-% $(BLDDIR)/$(LATIN)-%
	echo "   MERGE  $@"
	$(PY) merge.py --color --family="Aref Ruqaa" --suffix=Ink --out-file=$@ $+

dist: $(OTF) $(TTF)
	install -Dm644 -t $(DIST) $(OTF)
	install -Dm644 -t $(DIST)/ttf $(TTF)
	install -Dm644 -t $(DIST) OFL.txt
	install -Dm644 -t $(DIST) README.md
	zip -r $(DIST).zip $(DIST)

clean:
	rm -rf $(BLDDIR) $(OTF) $(TTF) $(DIST) $(DIST).zip
