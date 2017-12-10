all: test

SOURCES = lib/bool.bfs lib/control.bfs lib/8bit.bfs lib/16bit.bfs lib/32bit.bfs lib/array.bfs prototype.bfs
#SOURCES = prototype.bfs

test: test.py bf.py prototype.bf
	python test.py python bf.py prototype.bf

test-compile: test.py bf.py prototype
	python test.py ./prototype

prototype.bfi: $(SOURCES)
	cat $(SOURCES) > prototype.bfi

prototype.bf: compile.py prototype.bfi
	python compile.py prototype.bfi prototype.bf

prototype.c: bf.py prototype.bf
	python bf.py --compile prototype.bf prototype.c

prototype: prototype.c
	gcc -O0 -o prototype prototype.c

clean:
	-rm prototype.bf prototype.bfi

