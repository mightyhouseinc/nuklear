
import fnmatch
import os.path
import sys

def print_help():
    print(
"""usage: python single_header_packer.py --macro <macro> [--intro <files>] --pub <files> --priv <files> [--outro <files>]

       where <files> can be a comma-separated list of files. e.g. --priv *.c,inc/*.h

       The resulting code is packed as follows:

           /*
           [intro file contents]
           */

           #ifndef <macro>_SINGLE_HEADER
           #define <macro>_SINGLE_HEADER
           [public header file contents]
           #endif /* <macro>_SINGLE_HEADER */

           #ifdef <macro>_IMPLEMENTATION
           [private header and source file contents]
           #endif /* <macro>_IMPLEMENTATION */

           /*
           [outro file contents]
           */""")

def parse_files(arg):
    files = []
    paths = arg.split(",")
    for path in paths:
        if "*" in path:
            # Wildcard
            d = os.path.dirname(path)
            if d == "": d = "."
            if d == " ": continue
            if not os.path.exists(d):
                print(f"{d} does not exist.")
                exit()

            wildcard = os.path.basename(path)
            unsorted = [
                os.path.join(d, file)
                for file in os.listdir(d)
                if fnmatch.fnmatch(file, wildcard)
            ]
            unsorted.sort()
            files.extend(unsorted)

        elif not os.path.exists(path):
            print(f"{path} does not exist.")
            exit()
        elif os.path.isdir(path):
            print(f"{path} is a directory. Expected a file name.")
            exit()
        else:
            files.append(path)

    return files;

def omit_includes(str, files):
    for file in files:
        fname = os.path.basename(file)
        if ".h" in file:
            str = str.replace("#include \"" + fname + "\"", "");
            str = str.replace(f"#include <{fname}>", "");
    return str

# Main start
# ==========

if len(sys.argv) < 2:
    print_help()
    exit()

intro_files = []
pub_files = []
priv_files = []
outro_files = []
cur_arg = 1
macro = ""

# Parse args
# ----------
while cur_arg < len(sys.argv):
    if sys.argv[cur_arg] == "--help":
        print_help()
        exit()
    elif sys.argv[cur_arg] == "--macro":
        cur_arg += 1
        macro = sys.argv[cur_arg]
    elif sys.argv[cur_arg] == "--intro":
        cur_arg += 1
        intro_files = parse_files(sys.argv[cur_arg])
    elif sys.argv[cur_arg] == "--pub":
        cur_arg += 1
        pub_files = parse_files(sys.argv[cur_arg])
    elif sys.argv[cur_arg] == "--priv":
        cur_arg += 1
        priv_files = parse_files(sys.argv[cur_arg])
    elif sys.argv[cur_arg] == "--outro":
        cur_arg += 1
        outro_files = parse_files(sys.argv[cur_arg])
    else:
        print(f"Unknown argument {sys.argv[cur_arg]}")

    cur_arg += 1

if macro == "":
    print("Option --macro <macro> is mandatory")
    exit()

# Print concatenated output
# -------------------------
print("/*")
for f in intro_files:
    sys.stdout.write(open(f, 'r').read())
print("*/")

# print(os.linesep + "#ifndef " + macro + "_SINGLE_HEADER");
# print("#define " + macro + "_SINGLE_HEADER");
print("#ifndef NK_SINGLE_FILE");
print("  #define NK_SINGLE_FILE");
print("#endif");
print("");

for f in pub_files:
    sys.stdout.write(open(f, 'r').read())
# print("#endif /* " + macro + "_SINGLE_HEADER */");

print(f"{os.linesep}#ifdef {macro}_IMPLEMENTATION");
print("");
for f in priv_files:
    print(omit_includes(open(f, 'r').read(),
                        pub_files + priv_files))
print(f"#endif /* {macro}_IMPLEMENTATION */");

print(f"{os.linesep}/*")
for f in outro_files:
    sys.stdout.write(open(f, 'r').read())
print(f"*/{os.linesep}")

