#!/bin/sh
mkdir -p static/books
FILECOUNT="$(ls -la static/books/ | wc -l)"
if [ "$FILECOUNT" -lt 5 ]; then
    wget -O - https://www.gutenberg.org/browse/scores/top | sed -n 's/.*href="\/ebooks\/\([^"]*\).*/\1/p' | head -100 | tail -96 | awk '{print "https://www.gutenberg.org/files/"$1"/"$1"-0.txt"}' | wget -w 1 -P static/books/ -i -
fi
exit 0