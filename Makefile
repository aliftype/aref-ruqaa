NAME=arefruqaa
VERSION=000.001

SRC=sources
DOC=documentation
TOOLS=tools
DIST=$(NAME)-$(VERSION)

PY=python2.7
BUILD=$(TOOLS)/build.py

FONTS=regular bold

SFD=$(FONTS:%=$(SRC)/$(NAME)-%.sfdir)
TTF=$(FONTS:%=$(NAME)-%.ttf)
PDF=$(DOC)/$(NAME)-table.pdf

all: ttf doc

ttf: $(TTF)
doc: $(PDF)

%.ttf: $(SRC)/%.sfdir Makefile $(BUILD)
	@echo "   FF	$@"
	@$(PY) $(BUILD) $< $@ $(VERSION)

$(DOC)/$(NAME)-table.pdf: $(NAME)-regular.ttf
	@echo "   GEN	$@"
	@mkdir -p $(DOC)
	@fntsample --font-file $< --output-file $@.tmp --print-outline > $@.txt
	@pdfoutline $@.tmp $@.txt $@
	@rm -f $@.tmp $@.txt

dist: $(TTF)
	@echo "Making dist tarball"
	@mkdir -p $(DIST)/$(SRC)
	@mkdir -p $(DIST)/$(DOC)
	@mkdir -p $(DIST)/$(TOOLS)
	@cp $(SFD) $(DIST)/$(SRC)
	@cp $(PDF) $(DIST)/$(DOC)
	@cp $(TTF) $(DIST)
	@cp $(BUILD) $(DIST)/$(TOOLS)
	@cp Makefile $(DIST)
	@cp README.md $(DIST)/README.txt
	@zip -r $(DIST).zip $(DIST)

clean:
	@rm -rf $(TTF) $(PDF) $(DIST) $(DIST).zip
