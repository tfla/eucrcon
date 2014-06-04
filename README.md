eucrcon
======

eucrcon is a script used to analyze the EU Commision Consultation on Copyright Reform.

It currently downloads the zip files and make some category and extension statistics.
Basic ODT file parsing is implemented.
analyze.py can loop through all ODT files in all zip files and call the ODT parser.

Recommended execution:
```
# python3 download_files.py
# python3 analyze.py stats input/*.zip
# python3 analyze.py analyze input/users_en.zip #Doesn't do anything meaningful right now, but takes long time anyway :)
```

Some notes about .docx-xmls:
-----------------------------------------------
In .docx (which is a renamed .zip-file) you'll find document.xml, which contains all the relevant information for us (to our knowledge).

All underscores start with the tag ``` <w:u ```, the tag is then either ended immediately or with exact values. A single (one-row) undeline can look like this: ``` <w:u w:val="single"/> ```.

Formatting (e.g underlines) are persistent within a node. This means that underlines can be defined in sister-nodes to the text-node (which, for the record, looks like this: ``` <w:t ``` with following - non mandatory - configuration values).

Numbered points are labeled ``` <w:numPr> ```

An example of numbering with defined levels and id:
```
<w:numPr><w:ilvl w:val="0"/><w:numId w:val="36"/></w:numPr> 
```

``` xmllint --format file.xml > output.xml <``` gives an indented, readable xml-file instead of an obfuscated oneliner.

.docx is referenced in [http://www.iso.org/iso/home/store/catalogue_tc/catalogue_detail.htm?csnumber=61750](http://www.iso.org/iso/home/store/catalogue_tc/catalogue_detail.htm?csnumber=61750) for more info.

Useful links:
-------------------
http://www.linuxjournal.com/article/9347