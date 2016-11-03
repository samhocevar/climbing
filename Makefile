
HTML = s.html jo.html jy.html

all: $(HTML)

clean:
	rm -f $(HTML)

%.html: %.txt
	./misc/conv.py < $^ > $@

SUFFIXES = .html

