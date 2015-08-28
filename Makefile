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

ttx?=true
crunch?=false

all: ttf doc

ttf: $(TTF)
doc: $(PDF)

arefruqaa-%.ttf: $(SRC)/arefruqaa-%.sfdir $(SRC)/eulertext-%.sfdir Makefile $(BUILD)
	@echo "   FF	$@"
	@$(PY) $(BUILD) $(VERSION) $@ $+
ifeq ($(ttx), true)
	@echo "   TTX	$@"
	@ttx -q -o temp.ttx $@
	@ttx -q -o $@ temp.ttx
	@rm -f temp.ttx
endif
ifeq ($(crunch), true)
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

dist:
	@make ttx=true chrunch=false
	@mkdir -p $(NAME)-$(VERSION)
	@cp $(TTF) $(PDF) $(NAME)-$(VERSION)
	@markdown README.md | w3m -dump -T text/html > $(NAME)-$(VERSION)/README.txt
	@zip -r $(NAME)-$(VERSION).zip $(NAME)-$(VERSION)

clean:
	@rm -rf $(TTF) $(PDF) $(NAME)-$(VERSION) $(NAME)-$(VERSION).zip
