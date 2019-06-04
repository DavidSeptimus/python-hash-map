from typing import List

INITIAL_BUCKET_COUNT = 16
DEFAULT_LOAD_FACTOR = .75


class HashMap:
    """
    HashMap implementation using a singly linked list entry implementation (NodeEntry) inspired by the JDK's HashMap.

    The running time of get() and put() operations is dependent on the depth of the bucket associated with a key's hash.
    For well distributed hashes, depth should be small. This property can be improved by using a TreeEntry
    implementation for suitably large buckets (the JDK's HashMap treeifies buckets
    at a depth of 8 if the table has 64+ buckets).

    The put() operation is also impacted by resize operations triggered by the HashMap's len() hitting its
    resize threshold (generally bucket_count * load_factor).
    """

    def __init__(self, load_factor=DEFAULT_LOAD_FACTOR):
        """
        Constructs a new HashMap instance.

        :param load_factor: The HashMap size to table length ratio used to determine when the HashMap will resize its
                            internal bucket array. Defaults to DEFAULT_LOAD_FACTOR.
        """
        self._bucket_count = INITIAL_BUCKET_COUNT
        self._resize_threshold = INITIAL_BUCKET_COUNT
        self.load_factor = load_factor
        self._table: List[HashMap.NodeEntry] = [None] * self._bucket_count
        self._size = 0
        # used to invalidate iterators when the table's key/bucket assignments are modified
        self._modification_count = 0

    def get(self, key):
        """
        Retrieves the value for the supplied key from the HashMap

        :param key: The key whose value is being retrieved.
        :return: The value associated with the supplied key.
        """
        index = self.__index(self._bucket_count, hash(key))
        entry = self.__find_at(index, key)
        return entry.value if entry is not None else None

    def __find_at(self, index, key):
        entry: HashMap.NodeEntry = self._table[index]
        if entry is not None:
            if entry.key == key:
                return entry

            while entry.next is not None:
                entry = entry.next
                if entry.key == key:
                    return entry

    def put(self, key, value, only_if_absent=False):
        """
        Inserts a key, value mapping into the HashMap.

        :param key: The key to be inserted.
        :param value: The value to be inserted.
        :param only_if_absent: if True, the value will only be updated if the key does not already exist in the HashMap.
        :return: The previous value for the given key or None.
        """
        hash_code = hash(key)
        index = self.__index(self._bucket_count, hash_code)
        return self.__put_val(index, hash_code, key, value, only_if_absent)

    def compute(self, key, func, only_if_absent=False):
        """
        Computes the value associated with a given key based on its existing value using the supplied lambda.

        :param key
        :param func: The function that will be applied to derive the new value (signature k,v: v).
        :param only_if_absent: If True, func will only be applied when the key does not already exist in the HashMap.
        :return: The newly computed value or None.

         """
        hash_code = hash(key)
        index = self.__index(self._bucket_count, hash_code)
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
        entry = self._table[index]
        if entry is None:
            self._table[index] = HashMap.NodeEntry(hash_code, key, value)
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
        self._size += 1
        self._modification_count += 1
        if self._size >= self._resize_threshold:
            self.__grow()

    def remove(self, key, value=None, match_value=False):
        """
        Removes the key/value mapping from the table for the supplied key.

        :param key: The key to remove.
        :param value: The value to remove (only applicable when match_value=True).
        :param match_value: If true, the key/value mapping will only be removed if its value matches the supplied value.
        :return: The removed value or None.
        """
        entry: HashMap.Entry = self.__remove_entry(hash(key), key, value, match_value)
        return entry.value if entry is not None else None

    def __remove_entry(self, hash_code, key, value, match_value=False):
        index = self.__index(self._bucket_count, hash_code)
        entry = self._table[index]
        if entry is not None and entry.key == key and (not match_value or value == entry.value):
            self._table[index] = entry.next
            self._size -= 1
            self._modification_count += 1
        elif entry is not None:
            temp = entry
            while entry is not None:
                if entry.key == key and (match_value is False or value == entry.value):
                    temp.next = entry.next
                    self._size -= 1
                    self._modification_count += 1
                    break
                elif entry is not None:
                    temp = entry
                    entry = entry.next
        return entry if entry is not None and entry.key == key else None

    def __grow(self):
        """
        Grows the table by a factor of 2 and redistributes entries.

        Each entry will either remain in the same bucket (i) or will be moved to the bucket at i + new_table_size.
        """
        new_table_size = len(self._table) * 2
        new_table = [None] * new_table_size
        for i in range(0, self._bucket_count):
            entry = self._table[i]
            if entry is None:
                continue
            self._table[i] = None
            if entry.next is None:
                new_table[self.__index(new_table_size, entry.hash_code)] = entry
                continue
            # split NodeEntry buckets in half with upper/lower.
            low_head = low_tail = high_head = high_tail = None
            while entry is not None:
                # extracts lower half of a bucket's nodes (will be reinserted at the same index, i)
                if entry.hash_code & self._bucket_count == 0:
                    if low_tail is None:
                        low_head = entry
                    else:
                        low_tail.next = entry
                    low_tail = entry
                # extracts upper half of a bucket's nodes (will be reinserted at i + old bucket_count)
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
                new_table[i + self._bucket_count] = high_head
        self._resize_threshold = new_table_size * self.load_factor
        self._table = new_table
        self._bucket_count = new_table_size

    def __len__(self):
        return self._size

    @staticmethod
    def __index(table_size, hash_code):
        return hash_code & (table_size - 1)

    def __str__(self):
        return ', '.join(filter(lambda e: e != 'None', (map(str, self._table))))

    def __iter__(self):
        return HashMap.EntrySet.EntryIterator(self)

    def contains(self, key):
        index = self.__index(self._bucket_count, hash(key))
        entry = self.__find_at(index, key)
        return entry is not None

    def for_each(self, func):
        if self._size < 1:
            return
        emc = self._modification_count
        for entry in self._table:
            if entry is not None:
                func(entry.key, entry.value)
                while entry.next is not None:
                    entry = entry.next
                    func(entry)
        if emc < self._modification_count:
            raise Exception('Underlying HashMap instance has been modified!')

    def clear(self):
        for i in range(0, self._bucket_count):
            self._table[i] = None
            self._size = 0
            self._modification_count += 1

    def entry_set(self):
        return HashMap.EntrySet(self)

    class Entry:
        """
        Entry base class -- implementation of nesting is left to subclasses (e.g. NodeEntry -- implemented,
        TreeEntry -- not implemented)
        """

        def __init__(self, hash_code, key, value):
            self.hash_code = hash_code
            self.key = key
            self.value = value

        def __eq__(self, other):
            return self.hash_code == other.hash_code and self.value == other.value and self.key == other.key

        def __str__(self):
            return f'[{self.key}={self.value}]'

    class NodeEntry(Entry):
        """
        Entry implementation using a singly linked list structure.
        """

        def __init__(self, hash_code, key, value):
            super().__init__(hash_code, key, value)
            self.next = None

        def __str__(self):
            val = super().__str__()
            return val if self.next is None else ", ".join([val, str(self.next)])

    class EntrySet:

        def __init__(self, owner):
            self.owner = owner

        def __iter__(self):
            return HashMap.EntrySet.EntryIterator(self.owner)

        def contains(self, entry):
            return self.owner.__find_entry(entry.hash, entry.key)

        def clear(self):
            self.owner.clear()

        def remove(self, entry):
            self.owner.__remove_entry(entry.hash_code, entry.key)

        def for_each(self, func):
            expected_mod_count = self.owner._modification_count
            for entry in self:
                func(entry)
                if expected_mod_count < self.owner._modification_count:
                    raise Exception('Underlying HashMap instance has been modified!')

        def __len__(self):
            return self.owner._size

        class EntryIterator:

            def __init__(self, owner):
                self.owner = owner
                self.index = -1
                self.current = None
                self.__expected_mod_count = owner._modification_count

            def __next__(self):
                if self.__expected_mod_count < self.owner._modification_count:
                    raise Exception('Underlying HashMap instance has been modified!')
                if self.current is None or self.current.next is None:
                    self.index = self.__next_populated_index()
                    self.current = self.owner._table[self.index]
                elif self.current.next:
                    self.current = self.current.next
                return self.current

            def __next_populated_index(self):
                index = self.index + 1
                table = self.owner._table
                table_len = self.owner._bucket_count
                while 0 <= index < table_len and table[index] is None:
                    index += 1
                if index is table_len:
                    raise StopIteration()
                return index
