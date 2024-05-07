# file: ielib.py
# author: Roch Schanen
# created: 2024 05 06
# content: import export library
# repository: https://github.com/RochSchanen/postscript_dev
# comment: early stages of development

def file_export(fp, *dt, fm = "+.6E"):
    from os.path import basename
    from time import strftime, gmtime
    # get time stamp
    ts = strftime("%a, %d %b %Y, %H:%M:%S", gmtime())
    # get the number of lines and columns
    m, N = len(dt), []
    for d in dt: N.append(len(d))
    if not min(N) == max(N):
        print(f"inconsistent number of lines: {N}.")
        print(f"file '{basename(fp)}' not exported.")
        return
    # create file
    fh = open(fp, 'w')
    fh.write(f'# file: {basename(fp)}\n')
    fh.write(f'# created: {ts}\n')
    # write lines
    for j in range(min(N)):
        # write columns
        for i in range(m):
            # build string value
            v = f"{dt[i][j]:{fm}}"
            # include separator
            s = f"\t{v}" if i else f"{v}"
            # export string
            fh.write(s)
        # export end-of-line
        fh.write("\n")
    # done
    fh.close()
    return

def file_import(fp, start = 0, stop = -1):
    from numpy import array
    from os.path import exists
    if exists(fp) is False: return None
    fh = open(fp)
    tx = fh.read()
    dt = []
    for l in tx.split('\n')[start:stop]:
        if l[0] == "#": continue
        v = []
        for s in  l.split(): v.append(float(s))
        dt.append(v)
    return array(dt).transpose()
