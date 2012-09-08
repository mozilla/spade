def read_props(file_name):
    props = {}
    for line in open(file_name, 'r'):
        line = line.strip()
        if not line or line[0] == '#':
            # skip blank lines and comments
            continue
        words = line.split()

        columns = len(words)
        if columns > 3 or columns < 2:
            # bad line
            continue

        words = [w.strip() for w in words]

        moz = words[0]
        webkit = words[1]
        non_prefix = words[2] if columns == 3 else ''

        props[webkit] = (moz, non_prefix)

    return props


if __name__ == '__main__':
    from pprint import pprint
    import sys
    pprint(read_props(sys.argv[1]))
