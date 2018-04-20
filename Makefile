all: puzzle.png

puzzle.png: composeImage.py decomposeImage.py cat.jpg amaze.py.gz discs.png qr-output.txt
	python composeImage.py cat.jpg puzzle.png amaze.py.gz discs.png qr-output.txt
	python decomposeImage.py puzzle.png amaze.py.gz

qr-output.txt: makeqr.py qr.txt
	python makeqr.py qr.txt qr-output.txt

amaze.py.gz: amaze.py
	gzip --keep --force amaze.py

clean:
	-rm puzzle.png amaze.py.gz qr-output.txt *.pyc

