PYTHON = python3
BASENAME = demo
OUTDIR = build

$(OUTDIR) : render-split.py $(BASENAME).json index.j2 section.j2 styles.css
	rm -rf $(OUTDIR)
	$(PYTHON) render-split.py \
		-o $(OUTDIR) \
		-i index.html \
		-s section%02d.html \
		$(BASENAME).json \
		index.j2 \
		section.j2
	cp styles.css $(OUTDIR)

$(BASENAME).json : $(BASENAME).rst docutils.conf
	rst2json --format=html4 --split-section-level=1 $< $@

clean :
	rm -rf $(BASENAME).json $(OUTDIR)
