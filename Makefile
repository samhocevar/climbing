
SRC = db.txt

HTML = generated/index.html generated/index.en.html

SED = sed -b
CONV = PYTHONIOENCODING="UTF-8-sig" ./src/conv.py

all: $(HTML)

clean:
	rm -f $(HTML)

generated/index.en.html: $(SRC)
	cat $^ /dev/null | $(CONV) --english > $@

generated/index.html: $(SRC)
	cat $^ /dev/null | $(CONV) > $@

