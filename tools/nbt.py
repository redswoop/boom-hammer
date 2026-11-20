"""Minimal NBT reader/writer. Java files are big-endian (usually gzipped);
Bedrock .mcstructure files are little-endian and uncompressed."""
import gzip, struct

END, BYTE, SHORT, INT, LONG, FLOAT, DOUBLE, BYTES, STRING, LIST, COMPOUND, INTS, LONGS = range(13)


class Tag:
    """A typed value, used where the Python type alone is ambiguous."""
    __slots__ = ("t", "v", "sub")

    def __init__(self, t, v, sub=None):
        self.t, self.v, self.sub = t, v, sub

    def __repr__(self):
        return f"Tag({self.t},{self.v!r})"


def B(v): return Tag(BYTE, v)
def S(v): return Tag(SHORT, v)
def I(v): return Tag(INT, v)
def L(v): return Tag(LONG, v)
def F(v): return Tag(FLOAT, v)
def Str(v): return Tag(STRING, v)
def Lst(sub, items): return Tag(LIST, items, sub if items else None)  # an empty list we make is written untyped, as before


_FMT = {BYTE: "b", SHORT: "h", INT: "i", LONG: "q", FLOAT: "f", DOUBLE: "d"}


class Reader:
    def __init__(self, data, little=False, typed=False):
        self.d, self.p, self.e, self.typed = data, 0, "<" if little else ">", typed

    def num(self, f):
        n = struct.calcsize(f)
        v = struct.unpack_from(self.e + f, self.d, self.p)[0]
        self.p += n
        return v

    def string(self):
        n = self.num("H")
        s = self.d[self.p:self.p + n].decode("utf-8", "replace")
        self.p += n
        return s

    def payload(self, t):
        if t in _FMT:
            v = self.num(_FMT[t])
            return Tag(t, v) if self.typed else v
        if t == STRING:
            return self.string()
        if t == BYTES:
            n = self.num("i"); v = self.d[self.p:self.p + n]; self.p += n
            return Tag(t, v) if self.typed else v
        if t == INTS:
            n = self.num("i"); v = list(struct.unpack_from(f"{self.e}{n}i", self.d, self.p)); self.p += 4 * n
            return Tag(t, v) if self.typed else v
        if t == LONGS:
            n = self.num("i"); v = list(struct.unpack_from(f"{self.e}{n}q", self.d, self.p)); self.p += 8 * n
            return Tag(t, v) if self.typed else v
        if t == LIST:
            sub = self.num("b"); n = self.num("i")
            items = [self.payload(sub) for _ in range(n)]
            # Typed: keep the element type so the list can be written back unchanged.
            return Tag(LIST, items, sub) if self.typed else items
        if t == COMPOUND:
            out = {}
            while True:
                tt = self.num("b")
                if tt == END:
                    return out
                k = self.string()
                out[k] = self.payload(tt)
        raise ValueError(f"bad tag {t}")


def load(path, little=False, typed=False):
    """Plain Python values. With typed=True, numbers come back as Tag so the
    byte/int distinction survives (Bedrock block states need it)."""
    data = open(path, "rb").read()
    if data[:2] == b"\x1f\x8b":
        data = gzip.decompress(data)
    r = Reader(data, little, typed)
    t = r.num("b"); r.string()
    return r.payload(t)


class Writer:
    def __init__(self, little=True):
        self.e, self.out = "<" if little else ">", []

    def num(self, f, v): self.out.append(struct.pack(self.e + f, v))

    def string(self, s):
        b = s.encode("utf-8"); self.num("H", len(b)); self.out.append(b)

    @staticmethod
    def kind(v):
        if isinstance(v, Tag): return v.t
        if isinstance(v, dict): return COMPOUND
        if isinstance(v, str): return STRING
        if isinstance(v, bool): return BYTE
        if isinstance(v, int): return INT
        if isinstance(v, float): return FLOAT
        raise ValueError(f"untyped value {v!r}: wrap lists in Lst()")

    def payload(self, v):
        t = self.kind(v)
        x = v.v if isinstance(v, Tag) else v
        if t in _FMT:
            self.num(_FMT[t], int(x) if t in (BYTE, SHORT, INT, LONG) else x)
        elif t == STRING:
            self.string(x)
        elif t == LIST:
            sub = v.sub if (x or v.sub is not None) else END
            self.num("b", sub); self.num("i", len(x))
            for it in x:
                self.payload(it)
        elif t == COMPOUND:
            for k, it in x.items():
                self.num("b", self.kind(it)); self.string(k); self.payload(it)
            self.num("b", END)
        elif t == INTS:
            self.num("i", len(x)); self.out.append(struct.pack(f"{self.e}{len(x)}i", *x))
        elif t == LONGS:
            self.num("i", len(x)); self.out.append(struct.pack(f"{self.e}{len(x)}q", *x))
        elif t == BYTES:
            self.num("i", len(x)); self.out.append(bytes(x))
        else:
            raise ValueError(t)


def dump(root, path, little=True):
    w = Writer(little)
    w.num("b", COMPOUND); w.string(""); w.payload(root)
    open(path, "wb").write(b"".join(w.out))
