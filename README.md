eucrcon
======

eucrcon is a set of scripts used to analyze the EU Commision
Consultation on Copyright Reform.

They can currently:
* download the zip files
* make some category and extension statistics
* parse ODT files and save the results in a sqlite database
* print answer statistics by question

Recommended execution:
```
# python3 download_files.py
# python3 analyze.py stats input/*.zip
# python3 analyze.py analyze input/*.zip
# sh print_answer_statistics.sh > answer_statistics.txt
# less answer_statistics.txt
```

Using unoconv (https://github.com/dagwieers/unoconv) and pdf2odt (https://github.com/gutschke/pdf2odt) we can convert .doc, .docx and .pdf to .odt, a format we handle with reasonable accuracy. The conversion is done without dependencies on online services or brittle code.

``` xmllint --format file.xml > output.xml ``` gives an indented, readable xml-file instead of an obfuscated oneliner for manual debugging.

Useful links:
-------------------
http://www.linuxjournal.com/article/9347
