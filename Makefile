SHELL := /bin/bash

all: mkdir markdown_files toc_postprocess copy_cname copy_resources copy_images calendar sitemap htmls

mkdir:
	mkdir -p docs
	mkdir -p docs/Ordinarium
	mkdir -p docs/Proprium

markdown_files:
	rm -rf markdown
	cp missaal-eo/missaal-eo.markdown .
	python3 mdsplit.py -l 2 -t -o markdown missaal-eo.markdown
	cp index.md markdown
	rm -f markdown/missaal-eo.markdown

toc_postprocess:
	sed -i 's/\[Proprium\](.*)/Proprium/g' markdown/toc.md
	sed -i 's/\[Ordinarium\](.*)/Ordinarium/g' markdown/toc.md
	sed -i 's/Table of Contents/Inhoudstafel/g' markdown/toc.md
	sed -i '/missaal-eo.markdown/d' markdown/toc.md

copy_resources:
	cp -r resources docs

copy_images:
	cp -r missaal-eo/images docs/Proprium

copy_cname:
	cp CNAME docs

sitemap:
	./sitemap.sh
	cp sitemap.xml robots.txt docs

docs/%.html: markdown/%.md
	pandoc -s \
	  -c resources/tufte.css \
	  -c resources/mc.css \
	  --template=template.html \
	  --filter=./md_to_html_link.py\
	  -f markdown \
	  -t html5 \
	  -o $@ $<

htmls: $(patsubst markdown/%.md,docs/%.html,$(wildcard markdown/*.md) $(wildcard markdown/Ordinarium/*.md) $(wildcard markdown/Proprium/*.md)) 

calendar:
	java net.sf.saxon.Transform -s:calendar-eo.xml -xsl:calendar-redirects.xslt -o:dummy.xml
	rm -f dummy.xml

clean: 
	rm -rf markdown
	rm -rf docs
	rm missaal-eo.markdown
