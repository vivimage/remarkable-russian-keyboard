"""Pack files into a Qt binary resource file (.rcc, format version 1, uncompressed).

Usage:
  python3 make_rcc.py build <out.rcc> <resource/path>=<local file> [...]
  python3 make_rcc.py list <file.rcc>

Same format as the .rcc files qt-resource-rebuilder already loads on the tablet.
"""
import struct
import sys


def qt_hash(name):
    h = 0
    for ch in name:
        h = ((h << 4) + ord(ch)) & 0xFFFFFFFF
        h ^= (h & 0xF0000000) >> 23
        h &= 0x0FFFFFFF
    return h


class Node:
    def __init__(self, name):
        self.name = name
        self.children = {}
        self.data = None  # bytes for a file, None for a directory


def build(out_path, entries):
    root = Node("")
    for res_path, local in entries:
        node = root
        for part in res_path.strip("/").split("/"):
            node = node.children.setdefault(part, Node(part))
        node.data = open(local, "rb").read()

    # Breadth-first order; children of one directory are contiguous and sorted by name hash.
    order = [root]
    first_child = {}
    i = 0
    while i < len(order):
        n = order[i]
        if n.data is None:
            kids = sorted(n.children.values(), key=lambda c: qt_hash(c.name))
            first_child[id(n)] = len(order)
            order.extend(kids)
        i += 1

    names = b""
    name_off = {}
    data = b""
    data_off = {}
    for n in order[1:]:
        if n.name not in name_off:
            name_off[n.name] = len(names)
            names += struct.pack(">HI", len(n.name), qt_hash(n.name)) + n.name.encode("utf-16-be")
        if n.data is not None:
            data_off[id(n)] = len(data)
            data += struct.pack(">I", len(n.data)) + n.data

    tree = b""
    for n in order:
        off = name_off.get(n.name, 0)
        if n.data is None:
            tree += struct.pack(">IHII", off, 2, len(n.children), first_child[id(n)])
        else:
            tree += struct.pack(">IHHHI", off, 0, 0, 1, data_off[id(n)])

    header_len = 20
    data_start = header_len
    names_start = data_start + len(data)
    tree_start = names_start + len(names)
    with open(out_path, "wb") as f:
        f.write(b"qres" + struct.pack(">IIII", 1, tree_start, data_start, names_start))
        f.write(data + names + tree)


def list_rcc(path):
    blob = open(path, "rb").read()
    assert blob[:4] == b"qres", "not an rcc file"
    version, tree, data, names = struct.unpack(">IIII", blob[4:20])
    assert version == 1, f"only format version 1 is handled, got {version}"

    def name_at(off):
        (length,) = struct.unpack(">H", blob[names + off : names + off + 2])
        (stored_hash,) = struct.unpack(">I", blob[names + off + 2 : names + off + 6])
        text = blob[names + off + 6 : names + off + 6 + 2 * length].decode("utf-16-be")
        assert stored_hash == qt_hash(text), f"hash mismatch for {text}"
        return text

    result = []

    def walk(index, prefix):
        node = blob[tree + 14 * index : tree + 14 * index + 14]
        off, flags = struct.unpack(">IH", node[:6])
        label = prefix + ("/" + name_at(off) if index else "")
        if flags & 2:
            count, first = struct.unpack(">II", node[6:14])
            for c in range(first, first + count):
                walk(c, label)
        else:
            _country, _lang, doff = struct.unpack(">HHI", node[6:14])
            (size,) = struct.unpack(">I", blob[data + doff : data + doff + 4])
            result.append((label, blob[data + doff + 4 : data + doff + 4 + size]))

    walk(0, "")
    return result


if __name__ == "__main__":
    if sys.argv[1] == "build":
        build(sys.argv[2], [a.split("=", 1) for a in sys.argv[3:]])
    for res_path, content in list_rcc(sys.argv[2]):
        print(f"{res_path}  {len(content)} bytes")
