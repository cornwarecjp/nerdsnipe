all: test

SOURCES = lib/bool.bfs lib/control.bfs lib/8bit.bfs lib/16bit.bfs lib/32bit.bfs lib/array.bfs prototype.bfs
#SOURCES = prototype.bfs

test: bf.py prototype.bf
	python bf.py prototype.bf

prototype.bfi: $(SOURCES)
	cat $(SOURCES) > prototype.bfi

prototype.bf: compile.py prototype.bfi
	python compile.py prototype.bfi prototype.bf

clean:
	-rm prototype.bf prototype.bfi

