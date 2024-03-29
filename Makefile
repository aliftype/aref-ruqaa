NAME=ArefRuqaa
LATIN=EulerText

FONTDIR=fonts
BUILDDIR=build
SOURCEDIR=sources
SCRIPTDIR=scripts
INSTANCEDIR=$(BUILDDIR)/instance_ufos
DIST=$(NAME)-$(VERSION)

PY := python3

FONTS=Regular Bold

TTF=$(FONTS:%=$(FONTDIR)/$(NAME)-%.ttf) $(FONTS:%=$(FONTDIR)/$(NAME)Ink-%.ttf)
SAMPLE=sample.svg

TAG=$(shell git describe --tags --abbrev=0)
VERSION=$(TAG:v%=%)

MAKEFLAGS := -r -s

export SOURCE_DATE_EPOCH := 0
export FONTTOOLS_LOOKUP_DEBUGGING := 1

.SECONDARY:

all: ttf doc
ttf: $(TTF)
doc: $(SAMPLE)

FM_OPTS = --verbose WARNING \
	  --flatten-components \
	  --no-production-names

FM_OPTS2 = $(FM_OPTS) \
	  --master-dir="{tmp}" \
	  --instance-dir="{tmp}"

$(BUILDDIR)/$(NAME).glyphspackage: $(SOURCEDIR)/$(NAME).glyphspackage
	echo "   PREPARE  $(@F)"
	mkdir -p $(BUILDDIR)
	$(PY) $(SCRIPTDIR)/setversion.py $< $@ $(VERSION)

$(BUILDDIR)/$(NAME).designspace: $(BUILDDIR)/$(NAME).glyphspackage
	echo "   UFO      $(@F)"
	mkdir -p $(BUILDDIR)
	glyphs2ufo $< -m $(BUILDDIR) -n "$(PWD)"/$(INSTANCEDIR) \
		   --generate-GDEF \
		   --write-public-skip-export-glyphs \
		   --no-store-editor-state \
		   --no-preserve-glyphsapp-metadata \
		   --minimal

$(BUILDDIR)/$(LATIN)-%: $(SOURCEDIR)/$(LATIN).glyphs
	echo "   BUILD    $(@F)"
	mkdir -p $(BUILDDIR)
	$(PY) -m fontmake $(FM_OPTS2) -g $< -i ".* $(basename $*)" -o $(subst .,,$(suffix $(@F))) --output-path $@

$(BUILDDIR)/$(NAME)-%: $(BUILDDIR)/$(NAME).designspace
	echo "   BUILD    $(@F)"
	mkdir -p $(BUILDDIR)
	$(PY) -m fontmake $(FM_OPTS) $(BUILDDIR)/$(basename $(@F)).ufo -o $(subst .,,$(suffix $(@F))) --output-path $@

$(FONTDIR)/$(NAME)-%: $(BUILDDIR)/$(NAME)-% $(BUILDDIR)/$(LATIN)-%
	echo "   MERGE    $(@F)"
	$(PY) $(SCRIPTDIR)/merge.py --out-file=$@ $+

$(FONTDIR)/$(NAME)Ink-%: $(BUILDDIR)/$(NAME)-% $(BUILDDIR)/$(LATIN)-%
	echo "   MERGE    $(@F)"
	$(PY) $(SCRIPTDIR)/merge.py --color --family="Aref Ruqaa" --suffix=Ink --out-file=$@ $+

$(SAMPLE): $(TTF)
	echo "   SAMPLE   $(@F)"
	python3 $(SCRIPTDIR)/mksample.py $+ \
	  --output=$@ \
	  --text="﴿الحُبُّ سَمَاءٌ لَا تُمطرُ غَيرَ الأَحلَامِ﴾"


dist: $(TTF)
	install -Dm644 -t $(DIST) $(TTF)
	install -Dm644 -t $(DIST) OFL.txt
	install -Dm644 -t $(DIST) README.md
	zip -r $(DIST).zip $(DIST)

clean:
	rm -rf $(BUILDDIR) $(TTF) $(DIST) $(DIST).zip
