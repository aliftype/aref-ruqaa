import sys
try:
    from sortsmill import ffcompat as fontforge
except ImportError:
    import fontforge

font = fontforge.open(sys.argv[1])

font.version = sys.argv[3]
font.generate(sys.argv[2], flags=("round", "opentype"))
