#!/usr/bin/env python3

import sys

import harfbuzz as hb

def getHbFont(fontname):
    with open(fontname, "rb") as fp:
        data = fp.read()
    blob = hb.Blob.create_for_array(data, hb.HARFBUZZ.MEMORY_MODE_READONLY)
    face = hb.Face.create(blob, 0, False)
    font = hb.Font.create(face)
    font.scale = (face.upem, face.upem)
    font.ot_set_funcs()

    return font

def runHB(text, buf, font):
    buf.clear_contents()
    buf.add_str(text)
    buf.direction = hb.HARFBUZZ.DIRECTION_RTL
    buf.script = hb.HARFBUZZ.SCRIPT_ARABIC
    buf.language = hb.Language.from_string("ar")

    hb.shape(font, buf, [])

    info = buf.glyph_infos
    positions = buf.glyph_positions
    out = []
    for i, p in zip(info, positions):
        text = ""
        text += font.get_glyph_name(i.codepoint)
        text += " w=%d" % p.x_advance
        if p.x_offset:
            text += " x=%d" % p.x_offset
        if p.y_offset:
            text += " y=%d" % p.y_offset
        out.append(text)

    return "[%s]" % "|".join(out)

def runTest(tests, refs, fontname):
    failed = {}
    passed = []
    font = getHbFont(fontname)
    buf = hb.Buffer.create()
    for i, (text, ref) in enumerate(zip(tests, refs)):
        result = runHB(text, buf, font)
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

    if not failed:
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
