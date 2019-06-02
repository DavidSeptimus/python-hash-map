from HashMap import HashMap


class TestHashMap:

    def test_hash_map_get(self):
        mmap = HashMap()
        mmap.put("key", 1)
        mmap.put("ket2", 2)
        assert mmap.get("key") == 1
        assert mmap.get("ket2") == 2
        assert len(mmap) == 2

    def test_many_gets_and_removes(self):
        mmap = HashMap()
        x = 1
        while x <= 5000000:
        #    print(f'put{x}')
            mmap.put(f'key{x}', f'val{x}')
            # assert mmap.get(f'key{x}') is not None
            x += 1
        # assert len(mmap) is 32
        # t = 1
        # while t <= 32:
        #     assert mmap.get(f'key{t}') is not None
        #     assert mmap.get(f'key{t}') is not None
        #     t += 1
        # x -= 1
        # while x > 0:
        #     print(f'get{x}')
        #     assert mmap.get(f'key{x}') is not None
        #     mmap.remove(f'key{x}')
        #     x -= 1
        # assert len(mmap) is 0
    def test_compare_dict(self):
        m = dict()
        x = 1
        while x <= 5000000:
            #    print(f'put{x}')
            m[f'key{x}'] = f'val{x}'
            # assert mmap.get(f'key{x}') is not None
            x += 1
        print('done')

    def test_compute_replaces_existing_value_with_result_of_supplied_lambda(self):
        m = HashMap()
        m.put(1, 2)
        m.put(2, 3)
        m.compute(1, lambda k, v: k + v)
        m.compute(2, lambda k, v: k + v)
        assert m.get(1) == 3
        assert m.get(2) == 5
        assert len(m) == 2

    def test_compute_replaces_existing_value_with_result_of_supplied_lambda_without_affecting_len(self):
        m = HashMap()
        m.put(1, 2)
        m.put(2, 3)
        assert m.compute(1, lambda k, v: k + v) == 3
        assert m.get(1) == 3
        assert len(m) == 2

    def test_compute_if_absent_does_not_update_existing_value(self):
        m = HashMap()
        m.put(1, 2)
        assert m.compute(1, lambda k, v: 55, True) == 2
        assert m.compute(2, lambda k, v: 55, True) == 55

    def test_compute_inserts_new_entry_when_key_is_not_present(self):
        m = HashMap()
        m.compute(1, lambda k, v: k)
        assert m.get(1) == 1
        assert len(m) == 1

    def test_put_if_absent_does_not_replace_value_if_key_already_exists(self):
        key = 1
        m = HashMap()
        assert m.put(key, 1, True) is None
        assert m.get(key) == 1
        assert m.put(key, 2) == 1
        assert m.get(key) == 2
        assert m.put(key, 3, True) == 2
        assert m.get(key) == 2

    def test_remove_removes_and_returns_value_of_entry_with_corresponding_key(self):
        m = HashMap()
        m.put(1, 5)
        m.put(2, 3)

        assert len(m) == 2
        assert m.remove(1) == 5
        assert len(m) == 1
        assert m.remove(2) == 3
        assert len(m) == 0
        assert m.remove(44) is None

    def test_remove_only_removes_entry_with_matching_value_when_match_value_is_true(self):
        m = HashMap()
        m.put(1, 45)
        assert m.remove(1, 22, True) is None
        assert len(m) == 1
        assert m.remove(1) == 45
        assert len(m) == 0
