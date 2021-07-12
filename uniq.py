import sys
import argparse
import queue
import re

parser = argparse.ArgumentParser()

parser.add_argument(
    "fileName", nargs='?', type=argparse.FileType('r', encoding="utf-8"), default="-")
parser.add_argument(
    "output", nargs='?', type=argparse.FileType('w', encoding="utf-8"), default="-")
parser.add_argument(
    "-c", "--count", help="prefix lines by the number of occurrences",
    action="store_true")
parser.add_argument("-d", "--repeated",
                    help="only print duplicate lines, one for each group",
                    action="store_true")
parser.add_argument("-D", "--all-repeated", help="increase output verbosity")
parser.add_argument("-f", "--skip-fields=N",
                    help="avoid comparing the first N fields")
parser.add_argument("-i", "--igonore-case",
                    help="ignore differences in case when comparing",
                    action="store_true")
parser.add_argument("-s", "--skip-chars=N",
                    help="avoid comparing the first N characters")
parser.add_argument(
    "-u", "--unique", help="only print unique lines",
    action="store_true")
parser.add_argument("-z", "--zero-terminated",
                    help="line delimiter is NUL, not newline")
parser.add_argument("-w", "--check-chars",
                    help="compare no more than N characters in lines")


def test(file, args, removedLines) -> bool:
    lines = file.read().splitlines()
    if not lines:
        return False
    NumOfLines = len(lines)

    if args.igonore_case:
        comparison = lines[0]
        for s_line in range(1, NumOfLines):
            if re.search(lines[s_line], comparison, re.IGNORECASE) is None:
                print(comparison)
                comparison = lines[s_line]
            elif s_line == NumOfLines-1:
                print(comparison)
    else:
        for s_line in range(1, NumOfLines):
            # 行-１とその一行前の行を比較
            if lines[s_line] != lines[s_line-1]:
                print(lines[s_line-1])
            elif s_line == NumOfLines-1:
                print(lines[s_line])


def printLines(args, removedLines, duplicateLines, nonDuplicateLines):
    while True:
        file = args.fileName
        if count(file, args, removedLines, nonDuplicateLines) is False:
            break


def count(file, args, removedLines, duplicateLines, nonDuplicateLines) -> bool:

    lines = file.read().splitlines()
    if not lines:
        return False
    NumOfLines = len(lines)
    comparison = lines[0]
    i = 1
    if args.igonore_case:
        for s_line in range(1, NumOfLines):
            if re.search(lines[s_line], comparison, re.IGNORECASE) is None:
                removedLines.put((i, comparison))
                if i > 1:
                    duplicateLines.put((i, comparison))
                else:
                    nonDuplicateLines.put((i, comparison))
                comparison = lines[s_line]
                i = 1
            else:
                i += 1
            if s_line == NumOfLines-1:
                removedLines.put((i, lines[s_line]))
                if i > 1:
                    duplicateLines.put((i, comparison))
                else:
                    nonDuplicateLines.put((i, comparison))
    else:
        for s_line in range(1, NumOfLines):
            # 行-１とその一行前の行を比較
            if lines[s_line] != comparison:
                removedLines.put((i, comparison))
                if i > 1:
                    duplicateLines.put((i, comparison))
                else:
                    nonDuplicateLines.put((i, comparison))
                comparison = lines[s_line]
                i = 1
            else:
                i += 1
            if s_line == NumOfLines-1:
                removedLines.put((i, lines[s_line]))
                if i > 1:
                    duplicateLines.put((i, comparison))
                else:
                    nonDuplicateLines.put((i, comparison))


args = parser.parse_args()

removedLines = queue.Queue()
duplicateLines = queue.Queue()
nonDuplicateLines = queue.Queue()

if args.fileName.name != '<stdin>':
    try:
        with open(args.fileName.name) as file:
            count(file, args, removedLines,
                  duplicateLines, nonDuplicateLines)
            tmp = None
            if args.unique and args.repeated:
                print()
            elif args.unique:
                tmp = nonDuplicateLines
            elif args.repeated:
                tmp = duplicateLines
            else:
                tmp = removedLines

            while not tmp.empty():
                if args.count:
                    print(str(tmp.get()[0]) + " " + tmp.get()[1])
                else:
                    print(tmp.get()[1])
        file.close()
    except FileNotFoundError:
        sys.exit("No such file or directory:" + file)

else:
    printLines(args, removedLines,
               duplicateLines, nonDuplicateLines)
    while not removedLines.empty():
        tmp = removedLines.get()
        if args.count:
            print(str(tmp[0]) + " " + tmp[1])
        else:
            print(tmp[1])
