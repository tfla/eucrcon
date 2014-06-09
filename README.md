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

Using unoconv (https://github.com/dagwieers/unoconv) and pdf2odt (https://github.com/gutschke/pdf2odt) we can convert .doc, .doxc and .pdf to .odt, a format we handle with reasonable accuracy. The conversion is done without dependencies on online services or brittle code.

Useful links:
-------------------
http://www.linuxjournal.com/article/9347
