import sys
import argparse
import queue
import re

parser = argparse.ArgumentParser()

parser.add_argument("fileName", nargs='?', type=argparse.FileType(
    'r', encoding="utf-8"), default="-")
parser.add_argument("output", nargs='?', type=argparse.FileType(
    'w', encoding="utf-8"), default="-")
parser.add_argument("-c", "--count", help="prefix lines by the number of occurrences",
                    action="store_true")
parser.add_argument("-d", "--repeated",
                    help="only print duplicate lines, one for each group",
                    action="store_true")
parser.add_argument("-i", "--igonore-case",
                    help="ignore differences in case when comparing",
                    action="store_true")
parser.add_argument("-u", "--unique", help="only print unique lines",
                    action="store_true")
group = parser.add_mutually_exclusive_group()
group.add_argument("-w", "--check-chars", type=int,
                   help="compare no more than N characters in lines")
group.add_argument("-s", "--skip-chars", type=int,
                   help="avoid comparing the first N characters")

parser.add_argument("-D", "--all-repeated", help="increase output verbosity")
parser.add_argument("-f", "--skip-fields",
                    help="avoid comparing the first N fields")
parser.add_argument("-z", "--zero-terminated",
                    help="line delimiter is NUL, not newline")


def printLines(args, removedLines, duplicateLines, nonDuplicateLines):
    while True:
        file = args.fileName
        if count(file, args, removedLines, nonDuplicateLines) is False:
            break


def putToDuplicateQueue(num, comparison):
    if num > 1:
        duplicateLines.put((num, comparison))
    else:
        nonDuplicateLines.put((num, comparison))


def count(file, args, removedLines, duplicateLines, nonDuplicateLines) -> bool:
    lines = file.read().splitlines()
    if not lines:
        return False
    NumOfLines: int = len(lines)
    comparison: str = lines[0]
    i = 1

    if args.check_chars is None:
        backPos = None
    elif args.check_chars == 0:
        removedLines.put((NumOfLines, comparison))
        putToDuplicateQueue(NumOfLines, comparison)
        return
    else:
        backPos = args.check_chars

    if args.skip_chars is None:
        forthPos = 0
    else:
        forthPos = args.skip_chars

    if args.igonore_case:
        flag = re.IGNORECASE
    else:
        flag = 0

    for s_line in range(1, NumOfLines):
        if re.search(lines[s_line][forthPos:backPos], comparison[forthPos:backPos], flag) is None:
            removedLines.put((i, comparison))
            putToDuplicateQueue(i, comparison)
            comparison = lines[s_line]
            i = 1
        elif forthPos >= len(lines[s_line]):
            i += 1
            continue
        elif forthPos <= len(lines[s_line]):
            i += 1

        if s_line == NumOfLines-1:
            removedLines.put((i, lines[s_line]))
            putToDuplicateQueue(i, comparison)


try:
    args = parser.parse_args()
except Exception as e:
    error_type = type(e).__name__
    sys.stderr.write("{0}: {1}\n".format(error_type, e.message))
    sys.exit(1)

removedLines = queue.Queue()
duplicateLines = queue.Queue()
nonDuplicateLines = queue.Queue()

if args.fileName.name != '<stdin>':
    try:
        with open(args.fileName.name) as file:
            count(file, args, removedLines,
                  duplicateLines, nonDuplicateLines)
            tmpQueue = None
            if args.unique and args.repeated:
                pass
            elif args.unique:
                tmpQueue = nonDuplicateLines
            elif args.repeated:
                tmpQueue = duplicateLines
            else:
                tmpQueue = removedLines

            if args.output.name != '<stdout>':
                with open(args.output.name, args.output.mode) as wFile:
                    while not tmpQueue.empty():
                        tmp = tmpQueue.get()
                        if args.count:
                            wFile.write(
                                str(tmp[0]) + " " + tmp[1] + '\n')
                        else:
                            wFile.write(tmp[1] + '\n')
            else:
                while not tmpQueue.empty():
                    tmp = tmpQueue.get()
                    if args.count:
                        print(str(tmp[0]) + " " + tmp[1])
                    else:
                        print(tmp[1])

    except FileNotFoundError:
        sys.exit("No such file or directory:" + file)

else:
    printLines(args, removedLines,
               duplicateLines, nonDuplicateLines)
    while not removedLines.empty():
        tmpQueue = None
        if args.unique and args.repeated:
            pass
        elif args.unique:
            tmpQueue = nonDuplicateLines
        elif args.repeated:
            tmpQueue = duplicateLines
        else:
            tmpQueue = removedLines

        while not tmpQueue.empty():
            tmp = tmpQueue.get()
            if args.count:
                print(str(tmp[0]) + " " + tmp[1])
            else:
                print(tmp[1])
