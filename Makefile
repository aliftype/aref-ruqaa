NAME=arefruqaa
VERSION=0.2

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
glyphnames?=true

all: ttf doc

ttf: $(TTF)
doc: $(PDF)

arefruqaa-%.ttf: $(SRC)/arefruqaa-%.sfdir $(SRC)/eulertext-%.sfdir $(SRC)/arefruqaa.fea Makefile $(BUILD)
	@echo "   FF	$@"
ifeq ($(glyphnames), true)
	@FILES=($+); $(PY) $(BUILD) --version=$(VERSION) --out-file=$@ --feature-file=$${FILES[2]} $${FILES[0]} $${FILES[1]}
else
	@FILES=($+); $(PY) $(BUILD) --version=$(VERSION) --out-file=$@ --feature-file=$${FILES[2]} --no-glyphnames $${FILES[0]} $${FILES[1]}
endif
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
	@make -B ttx=true chrunch=false glyphnames=false
	@mkdir -p $(NAME)-$(VERSION)
	@cp $(TTF) $(PDF) $(NAME)-$(VERSION)
	@markdown README.md | w3m -dump -T text/html > $(NAME)-$(VERSION)/README.txt
	@zip -r $(NAME)-$(VERSION).zip $(NAME)-$(VERSION)

clean:
	@rm -rf $(TTF) $(PDF) $(NAME)-$(VERSION) $(NAME)-$(VERSION).zip
