from HashMap import HashMap


class TestHashMap:

    def test_get_returns_value_for_associated_key(self):
        m = HashMap()
        for n in range(0, 8):
            m.put(n, f'val{n}')
        for n in range(0, 8):
            assert m.get(n) == f'val{n}'

    def test_get_returns_value_for_supplied_key_after_resize(self):
        m = HashMap()
        for n in range(0, 40):
            m.put(f'key{n}', f'val{n}')
        for n in range(0, 40):
            assert m.get(f'key{n}') == f'val{n}'

    def test_len_increases_by_one_on_put_and_decreases_by_one_on_remove(self):
        m = HashMap()
        for n in range(0, 20):
            m.put(n, n)
            assert len(m) == n + 1
        for n in range(0, 20):
            m.remove(n)
            assert len(m) == 19 - n

    def test_put_inserts_entry_and_returns_previous_value(self):
        m = HashMap()
        assert m.put(1, 2) is None
        assert m.put(1, 3) == 2

    def test_remove_removes_entry_for_supplied_key_and_returns_associated_value(self):
        m = HashMap()
        m.put(1, 2)
        assert len(m) == 1
        assert m.remove(1) == 2
        assert m.get(1) is None
        assert len(m) == 0

    def test_remove_with_match_value_only_removes_entry_if_both_key_and_value_match_supplied_values(self):
        m = HashMap()
        m.put(1, 2)
        assert m.remove(1, 3, True) is None
        assert len(m) == 1
        assert m.remove(1, 2) == 2
        assert len(m) == 0

    def test_put_if_absent_does_not_replace_value_if_key_already_exists(self):
        key = 1
        m = HashMap()
        assert m.put(key, 1, True) is None
        assert m.get(key) == 1
        assert m.put(key, 2) == 1
        assert m.get(key) == 2
        assert m.put(key, 3, True) == 2
        assert m.get(key) == 2

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
