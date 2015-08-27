NAME=arefruqaa
VERSION=000.002

SRC=sources
DOC=documentation
TOOLS=tools
DIST=$(NAME)-$(VERSION)

PY=python2.7
BUILD=$(TOOLS)/build.py
COMPOSE=$(TOOLS)/build-encoded-glyphs.py

FONTS=regular bold

SFD=$(FONTS:%=$(SRC)/$(NAME)-%.sfdir)
TTF=$(FONTS:%=$(NAME)-%.ttf)
PDF=$(DOC)/$(NAME)-table.pdf

ttx?=t
crunch?=

all: ttf doc

ttf: $(TTF)
doc: $(PDF)

arefruqaa-%.ttf: $(SRC)/arefruqaa-%.sfdir $(SRC)/eulertext-%.sfdir Makefile $(BUILD)
	@echo "   FF	$@"
	@$(PY) $(BUILD) $(VERSION) $@ $+
ifdef ttx
	@echo "   TTX	$@"
	@ttx -q -o temp.ttx $@
	@ttx -q -o $@ temp.ttx
	@rm -f temp.ttx
endif
ifdef crunch
	@echo "   FC	$@"
	@font-crunch -q -j8 -o $@.tmp $@
	@mv $@.tmp $@
endif



$(DOC)/$(NAME)-table.pdf: $(NAME)-regular.ttf
	@echo "   GEN	$@"
	@mkdir -p $(DOC)
	@fntsample --font-file $< --output-file $@.tmp --print-outline > $@.txt
	@pdfoutline $@.tmp $@.txt $@.comp
	@pdftk $@.comp output $@ uncompress
	@rm -f $@.tmp $@.comp $@.txt

build-encoded-glyphs: $(SFD)
	@$(foreach sfd, $(SFD), \
	     echo "   CMP	"`basename $(sfd)`; \
	     $(PY) $(COMPOSE) $(sfd); \
	  )

clean:
	@rm -rf $(TTF) $(PDF)
