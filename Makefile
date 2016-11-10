
SRC = db.txt
NAMES = jo jy s

HTML = $(NAMES:%=generated/%.html)

# Test crap
HTML += $(NAMES:%=generated/%.en.html)
HTML += generated/all.html

SED = sed -b
CONV = PYTHONIOENCODING="UTF-8" ./src/conv.py

all: $(HTML)

clean:
	rm -f $(HTML)

generated/%.en.html: generated/%.html
	cat $^ /dev/null | $(SED) \
	  -e 's/ *<.*a href.*>[ |]*//' \
	  -e 's/beige/beige/g' \
	  -e 's/blanche/white/g' \
	  -e 's/bleue/blue/g' \
	  -e 's/jaune/yellow/g' \
	  -e 's/noire/black/g' \
	  -e 's/orange/orange/g' \
	  -e 's/rose/pink/g' \
	  -e 's/rouge/red/g' \
	  -e 's/saumon/salmon/g' \
	  -e 's/verte/green/g' \
	  -e 's/violette/purple/g' \
	> $@

generated/%.html: $(SRC)
	cat $^ /dev/null | grep -i '^\(#\|$*\)' | $(CONV) > $@

generated/all.html: $(SRC)
	cat $^ /dev/null | $(CONV) > $@

