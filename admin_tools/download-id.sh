#!/bin/sh
mkdir -p static/books
wget "https://www.gutenberg.org/ebooks/"$1".txt.utf-8" -P static/books/ -i -
exit 0