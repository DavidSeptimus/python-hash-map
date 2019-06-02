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

    # returns old value or none
    def put(self, key, value, only_if_absent=False):
        return self.__put_val(hash(key), key, value, only_if_absent)

    # returns new val or none
    def compute(self, key, func, only_if_absent=False):
        hash_code = hash(key)
        entry = self.__find_entry(hash_code, key)
        if entry is None:
            value = func(key, None)
            self.__put_val(hash_code, key, value)
            return value
        elif only_if_absent is False:
            value = entry.value = func(key, entry.value)
            return value
        else:
            return entry.value

    def __put_val(self, hash_code, key, value, only_if_absent=False):
        index = self.index(self.bucket_count, hash_code)
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
            last_visited.append(HashMap.NodeEntry(hash_code, key, value))
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

        if self.__size < self.resize_threshold / 2:
            self.shrink()
        return entry if entry is not None and entry.key == key else None

    def get(self, key):
        entry = self.__find_entry(hash(key), key)
        return entry.value if entry is not None else None

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

    def __find_entry(self, hash_code, key):
        index = self.index(self.bucket_count, hash_code)
        entry: HashMap.NodeEntry = self.table[index]
        if entry is not None:
            if entry.key == key:
                return entry

            while entry.next is not None:
                entry = entry.next
                if entry.key == key:
                    return entry

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

        def append(self, tail):
            node = self
            while node.next is not None:
                if tail == self:
                    return  # prevents appending a duplicate
                node = node.next
            node.next = tail

    # class TreeEntry(NodeEntry):
    #
    #     def __init__(self, hash_code, key, value, next=None):
    #         super().__init__(hash_code, key, value)
    #         super().next = next
    #         self.parent: HashMap.TreeEntry = None  # maintains RBL link to parent
    #         self.left: HashMap.TreeEntry = None
    #         self.right: HashMap.TreeEntry = None
    #         self.red = False
    #
    #     def root(self):
    #         root = self.parent
    #         while root is not None:
    #             root = root.parent
    #         return root
    #
    #     # finds node starting at root p for given hash_code and key
    #     def find(self, hash_code, key):
    #         p = self
    #         while p is not None:
    #             pl = p.left
    #             pr = p.right
    #             pk = p.key
    #             ph = p.hash_code
    #             if pk == key or (key is not None and key is pk):
    #                     return p
    #             elif ph < hash_code or p.left is None:
    #                 p = p.right
    #             elif ph > hash_code or p.right is None:
    #                 p = p.left
    #             else:
    #                 q = pr.find(hash_code, key)
    #                 if q is not None:
    #                     return q
    #                 else:
    #                     p = pl
    #         return None
    #
    #     # calls find from the root associated with the supplied key and hash_code
    #     def get_tree_node(self, hash_code, key):
    #         return (self.root() if self.parent is not None else self).find(hash_code, key)
    #
    #     def treeify(self, table):
    #         root = None
    #         current = self
    #         while current is not None:
    #             next_entry = current.next
    #             current.left = current.right = None
    #             # sets current as a black root when no root is present
    #             if root is None:
    #                 current.parent = None
    #                 current.red = False
    #                 root = current
    #             else:  # add red/black leaf
    #                 ch = current.hash_code
    #                 while True:
    #                     dir = 0  # default direction (as opposed to using a tie-breaker algorithm)
    #                     parent = root
    #                     ph = parent.hash_code
    #                     if ph > ch:
    #                         dir = -1  # left
    #                     if ph < ch:
    #                         dir = 1  # right
    #
    #                     cur_parent = parent
    #                     parent = current.left if dir <= 0 else current.right
    #                     if parent is None:
    #                         current.parent = cur_parent
    #                         if dir <= 0:
    #                             cur_parent.left = current
    #                         else:
    #                             cur_parent.right = current
    #                         root = self.balance_insertion(root, current)
    #                         break
    #             current = next_entry
    #         self.move_root_to_front(table, root)
