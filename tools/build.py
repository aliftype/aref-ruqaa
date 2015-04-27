import sys
try:
    from sortsmill import ffcompat as fontforge
except ImportError:
    import fontforge

arabic = fontforge.open(sys.argv[1])
arabic.em = 1000

latin = fontforge.open(sys.argv[1].replace("arefruqaa", "eulertext"))

arabic.mergeFonts(latin)

arabic.version = sys.argv[3]
arabic.copyright += " Portions " + latin.copyright[0].lower() + latin.copyright[1:]
arabic.generate(sys.argv[2], flags=("round", "opentype"))
