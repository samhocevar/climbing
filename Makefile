
SRC = db.txt

HTML = generated/index.html

SED = sed -b
CONV = PYTHONIOENCODING="UTF-8-sig" ./src/conv.py

all: $(HTML)

clean:
	rm -f $(HTML)

generated/index.html: $(SRC)
	(cat $^ /dev/null; sed 's/[^#]*/Xx & OK /' routes.txt) | $(CONV) > $@

