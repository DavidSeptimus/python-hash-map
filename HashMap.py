from typing import List

from Profiler import profile

INITIAL_BUCKET_COUNT = 16
DEFAULT_LOAD_FACTOR = .75


class HashMap:

    def __init__(self):
        self.bucket_count = INITIAL_BUCKET_COUNT
        self.resize_threshold = INITIAL_BUCKET_COUNT
        self.load_factor = DEFAULT_LOAD_FACTOR
        self.table: List[HashMap.NodeEntry] = [None] * self.bucket_count
        self.__size = 0

    def get(self, key):
        index = self.index(self.bucket_count, hash(key))
        entry = self.__find_at(index, key)
        return entry.value if entry is not None else None

    def __find_at(self, index, key):
        entry: HashMap.NodeEntry = self.table[index]
        if entry is not None:
            if entry.key == key:
                return entry

            while entry.next is not None:
                entry = entry.next
                if entry.key == key:
                    return entry

    # returns old value or none
    def put(self, key, value, only_if_absent=False):
        hash_code = hash(key)
        index = self.index(self.bucket_count, hash_code)
        return self.__put_val(index, hash_code, key, value, only_if_absent)

    # returns new val or none
    def compute(self, key, func, only_if_absent=False):
        hash_code = hash(key)
        index = self.index(self.bucket_count, hash_code)
        entry = self.__find_at(index, key)
        if entry is None:
            value = func(key, None)
            self.__put_val(index, hash_code, key, value)
            return value
        elif only_if_absent is False:
            value = entry.value = func(key, entry.value)
            return value
        else:
            return entry.value

    def __put_val(self, index, hash_code, key, value, only_if_absent=False):
        entry = self.table[index]
        if entry is None:
            self.table[index] = HashMap.NodeEntry(hash_code, key, value)
        else:
            # We can track depth and convert to/from a TreeNode implementation
            # when the number of elements in a bucket reaches a given threshold.
            last_visited = entry
            while entry is not None:
                if entry.key == key:
                    # required for put_if_absent functionality
                    old_value = entry.value
                    if only_if_absent is False:
                        entry.value = value
                    return old_value
                last_visited = entry
                entry = entry.next
            last_visited.next = HashMap.NodeEntry(hash_code, key, value)
        self.__size += 1
        if self.__size >= self.resize_threshold:
            self.grow()

    # returns previous value for key or None if not present
    def remove(self, key, value=None, match_value=False):
        entry: HashMap.Entry = self.__remove_entry(hash(key), key, value, match_value)
        return entry.value if entry is not None else None

    def __remove_entry(self, hash_code, key, value, match_value=False):
        index = self.index(self.bucket_count, hash_code)
        entry = self.table[index]
        if entry is not None and entry.key == key and (not match_value or value == entry.value):
            self.table[index] = entry.next
            self.__size -= 1
        elif entry is not None:
            temp = entry
            while entry is not None:
                if entry.key == key and (match_value is False or value == entry.value):
                    temp.next = entry.next
                    self.__size -= 1
                    break
                elif entry is not None:
                    temp = entry
                    entry = entry.next
        return entry if entry is not None and entry.key == key else None

    def grow(self):
        print('growing...')
        new_table_size = len(self.table) * 2
        new_table = [None] * new_table_size
        for i in range(0, self.bucket_count):
            entry = self.table[i]
            if entry is None:
                continue
            self.table[i] = None
            if entry.next is None:
                new_table[self.index(new_table_size, entry.hash_code)] = entry
                continue
            # elif handle treenode split
            # split NodeEntry buckets in half with upper/lower
            low_head = low_tail = high_head = high_tail = None
            while entry is not None:
                # extracts lower half of a bucket's nodes
                if entry.hash_code & self.bucket_count == 0:
                    if low_tail is None:
                        low_head = entry
                    else:
                        low_tail.next = entry
                    low_tail = entry
                # extracts upper half of a bucket's nodes
                else:
                    if high_tail is None:
                        high_head = entry
                    else:
                        high_tail.next = entry
                    high_tail = entry
                entry = entry.next
            if low_tail is not None:
                low_tail.next = None
                new_table[i] = low_head
            if high_tail is not None:
                high_tail.next = None
                new_table[i + self.bucket_count] = high_head
        self.resize_threshold = new_table_size * self.load_factor
        self.table = new_table
        self.bucket_count = new_table_size

    def __len__(self):
        return self.__size

    @staticmethod
    def index(table_size, hash_code):
        return hash_code & (table_size - 1)

    def __str__(self):
        return ', '.join(filter(lambda e: e != 'None', (map(str, self.table))))

    # Entry base class -- implementation of nesting is left to subclasses (e.g. NodeEntry -- implemented,
    # TreeEntry -- not implemented)
    class Entry:

        def __init__(self, hash_code, key, value):
            self.hash_code = hash_code
            self.key = key
            self.value = value

        def __eq__(self, other):
            return self.hash_code == other.hash_code and self.value == other.value and self.key == other.key

        def __str__(self):
            return f'[{self.key}={self.value}]'

    # Entry implementation using a singly linked list structure
    class NodeEntry(Entry):

        def __init__(self, hash_code, key, value):
            super().__init__(hash_code, key, value)
            self.next = None

        def __str__(self):
            val = super().__str__()
            return val if self.next is None else ", ".join([val, str(self.next)])
