#!/bin/bash
for x in `seq 80`
do
    echo
    echo "== QUESTION $x =="
    sqlite3 -header -column responses.sqlite "SELECT count(*) AS count, choice FROM answers WHERE question=$x GROUP BY choice ORDER BY count DESC;"
done
