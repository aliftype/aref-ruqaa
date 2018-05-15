import sys

def parse(fea):
    subs = {}
    baseGlyphs = None
    for statement in fea.statements:
        if getattr(statement, "name", None) in ("isol", "ccmp"):
            for substatement in statement.statements:
                if hasattr(substatement, "glyphs"):
                    # Single
                    originals = substatement.glyphs[0].glyphSet()
                    replacements = substatement.replacements[0].glyphSet()
                    subs.update(dict(zip(originals, replacements)))
                elif hasattr(substatement, "glyph"):
                    # Multiple
                    subs[substatement.glyph] = substatement.replacement
        elif getattr(statement, "name", None) == "GDEF":
            for substatement in statement.statements:
                if hasattr(substatement, "baseGlyphs"):
                    baseGlyphs = substatement.baseGlyphs
                    if hasattr(baseGlyphs, "glyphclass"):
                        baseGlyphs = baseGlyphs.glyphclass

    return subs, baseGlyphs

def build(font, features):
    subs, baseGlyphs = parse(features)

    temp_glyph = font.createChar(-1, "TempXXX")

    for base in subs:
        names = subs[base]
        glyph = font.createMappedChar(base)
        # build the composite on a temp glyph to prevent FontForge from using
        # its built-in knowledge about components of some encoded glyphs.
        temp_glyph.clear()
        temp_glyph.addReference(names[0])
        for name in names[1:]:
            temp_glyph.appendAccent(name)
        temp_glyph.build()
        glyph.clear()
        glyph.references = temp_glyph.references
        glyph.useRefsMetrics(names[0])
        glyph.color = 0xff0000
        baseGlyphs.glyphs.append(base)

    font.removeGlyph(temp_glyph)
