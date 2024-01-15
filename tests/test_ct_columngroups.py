# test_ct_columngroups.py

import collections
import pandas as pd
import bifi_outboard as bob
import captest as ct

def test_group_columns_generic():
    t1 = [
        collections.OrderedDict([
            ('warm', ['red', 'orange', 'yellow'])
            , ('cool', ['green', 'blue'])])
        , collections.OrderedDict([
            ('large', ['bulky', 'massive'])
            , ('small', ['compact', 'tiny'])])]
    d1 = pd.DataFrame(
        {
            'yellow_tiny': [1, 2, 3]
            , 'green_bulky': [4, 5, 6]
            , 'red_compact': [7, 8, 9]}
        , index=pd.Index(['a', 'b', 'c'], name='Timestamp'))
    ans = bob.pvcaptest.columngroups.group_columns_generic(
        data=d1
        , type_defs=t1)
    assert list(ans.keys()) == ['cool_large', 'warm_small']
    assert ans['warm_small'] == ['red_compact', 'yellow_tiny']
