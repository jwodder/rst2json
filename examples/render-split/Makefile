PYTHON = python3
INPUT  = demo.rst
OUTDIR = build

$(OUTDIR) : render-split.py $(INPUT) index.j2 section.j2 styles.css docutils.conf
	rm -rf $(OUTDIR)
	$(PYTHON) render-split.py \
		-f html4 \
		-o $(OUTDIR) \
		-i index.html \
		-s section%02d.html \
		$(INPUT) \
		index.j2 \
		section.j2
	cp styles.css $(OUTDIR)

clean :
	rm -rf $(OUTDIR)
