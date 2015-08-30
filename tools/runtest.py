#!/usr/bin/env python3

import sys

from gi.repository import HarfBuzz
from gi.repository import GLib

from fontTools.ttLib import TTFont

HbFonts = {}
def getHbFont(fontname):
    if fontname not in HbFonts:
        font = open(fontname, "rb")
        data = font.read()
        font.close()
        blob = HarfBuzz.glib_blob_create(GLib.Bytes.new(data))
        face = HarfBuzz.face_create(blob, 0)
        font = HarfBuzz.font_create(face)
        upem = HarfBuzz.face_get_upem(face)
        HarfBuzz.font_set_scale(font, upem, upem)
        HarfBuzz.ot_font_set_funcs(font)

        HbFonts[fontname] = font

    return HbFonts[fontname]

TtFonts = {}
def getTtFont(fontname):
    if fontname not in TtFonts:
        font = TTFont(fontname)
        TtFonts[fontname] = font

    return TtFonts[fontname]

def runHB(text, fontname):
    font = getHbFont(fontname)
    buf = HarfBuzz.buffer_create()
    HarfBuzz.buffer_add_utf8(buf, text.encode('utf-8'), 0, -1)
    if text.isdigit():
        HarfBuzz.buffer_set_direction(buf, HarfBuzz.direction_t.LTR)
    else:
        HarfBuzz.buffer_set_direction(buf, HarfBuzz.direction_t.RTL)
    HarfBuzz.buffer_set_script(buf, HarfBuzz.script_t.ARABIC)
    HarfBuzz.buffer_set_language(buf, HarfBuzz.language_from_string(b"ar"))

    HarfBuzz.shape(font, buf, [])

    info = HarfBuzz.buffer_get_glyph_infos(buf)
    ttfont = getTtFont(fontname)
    out = "|".join([ttfont.getGlyphName(i.codepoint) for i in info])

    return "[%s]" % out

def runTest(tests, refs, fontname):
    failed = {}
    passed = []
    for i, (text, ref) in enumerate(zip(tests, refs)):
        result = runHB(text, fontname)
        if ref == result:
            passed.append(i + 1)
        else:
            failed[i + 1] = (text, ref, result)

    return passed, failed

if __name__ == '__main__':
    fontname = sys.argv[1]

    with open(sys.argv[2]) as test:
        tests = test.read().splitlines()

    with open(sys.argv[3]) as ref:
        refs = ref.read().splitlines()

    passed, failed = runTest(tests, refs, fontname)
    message = "%d passed, %d failed" % (len(passed), len(failed))

    with open(sys.argv[4], "w") as result:
        result.write(message + "\n")

    if failed:
        for failure in failed:
            print(failure)
            print("string:   \t", failed[failure][0])
            print("reference:\t", failed[failure][1])
            print("result:   \t", failed[failure][2])
        print(message)
        sys.exit(1)

    sys.exit(0)
