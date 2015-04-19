import sys
try:
    from sortsmill import ffcompat as fontforge
except ImportError:
    import fontforge

arabic = fontforge.open(sys.argv[1])

latin = fontforge.open(sys.argv[1].replace("arefruqaa", "eulertext"))
latin.em = 2048

arabic.mergeFonts(latin)

arabic.version = sys.argv[3]
arabic.generate(sys.argv[2], flags=("round", "opentype"))
