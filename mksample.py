import argparse

from blackrenderer.font import BlackRendererFont
from blackrenderer.backends.svg import SVGSurface
from blackrenderer.render import buildGlyphLine, calcGlyphLineBounds
from fontTools.misc.arrayTools import offsetRect, unionRect

import uharfbuzz as hb


def parseFeatures(text):
    if not text:
        return {}
    features = {}
    for feature in text.split(","):
        value = 1
        start = 0
        end = -1
        if feature[0] == "-":
            value = 0
        if feature[0] in ("+", "-"):
            feature = feature[1:]
        tag = feature
        if "[" in feature:
            tag, extra = feature.split("[")
            if "=" in extra:
                extra, value = extra.split("=")
            if extra[-1] == "]":
                extra = extra[:-1]
                start = end = extra
                if ":" in extra:
                    start, end = extra.split(":")
        features[tag] = [[int(value), int(start), int(end)]]
    return features


def makeLine(buf, font, y):
    line = buildGlyphLine(buf.glyph_infos, buf.glyph_positions, font.glyphNames)

    rect = calcGlyphLineBounds(line, font)
    rect = offsetRect(rect, 0, y)

    ascender = font.ttFont["OS/2"].sTypoAscender
    descender = font.ttFont["OS/2"].sTypoDescender
    height = -ascender + descender

    return line, rect, height


def draw(surface, paths, text, features):
    bounds = None
    lines = []
    y = 0
    for path in paths:
        font = BlackRendererFont(path)

        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(font.hbFont, buf, features)

        line, rect, height = makeLine(buf, font, y)
        lines.append((font, line, rect, y))

        if bounds is None:
            bounds = rect
        bounds = unionRect(bounds, rect)
        y += height

    with surface.canvas(bounds) as canvas:
        for font, line, rect, y in lines:
            with canvas.savedState():
                # Center align the line. 
                x = (bounds[2] - rect[2]) / 2
                canvas.translate(x, y)
                for glyph in line:
                    with canvas.savedState():
                        canvas.translate(glyph.xOffset, glyph.yOffset)
                        font.drawGlyph(glyph.name, canvas)
                    canvas.translate(glyph.xAdvance, glyph.yAdvance)


def main(args=None):
    parser = argparse.ArgumentParser(description="Create SVG sample.")
    parser.add_argument("fonts", nargs="+", help="input fonts")
    parser.add_argument("-t", "--text", help="input text", required=True)
    parser.add_argument("-f", "--features", help="input features")
    parser.add_argument("-o", "--output", help="output SVG", required=True)

    options = parser.parse_args(args)

    surface = SVGSurface()
    features = parseFeatures(options.features)
    draw(surface, options.fonts, options.text, features)
    surface.saveImage(options.output)


if __name__ == "__main__":
    import sys

    sys.exit(main())
