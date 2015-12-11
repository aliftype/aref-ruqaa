from sortsmill import ffcompat as fontforge
import sys

def build(font):
    subtables = []
    for lookup in font.gsub_lookups:
        for feature, script in font.getLookupInfo(lookup)[2]:
            if feature in ("isol", "ccmp"):
                for subtable in font.getLookupSubtables(lookup):
                    subtables.append(subtable)

    subs = {}
    for glyph in font.glyphs():
        if glyph.unicode > 0:
            for subtable in subtables:
                sub = glyph.getPosSub(subtable)
                if sub:
                    assert glyph.glyphname not in subs
                    subs[glyph.glyphname] = sub

    temp_glyph = font.createChar(-1, "TempXXX")

    for glyph in font.glyphs():
        if glyph.glyphname in subs:
            sub = subs[glyph.glyphname]
            assert len(sub) == 1
            sub = sub[0]
            assert sub[1] in ("MultSubs", "Substitution"), sub[1]
            names = sub[2:]
            # build the composite on a temp glyph to prevent FontForge from
            # using its built-in knowledge about components of some encoded
            # glyphs.
            temp_glyph.clear()
            temp_glyph.addReference(names[0])
            if len(names) > 1:
                for name in names[1:]:
                    temp_glyph.appendAccent(name)
                temp_glyph.build()
            glyph.clear()
            glyph.references = temp_glyph.references
            glyph.useRefsMetrics(names[0])
            glyph.color = 0xff0000
    font.removeGlyph(temp_glyph)
