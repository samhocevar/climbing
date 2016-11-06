
HTML = s.html jo.html jy.html

CONV = ./misc/conv.py

all: $(HTML) extra

clean:
	rm -f $(HTML)

extra:
	cat s.html | sed \
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
	> ../climbing.html
	cat $(HTML:%.html=%.txt) | $(CONV) > all.html

%.html: %.txt
	$(CONV) < $^ > $@

SUFFIXES = .html

