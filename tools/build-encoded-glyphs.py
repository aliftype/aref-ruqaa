from sortsmill import ffcompat as fontforge
import sys
import string

font = fontforge.open(sys.argv[1])
with open(sys.argv[2]) as feature_file:
    features = string.Template(feature_file.read())
    font.mergeFeatureString(features.substitute(GPOS=""))

isol_subtable = None
for lookup in font.gsub_lookups:
    for feature, script in font.getLookupInfo(lookup)[2]:
        if feature == "isol":
            isol_subtable = font.getLookupSubtables(lookup)
            break

assert len(isol_subtable) == 1
isol_subtable = isol_subtable[0]

subs = {}
for glyph in font.glyphs():
    if glyph.unicode > 0:
        sub = glyph.getPosSub(isol_subtable)
        if sub:
            subs[glyph.glyphname] = sub

font.close()
font = fontforge.open(sys.argv[1])

temp_glyph = font.createChar(-1, "TempXXX")

for glyph in font.glyphs():
    if glyph.glyphname in subs:
        sub = subs[glyph.glyphname]
        assert len(sub) == 1
        sub = sub[0]
        assert sub[1] == "MultSubs"
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
font.removeGlyph(temp_glyph)
font.save()
