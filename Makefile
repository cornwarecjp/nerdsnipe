all: puzzle.png

puzzle.png: composeImage.py cat.jpg amaze.py.gz discs.png qr.txt
	python composeImage.py cat.jpg puzzle.png amaze.py.gz discs.png qr.txt

amaze.py.gz: amaze.py
	gzip --keep --force amaze.py

clean:
	-rm puzzle.png amaze.py.gz

