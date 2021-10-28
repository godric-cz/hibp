import functools
import hashlib
import os


class Search(object):
    def __init__(self, index_filename, passwords_filename):
        self.index = Index(index_filename, os.path.getsize(passwords_filename) // 21 - 1)
        self.passwords = Passwords(passwords_filename)

    def __enter__(self):
        self.passwords.__enter__()
        return self

    def __exit__(self, _, __, ___):
        self.passwords.__exit__(0, 0, 0)

    def search(self, hsh):
        prefix = hsh[:5]

        boundaries = self.index.get_boundaries(prefix)

        chunk = Chunk(self.passwords, prefix, boundaries[0], boundaries[1])
        return chunk.search(hsh)

    def list(self, prefix):
        boundaries = self.index.get_boundaries(prefix)
        return self.passwords.list(boundaries[0], boundaries[1])


class Index(object):
    def __init__(self, filename, max_hi):
        self.max_hi = max_hi
        with open(filename, 'rb') as f:
            self.data = f.read()

    def get_boundaries(self, prefix):
        """ Return first and last index belonging to given prefix. """
        assert len(prefix) == 5

        pre = int(prefix, 16)
        lo = self._get_item_no(pre)

        next_pre = pre + 1
        hi = self._get_item_no(next_pre) # TODO file end

        return (lo, hi - 1)

    def _get_item_no(self, prefix_int):
        """ Return item number of first item with given prefix. """
        i = prefix_int * 4
        if i >= len(self.data):
            return self.max_hi + 1

        return int.from_bytes(self.data[i:i+4], byteorder='little')


class Chunk(object):
    def __init__(self, passwords, prefix, lo, hi):
        self.passwords = passwords
        self.prefix = prefix
        self.lo = lo
        self.hi = hi

    def __getitem__(self, i):
        if i == self.lo - 1:
            return int(self.prefix + ('0' * 35), 16)
        elif i == self.hi + 1:
            return int(self.prefix + ('f' * 35), 16)
        else:
            return self.passwords[i]

    def search(self, key):
        i = interpolation_search(self, int(key, 16), self.lo - 1, self.hi + 1)
        if i == None:
            return 0

        # handle fake segment boundaries
        if i == self.lo - 1 or i == self.hi + 1:
            return 0

        return self.passwords.get(i)[1]


class Passwords(object):
    def __init__(self, filename):
        self.filename = filename
        self.item_length = 21
        self.len = os.path.getsize(filename) // self.item_length

    def __enter__(self):
        self.f = open(self.filename, 'rb', buffering=4096)
        self.reader = Reader(self.f, 4096)
        return self

    def __exit__(self, _, __, ___):
        self.f.close()

    def __len__(self):
        return self.len

    def __getitem__(self, i):
        return int(self.get(i)[0], 16)

    @functools.lru_cache
    def get(self, i):
        pos = self.item_length * i
        item = self.reader.read(pos, self.item_length)
        hash_length = self.item_length - 1

        checksum = item[:hash_length].hex()
        occurences = item[hash_length]

        return (checksum, occurences)

    def list(self, lo, hi):
        hash_length = self.item_length - 1
        self.f.seek(lo * self.item_length)
        out = []

        for _ in range(hi - lo + 1):
            item = self.f.read(self.item_length)
            prefix = item[:hash_length].hex()[5:].upper()
            occurences = item[hash_length]
            out.append(f'{prefix}:{occurences}\n')

        return ''.join(out)


class Reader(object):
    def __init__(self, file, buffer_length):
        self.file = file
        self.buffer_length = buffer_length
        self.lo = -1
        self.hi = -1

    def read(self, pos, length):
        end = pos + length - 1

        if not self._contains(pos, end):
            self._prefetch(pos)

        self.file.seek(pos)
        return self.file.read(length)

    def _contains(self, lo, hi):
        return self.lo <= lo and hi <= self.hi

    def _prefetch(self, pos):
        self.lo = pos - self.buffer_length // 2
        self.lo = max(self.lo, 0)
        self.hi = self.lo + self.buffer_length - 1
        self.file.seek(self.lo)
        self.file.read(1)


def interpolation_search(haystack, needle, lo, hi):
    # lo = 0
    # hi = len(haystack) - 1

    while haystack[lo] != haystack[hi] and haystack[lo] <= needle <= haystack[hi]:
        needle_val_distance = needle - haystack[lo]
        key_distance = hi - lo
        val_distance = haystack[hi] - haystack[lo]
        mid = lo + needle_val_distance * key_distance // val_distance

        if needle == haystack[mid]:
            return mid
        elif needle < haystack[mid]:
            hi = mid - 1
        else:
            lo = mid + 1

    if needle == haystack[lo]:
        return lo

    return None


def sha1(s):
    return hashlib.sha1(s.encode('utf8')).digest().hex()
