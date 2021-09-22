#!/bin/sh
tr -c '[:alnum:]' '[\n*]' < $1 | fgrep -v -w -i -f stopwords.txt | sort | uniq -c | sort -nr | head  -100 | grep -oP "\w*[A-Z]+\w*"
