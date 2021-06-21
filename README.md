# srt-deborker
fix subtitles that have been incorrectly double encoded

## What problem does srt-deborker solve?

Have you ever encountered this problem with subtitles (example from 
[this thread](https://forum.videohelp.com/threads/355208-Strange-Characters-in-Subtitle-Editing-using-accents-and-diacritic-marks)?

> Deixe a oposiÃ§Ã£o ter

This subtitle text is supposed to say "Deixe a oposição ter". This is a 
variant of [Mojibake](https://en.wikipedia.org/wiki/Mojibake), where 
text is garbled as a result of using an incorrect encoding. In this 
case, an unknown software tool has decoded some text (usually encoded 
as UTF-8) with some other character encoding (often the user's local 
default), and then the result has been re-encoded as a UTF-8 file.

In the case above, the characters "çã" are encoded in UTF-8 using the 
bytes \xC3\xA7\xC3\xA3 --- two bytes for each character. Most local 
encodings (the most common being 
[latin1](https://en.wikipedia.org/wiki/ISO/IEC_8859-1)) are one-byte 
encodings, meaning that each character that can be represented in the 
encoding is encoded by exactly one byte. (For this reason, these 
encodings are very limited in the number of characters they can encode. 
They are usually *local* encodings, meaning that they encode characters 
that are commonly used in a specific language or region.)

Suppose you have software (usually on Windows, Linux does not have this 
issue) that assumes a file containing these bytes is in a local 
encoding, not UTF-8. For example, in latin1, 

    \xC3 -> À
    \xA7 -> §
    \xC3 -> À
    \xA3 -> £

In other words, this broken software will display those two correctly 
encoded UTF-8 characters as "Ã§Ã£", exactly what we see in the example. 
If you see this, it's *possible* that your movie player is broken in 
this way. But it's more likely that someone else broke the subtitle 
file by opening it in a broken tool which resaved it as UTF-8 or copied 
the improperly decoded subtitles into a text editor which did the same. 
A broken tool to extract the subtitles from one file might have the 
same effect. If you know of tools which have this bug, please file an 
issue and I'll list them here.

In other words, the subtitle file now literally contains the bytes for 
"Ã§Ã£" encoded as UTF-8, and your software is decoding and displaying 
those bytes correctly. My experience is that these files are 
unfortunately very common.

## Why use srt-deborker?

If you know what text encoding was incorrectly used as part of the 
chain, you could easily fix the text manually. For example, knowing 
that the above example was incorrectly decoded as latin1 and saved as 
UTF-8, we simply encode the decoded string (e.g. "Ã§Ã£") as latin1, 
then save or print the resulting bytes as if they were UTF-8.

However, it's already nice to have a tool to do this automatically. 
Moreover, sometimes you don't know what encoding was used to decode the 
text. That's when srt-deborker really comes in handy.

The default or automatic mode works like this:

    python debork.py mysubtitles.srt

The program will scan each line of the file for non-ASCII characters 
(the ASCII charcters have the same byte values in UTF-8 as in most 
major alternatives). If the line contains non-ASCII characters, the 
program will check whether the string can be encoded in each of the 
alternative encodings it knows about. If it can, it checks whether the 
non-ASCII characters use *half* as many bytes when encoded with that 
encoding. If so, it's a candidate for being the encoding that the 
software used to decode the subtitles. (Most text shown in English 
subtitles uses one or two bytes in UTF-8. I'm open to making this 
program more robust to working with subtitles in other languages in the 
future.)

As it scans each line of the file, the program builds up a histogram of 
whether a particular encoding assumption passes the test above. After 
it's done, you'll see one or more potential encodings, and you can 
choose the one that seems to give the correct results.

## How do I use srt-deborker?

If you just want to scan and fix your subtitles (in SubRip / .srt 
format), it's simple:

    python debork.py -o <output.srt> <input.srt>
    
If the deborker works correctly, you should see one or more encodings 
along with a sample piece of text chosen from the file which is "fixed" 
using the selected encoding. Simply type the name of the encoding that 
fixes the file (there may be more than one, some encodings overlap).

If you already know which encoding was used, you can enter it directly 
as follows:

    python debork.py -e <encoding> -o <output.srt> <input.srt>

What if you just have a piece of text like "Deixe a oposição ter" and 
you want to see how it would be affected by different encodings? Simply 
run the script without any arguments at all, and enter the text at the 
prompt. You can also enter the result you're looking for, and get a 
list of encodings instead.
