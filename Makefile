
SRC = s.txt jo.txt jy.txt

HTML = $(SRC:%.txt=generated/%.html)

# Test crap
HTML += $(SRC:%.txt=generated/%.en.html)
HTML += generated/all.html

CONV = ./misc/conv.py

all: $(HTML)

clean:
	rm -f $(HTML)

%.en.html: %.html
	cat $^ /dev/null | sed \
          -e 's/.*a href.*//' \
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

generated/all.html: $(SRC)
	cat $^ /dev/null | $(CONV) > $@

generated/%.html: %.txt
	$(CONV) < $^ > $@

