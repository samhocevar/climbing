
SRC = db.txt

HTML = generated/index.html

SED = sed -b
CONV = PYTHONIOENCODING="UTF-8-sig" ./src/conv.py

all: $(HTML)

clean:
	rm -f $(HTML)

generated/index.html: $(SRC)
	(cat $^ /dev/null; \
	 sed 's/[^#]*/Zz & OK en tête/' routes.txt; \
	 sed 's/^[A-Za-z][^ ]*/Zz/; s/\(--\|OK\).*/OK en tête/' $^ /dev/null) | $(CONV) > $@

