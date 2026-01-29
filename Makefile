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
SCRIPTDIR = scripts
FONTDIR = fonts
TESTDIR = tests
BUILDDIR = build
INSTANCEDIR = ${BUILDDIR}/instance_ufos

NAMES = ${NAME}-Regular ${NAME}-Bold ${NAME}Ink-Regular ${NAME}Ink-Bold
FONTS = ${NAMES:%=${FONTDIR}/%.ttf}
SVG = FontSample.svg

GLYPHSFILE = ${SOURCEDIR}/${NAME}.glyphspackage

export SOURCE_DATE_EPOCH ?= $(shell stat -c "%Y" ${GLYPHSFILE})

TAG = $(shell git describe --tags --abbrev=0)
VERSION = ${TAG:v%=%}
DIST = ${NAME}-${VERSION}


.SECONDARY:
.ONESHELL:
.PHONY: all clean dist ttf test doc ${HTML}

all: ttf doc
ttf: ${FONTS}
doc: ${SVG}

FM_OPTS = --verbose WARNING \
	  --flatten-components \
	  --no-production-names

${BUILDDIR}/${NAME}.designspace: ${GLYPHSFILE}
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

${SVG}: ${FONTS}
	$(info   SVG    ${@F})
	${PYTHON} -m alifTools.sample $+ \
				      --text="﴿الحُبُّ سَمَاءٌ لَا تُمطرُ غَيرَ الأَحلَامِ﴾" \
				      --foreground=1F2328 \
				      --dark-foreground=D1D7E0 \
				      -o $@


dist: ${FONTS}
	$(info   DIST   ${DIST}.zip)
	install -Dm644 -t ${DIST} ${FONTS}
	install -Dm644 -t ${DIST} README.md
	install -Dm644 -t ${DIST} OFL.txt
	zip -rq ${DIST}.zip ${DIST}

clean:
	rm -rf ${BUILDDIR} ${FONTS} ${SVG} ${DIST} ${DIST}.zip
