# Copyright (c) 2020-2025 Khaled Hosny
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

NAME = ArefRuqaa
LATIN = EulerText

SHELL = bash
MAKEFLAGS := -sr
PYTHON := venv/bin/python3

SOURCEDIR = sources
FONTDIR = fonts
BUILDDIR = build
SCRIPTDIR = scripts
INSTANCEDIR = ${BUILDDIR}/instance_ufos

FONTS = Regular Bold
SVG = FontSample.svg

TTF=${FONTS:%=${FONTDIR}/${NAME}-%.ttf} ${FONTS:%=${FONTDIR}/${NAME}Ink-%.ttf}

export SOURCE_DATE_EPOCH ?= 0

TAG = $(shell git describe --tags --abbrev=0)
VERSION = ${TAG:v%=%}
DIST = ${NAME}-${VERSION}


.SECONDARY:
.ONESHELL:
.PHONY: all clean dist ttf test doc ${HTML}

all: ttf doc
ttf: ${TTF}
doc: ${SVG}

FM_OPTS = --verbose WARNING \
	  --flatten-components \
	  --no-production-names

${BUILDDIR}/${NAME}.designspace: ${SOURCEDIR}/${NAME}.glyphspackage
	$(info   UFO    ${@F})
	mkdir -p ${BUILDDIR}
	glyphs2ufo $< -m ${BUILDDIR} -n "$(PWD)"/${INSTANCEDIR} \
		   --generate-GDEF \
		   --write-public-skip-export-glyphs \
		   --no-store-editor-state \
		   --no-preserve-glyphsapp-metadata \
		   --minimal

${BUILDDIR}/${LATIN}-%: ${SOURCEDIR}/${LATIN}.glyphs
	$(info   BUILD  ${@F})
	mkdir -p ${BUILDDIR}
	${PYTHON} -m fontmake $< \
			      --output-path=$@ \
			      --output=ttf \
			      --verbose=WARNING \
			      --flatten-components \
			      --no-production-names \
			      --master-dir="{tmp}" \
			      --instance-dir="{tmp}" \
			      -i ".* $(basename $*)"

${BUILDDIR}/${NAME}-%: ${BUILDDIR}/${NAME}.designspace
	$(info   BUILD  ${@F})
	mkdir -p ${BUILDDIR}
	${PYTHON} -m fontmake ${BUILDDIR}/$(basename ${@F}).ufo \
			      --output-path=$@ \
			      --output=ttf \
			      --verbose=WARNING \
			      --flatten-components \
			      --no-production-names \
			      --filter ... \
			      --filter "alifTools.filters::FontVersionFilter(fontVersion=${VERSION})"

${FONTDIR}/${NAME}-%: ${BUILDDIR}/${NAME}-% ${BUILDDIR}/${LATIN}-%
	$(info   MERGE  ${@F})
	${PYTHON} ${SCRIPTDIR}/merge.py --out-file=$@ $+

${FONTDIR}/${NAME}Ink-%: ${BUILDDIR}/${NAME}-% ${BUILDDIR}/${LATIN}-%
	$(info   MERGE  ${@F})
	${PYTHON} ${SCRIPTDIR}/merge.py --color --family="Aref Ruqaa" --suffix=Ink --out-file=$@ $+

${SVG}: ${TTF}
	$(info   SVG    ${@F})
	${PYTHON} -m alifTools.sample $+ \
				      --text="﴿الحُبُّ سَمَاءٌ لَا تُمطرُ غَيرَ الأَحلَامِ﴾" \
				      --foreground=1F2328 \
				      --dark-foreground=D1D7E0 \
				      -o $@


dist: ${TTF}
	$(info   DIST   ${DIST}.zip)
	install -Dm644 -t ${DIST} ${TTF}
	install -Dm644 -t ${DIST} README.md
	install -Dm644 -t ${DIST} OFL.txt
	zip -rq ${DIST}.zip ${DIST}

clean:
	rm -rf ${BUILDDIR} ${TTF} ${SVG} ${DIST} ${DIST}.zip
