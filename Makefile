NAME=arefruqaa
VERSION=000.002

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

arefruqaa-%.ttf: $(SRC)/arefruqaa-%.sfdir $(SRC)/eulertext-%.sfdir Makefile $(BUILD)
	@echo "   FF	$@"
	@$(PY) $(BUILD) $(VERSION) $@ $+

$(DOC)/$(NAME)-table.pdf: $(NAME)-regular.ttf
	@echo "   GEN	$@"
	@mkdir -p $(DOC)
	@fntsample --font-file $< --output-file $@.tmp --print-outline > $@.txt
	@pdfoutline $@.tmp $@.txt $@.comp
	@pdftk $@.comp output $@ uncompress
	@rm -f $@.tmp $@.comp $@.txt

ttx: $(TTF)
	@$(foreach ttf, $(TTF), \
	     echo "   TTX	"$(ttf); \
	     ttx -q -o temp.ttx $(ttf) && ttx -q -o $(ttf) temp.ttx; \
	 )
	@rm -f temp.ttx

crunch: $(TTF)
	@$(foreach ttf, $(TTF), \
	     echo "   FC	"$(ttf); \
	     font-crunch -q -j8 $(ttf); \
	 )

clean:
	@rm -rf $(TTF) $(PDF)
