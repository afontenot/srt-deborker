import argparse
import struct
from collections import defaultdict

# list of supported text encodings: most of them are very improbable
# no great way to get this programatically, so copied from Python docs
ENCODINGS = ['latin_1', 'cp1251', 'cp1252', 'big5', 'big5hkscs', 'cp037', 
             'cp273', 'cp424', 'cp437', 'cp500', 'cp720', 'cp737', 'cp775', 
             'cp850', 'cp852', 'cp855', 'cp856', 'cp857', 'cp858', 'cp860', 
             'cp861', 'cp862', 'cp863', 'cp864', 'cp865', 'cp866', 'cp869', 
             'cp874', 'cp875', 'cp932', 'cp949', 'cp950', 'cp1006', 'cp1026', 
             'cp1125', 'cp1140', 'cp1250', 'cp1253', 'cp1254', 'cp1255', 
             'cp1256', 'cp1257', 'cp1258', 'euc_jp', 'euc_jis_2004', 
             'euc_jisx0213', 'euc_kr', 'gb2312', 'gbk', 'gb18030', 'hz', 
             'iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_2004', 
             'iso2022_jp_3', 'iso2022_jp_ext', 'iso2022_kr', 'iso8859_2', 
             'iso8859_3', 'iso8859_4', 'iso8859_5', 'iso8859_6', 'iso8859_7', 
             'iso8859_8', 'iso8859_9', 'iso8859_10', 'iso8859_11', 
             'iso8859_13', 'iso8859_14', 'iso8859_15', 'iso8859_16', 'johab', 
             'koi8_r', 'koi8_t', 'koi8_u', 'kz1048', 'mac_cyrillic', 
             'mac_greek', 'mac_iceland', 'mac_latin2', 'mac_roman', 
             'mac_turkish', 'ptcp154', 'shift_jis', 'shift_jis_2004', 
             'shift_jisx0213', 'utf_32', 'utf_32_be', 'utf_32_le', 'utf_16', 
             'utf_16_be', 'utf_16_le', 'utf_7']


# A simple wrapper to allow selective printing to a file or stdout
class OutputWriter():
    def __init__(self, filename):
        self.has_file_handle = False
        if filename:
            self.out = open(filename, "w")
            self.has_file_handle = True
        else:
            import sys
            self.out = sys.stdout

    def __enter__(self):
        return self

    def write(self, val):
        self.out.write(val)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.has_file_handle:
            self.out.close()

# accept bytes, return only the non-ASCII bytes
def getnonascii(bstr):
    out = b""
    for byte in struct.iter_unpack("1c", bstr):
        byte = byte[0]
        if not byte.isascii():
            out += byte
    return out

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--encoding")
    parser.add_argument("-o", "--output")
    parser.add_argument("srt", default=None, nargs='?')
    args = parser.parse_args()
    
    if args.srt and args.srt == args.output:
        print("output can't be the same as the input!")
        return

    if not args.encoding and not args.srt:
        orig = input("original text: ")
        output = input("output text (if known): ")
        if output.strip() == "":
            for encoding in ENCODINGS:
                try:
                    print(encoding, orig.encode("utf-8").decode(encoding))
                except:
                    continue
        else:
            for encoding in ENCODINGS:
                try:
                    if output.strip() == orig.encode("utf-8").decode(encoding):
                        print(encoding)
                except:
                    continue

    # Automatic mode requires reading the file twice, but usually works.
    # Simply assume that any non-ascii n byte strings are really supposed to be 
    # n/2 byte UTF-8 strings, and see which encodings cause byte doublings of 
    # this kind, picking the best choice using a histogram.
    if not args.encoding and args.srt:
        hist = defaultdict(int)
        results = defaultdict(str)
        f = b''
        example = ""
        with open(args.srt, 'r', encoding="utf-8") as srt:
            for s in srt:
                if not s.isascii():
                    if not example:
                        example = s.strip()
                    for encoding in ENCODINGS:
                        # most encodings are going to fail for random non-ASCII 
                        # charcters an error means the encoding doesn't work, 
                        # so we just skip it
                        try:
                            # get all non-ASCII parts of string as a normal 
                            # Python string
                            unicode_nonascii = getnonascii(s.encode("utf-8"))
                            orig = unicode_nonascii.decode("utf-8")
                            # start with the full line here instead of orig 
                            # just to make sure the whole string is encodable 
                            # with the chosen encoding
                            encoding_nonascii = getnonascii(s.encode(encoding))
                            result = encoding_nonascii.decode("utf-8")
                            if len(orig) == 2 * len(result):
                                results[encoding] += result
                                hist[encoding] += 1
                        except (UnicodeEncodeError, UnicodeDecodeError):
                            continue
        best = sorted(list(hist.items()), key=lambda x: x[1], reverse=True)
        best_score = best[0][1]
        seen = []
        for enc, score in best:
            if score == best_score:
                if not results[enc] in seen:
                    seen.append(results[enc])
                    fixed_example = example.encode(enc).decode("utf-8")
                    print(enc, f'({example} -> {fixed_example})')
            else:
                break
        print()

    if args.srt:
        encoding = args.encoding
        if not encoding:
            encoding = input("enter encoding choice: ")
        with open(args.srt, 'r', encoding="utf-8") as srt:
            with OutputWriter(args.output) as out:
                for line in srt:
                    out.write(line.encode(encoding).decode("utf-8"))

if __name__ == "__main__":
    main()
