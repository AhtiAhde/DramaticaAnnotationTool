#!/bin/sh
tr -c '[:alnum:]' '[\n*]' < $1 | fgrep -v -w -i -f admin_tools/stopwords.txt | sort | uniq -c | sort -nr | grep -oP "\w*[A-Z]+\w*" | head  -20
