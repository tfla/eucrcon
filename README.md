Scripts to analyze the EU Commision Consultation on Copyright Reform.

Texts found useful:
http://www.linuxjournal.com/article/9347

=======
Currently downloads zip files and make some category and extension statistics.
Basic ODT file parsing is implemented.
analyze.py can loop through all ODT files in all zip files and call the ODT parser.

Recommended execution:
```
# python3 download_files.py
# python3 analyze.py stats input/*.zip
# python3 analyze.py analyze input/users_en.zip #Doesn't do anything meaningful right now, but takes long time anyway :)
```
