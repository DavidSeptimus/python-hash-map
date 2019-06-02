# Python HashMap Implementation

### Running the Test Suite From The Command Line
1. Navigate to the HashMap project Directory.
2. Run the following command:
```
pytest HashMap_pytest.py
```

### Dependencies
* Python 3.6.0
* pytest 4.6.2 (`pip install -U pytest`)

# Module Documentation

## HashMap
```python
HashMap(self, load_factor=0.75)
```

HashMap implementation using a singly linked list entry implementation (NodeEntry) inspired by the JDK's HashMap.

The running time of get() and put() operations is dependent on the depth of the bucket associated with a key's hash.
For well distributed hashes, depth should be small. This property can be improved by using a TreeEntry
implementation for suitably large buckets (the JDK's HashMap treeifies buckets
at a depth of 8 if the table has 64+ buckets).

The put() operation is also impacted by resize operations triggered by the HashMap's len() hitting its
resize threshold (generally bucket_count * load_factor).

### get
```python
HashMap.get(self, key)
```

Retrieves the value for the supplied key from the HashMap

**param:** key: The key whose value is being retrieved.  
**return:** The value associated with the supplied key.  

### put
```python
HashMap.put(self, key, value, only_if_absent=False)
```

Inserts a key, value mapping into the HashMap.

**param:** key: The key to be inserted.  
**param:** value: The value to be inserted.  
**param:** only_if_absent: if True, the value will only be updated if the key does not already exist in the HashMap.  
**return:** The previous value for the given key or None.  

### compute
```python
HashMap.compute(self, key, func, only_if_absent=False)
```

Computes the value associated with a given key based on its existing value using the supplied lambda.

**param:** key  
**param:** func: The function that will be applied to derive the new value (signature k,v: v).  
**param:** only_if_absent: If True, func will only be applied when the key does not already exist in the HashMap.  
**return:** The newly computed value or None.  


### remove
```python
HashMap.remove(self, key, value=None, match_value=False)
```

Removes the key/value mapping from the table for the supplied key.

**param:** key: The key to remove.  
**param:** value: The value to remove (only applicable when match_value=True).  
**param:** match_value: If true, the key/value mapping will only be removed if its value matches the supplied value.  
**return:** The removed value or None.  

### Entry
```python
HashMap.Entry(self, hash_code, key, value)
```

Entry base class -- implementation of nesting is left to subclasses (e.g. NodeEntry -- implemented,
TreeEntry -- not implemented)

### NodeEntry
```python
HashMap.NodeEntry(self, hash_code, key, value)
```

Entry implementation using a singly linked list structure.

