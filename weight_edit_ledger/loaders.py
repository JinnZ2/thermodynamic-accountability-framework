#!/usr/bin/env python3
# loaders.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
#
# Checkpoint readers for audit.py, stdlib only. Both formats are simple
# containers; tensors are read one at a time, never the whole file.
#
#   safetensors   [u64 LE header length][JSON header][raw bytes]
#                 header: {name: {dtype, shape, data_offsets: [start, end]}, "__metadata__": {...}}
#                 offsets are relative to the end of the header
#   .npz          zip of NAME.npy members
#   .npy          b"\x93NUMPY" + major, minor + header length (u16 LE v1, u32 LE v2/3)
#                 + header dict {'descr', 'fortran_order', 'shape'} + raw bytes
#   .json         {name: number | nested list}  (the original test format)
#
# dtypes: F64 / F32 / F16 via struct ('d' / 'f' / 'e'); BF16 by shifting the
# 16 bits into the top half of a float32. Anything else -> LoaderError.
#
#   r = open_checkpoint(path)      r.names() -> sorted names
#   r.read(name) -> flat list of floats (one tensor in memory)
#   r.shape(name), r.dtype(name)
#
# Writers (write_safetensors, write_npz) exist for the tests: tiny synthetic
# files made by the same code, no external libraries.

import ast
import hashlib
import json
import struct
import zipfile

CHUNK = 1 << 20

# dtype -> (bytes per element, struct char or None for BF16)
DTYPES = {"F64": (8, "d"), "F32": (4, "f"), "F16": (2, "e"), "BF16": (2, None)}
NPY_DESCR = {"<f8": "F64", "<f4": "F32", "<f2": "F16"}
DESCR_NPY = dict((v, k) for k, v in NPY_DESCR.items())
NPY_MAGIC = b"\x93NUMPY"


class LoaderError(ValueError):
    pass


def file_hash(path):
    """sha256 of the file bytes, read in chunks."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def _count(shape):
    n = 1
    for s in shape:
        n *= int(s)
    return n


def decode(raw, dtype):
    """little-endian bytes -> list of floats."""
    if dtype not in DTYPES:
        raise LoaderError("dtype %s not supported (F64, F32, F16, BF16)" % dtype)
    size, ch = DTYPES[dtype]
    if len(raw) % size:
        raise LoaderError("byte length %d not a multiple of %d for %s" % (len(raw), size, dtype))
    n = len(raw) // size
    if ch is not None:
        return list(struct.unpack("<%d%s" % (n, ch), raw))
    halves = struct.unpack("<%dH" % n, raw)
    return list(struct.unpack("<%df" % n, struct.pack("<%dI" % n, *[h << 16 for h in halves])))


def encode(values, dtype):
    """list of floats -> little-endian bytes (BF16 truncates the low 16 bits)."""
    if dtype not in DTYPES:
        raise LoaderError("dtype %s not supported" % dtype)
    n = len(values)
    size, ch = DTYPES[dtype]
    if ch is not None:
        return struct.pack("<%d%s" % (n, ch), *values)
    words = struct.unpack("<%dI" % n, struct.pack("<%df" % n, *values))
    return struct.pack("<%dH" % n, *[w >> 16 for w in words])


class SafetensorsReader(object):
    def __init__(self, path):
        self.path = path
        with open(path, "rb") as f:
            head = f.read(8)
            if len(head) != 8:
                raise LoaderError("safetensors: file shorter than 8 bytes")
            (hlen,) = struct.unpack("<Q", head)
            raw = f.read(hlen)
            if len(raw) != hlen:
                raise LoaderError("safetensors: header truncated")
        try:
            hdr = json.loads(raw.decode("utf-8"))
        except ValueError as e:
            raise LoaderError("safetensors: header is not JSON: %s" % e)
        hdr.pop("__metadata__", None)
        self.base = 8 + hlen
        self.hdr = hdr
        for k, v in hdr.items():
            s, e = v["data_offsets"]
            size = DTYPES.get(v["dtype"], (None,))[0]
            if size is not None and e - s != size * _count(v["shape"]):
                raise LoaderError("safetensors: %s offsets do not match shape x dtype" % k)

    def names(self):
        return sorted(self.hdr)

    def dtype(self, name):
        return self.hdr[name]["dtype"]

    def shape(self, name):
        return list(self.hdr[name]["shape"])

    def read(self, name):
        v = self.hdr[name]
        s, e = v["data_offsets"]
        with open(self.path, "rb") as f:
            f.seek(self.base + s)
            raw = f.read(e - s)
        if len(raw) != e - s:
            raise LoaderError("safetensors: %s data truncated" % name)
        return decode(raw, v["dtype"])


def _npy_header(f):
    if f.read(6) != NPY_MAGIC:
        raise LoaderError("npy: bad magic")
    major = f.read(2)[0]
    hlen = struct.unpack("<H", f.read(2))[0] if major == 1 else struct.unpack("<I", f.read(4))[0]
    try:
        d = ast.literal_eval(f.read(hlen).decode("latin1"))
    except (ValueError, SyntaxError) as e:
        raise LoaderError("npy: header not a literal dict: %s" % e)
    if d.get("fortran_order"):
        raise LoaderError("npy: fortran_order arrays not supported")
    if d.get("descr") not in NPY_DESCR:
        raise LoaderError("npy: descr %r not supported (<f8, <f4, <f2)" % d.get("descr"))
    return NPY_DESCR[d["descr"]], list(d["shape"])


class NpzReader(object):
    def __init__(self, path):
        self.path = path
        self.meta = {}
        with zipfile.ZipFile(path) as z:
            for m in z.namelist():
                if not m.endswith(".npy"):
                    continue
                with z.open(m) as f:
                    self.meta[m[:-4]] = (m,) + _npy_header(f)

    def names(self):
        return sorted(self.meta)

    def dtype(self, name):
        return self.meta[name][1]

    def shape(self, name):
        return list(self.meta[name][2])

    def read(self, name):
        member, dtype, shape = self.meta[name]
        with zipfile.ZipFile(self.path) as z, z.open(member) as f:
            _npy_header(f)
            want = DTYPES[dtype][0] * _count(shape)
            raw = f.read(want)
        if len(raw) != want:
            raise LoaderError("npy: %s data truncated" % name)
        return decode(raw, dtype)


def _flat(v):
    if isinstance(v, list):
        out = []
        for x in v:
            out.extend(_flat(x))
        return out
    return [v]


class JsonReader(object):
    """The original test format; loads the whole (small) file."""

    def __init__(self, path):
        with open(path, encoding="utf-8") as f:
            self.d = dict((k, _flat(v)) for k, v in json.load(f).items())

    def names(self):
        return sorted(self.d)

    def dtype(self, name):
        return "JSON"

    def shape(self, name):
        return [len(self.d[name])]

    def read(self, name):
        return list(self.d[name])


def open_checkpoint(path):
    p = path.lower()
    if p.endswith(".safetensors"):
        return SafetensorsReader(path)
    if p.endswith(".npz"):
        return NpzReader(path)
    if p.endswith(".json"):
        return JsonReader(path)
    raise LoaderError("unknown checkpoint format: %s (.safetensors, .npz, .json)" % path)


# -- writers, for tests ------------------------------------------------------

def write_safetensors(path, tensors, metadata=None):
    """tensors: {name: (dtype, shape, flat values)}."""
    hdr, blobs, off = {}, [], 0
    for k in sorted(tensors):
        dtype, shape, vals = tensors[k]
        raw = encode(vals, dtype)
        hdr[k] = {"dtype": dtype, "shape": list(shape), "data_offsets": [off, off + len(raw)]}
        blobs.append(raw)
        off += len(raw)
    if metadata:
        hdr["__metadata__"] = metadata
    h = json.dumps(hdr, separators=(",", ":")).encode("utf-8")
    h += b" " * (-len(h) % 8)
    with open(path, "wb") as f:
        f.write(struct.pack("<Q", len(h)) + h)
        for b in blobs:
            f.write(b)


def npy_bytes(dtype, shape, vals):
    if dtype not in DESCR_NPY:
        raise LoaderError("npy writer: dtype %s not supported" % dtype)
    d = "{'descr': '%s', 'fortran_order': False, 'shape': (%s), }" % (
        DESCR_NPY[dtype], "".join("%d, " % s for s in shape) if len(shape) != 1 else "%d," % shape[0])
    pad = 64 - (10 + len(d) + 1) % 64
    d = (d + " " * pad + "\n").encode("latin1")
    return NPY_MAGIC + bytes([1, 0]) + struct.pack("<H", len(d)) + d + encode(vals, dtype)


def write_npz(path, tensors, compressed=False):
    """tensors: {name: (dtype, shape, flat values)}."""
    mode = zipfile.ZIP_DEFLATED if compressed else zipfile.ZIP_STORED
    with zipfile.ZipFile(path, "w", mode) as z:
        for k in sorted(tensors):
            z.writestr(k + ".npy", npy_bytes(*tensors[k]))
