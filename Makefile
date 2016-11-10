
SRC = db.txt
NAMES = jo jy s

HTML = $(NAMES:%=generated/%.html)

# Test crap
HTML += $(NAMES:%=generated/%.en.html)
HTML += generated/all.html

SED = sed -b
CONV = PYTHONIOENCODING="UTF-8-sig" ./src/conv.py

all: $(HTML)

clean:
	rm -f $(HTML)

generated/%.en.html: $(SRC)
	cat $^ /dev/null | $(CONV) --name $* --english > $@

generated/%.html: $(SRC)
	cat $^ /dev/null | $(CONV) --name $* > $@

generated/all.html: $(SRC)
	cat $^ /dev/null | $(CONV) > $@

