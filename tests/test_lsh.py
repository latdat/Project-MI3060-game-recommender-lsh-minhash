import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.MinHash import MinHash
from core.LSH_Engine import LSH_Engine
from models.User import User

def test_lsh_initialization():
    mh = MinHash(num_hashes=10)
    lsh = LSH_Engine(num_bands=5, rows_per_band=2, minhash=mh)
    assert lsh.num_bands == 5
    assert lsh.rows_per_band == 2

def test_lsh_indexing_and_candidates():
    # Setup mock users
    u1 = User("user1")
    u1.add_item("item1")
    u1.add_item("item2")
    
    u2 = User("user2")
    u2.add_item("item1")
    u2.add_item("item2")
    
    u3 = User("user3")
    u3.add_item("item3")
    u3.add_item("item4")
    
    user_index = {"user1": u1, "user2": u2, "user3": u3}
    
    mh = MinHash(num_hashes=10)
    mh.build_signatures(user_index)
    
    lsh = LSH_Engine(num_bands=5, rows_per_band=2, minhash=mh)
    lsh.build_index(user_index)
    
    candidates_for_u1 = lsh.get_candidates("user1")
    
    # user2 should likely be a candidate for user1 since they have identical items
    assert "user2" in candidates_for_u1
    assert "user1" not in candidates_for_u1 # Should not return itself
