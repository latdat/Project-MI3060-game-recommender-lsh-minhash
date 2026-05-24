import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.MinHash import MinHash
from models.User import User

def test_minhash_initialization():
    mh = MinHash(num_hashes=50)
    assert mh.num_hashes == 50
    assert len(mh.hash_funcs) == 50

def test_minhash_signature_generation():
    # Setup mock users
    u1 = User("user1")
    u1.add_item("item1")
    u1.add_item("item2")
    
    u2 = User("user2")
    u2.add_item("item2")
    u2.add_item("item3")
    
    user_index = {"user1": u1, "user2": u2}
    
    mh = MinHash(num_hashes=10)
    mh.build_signatures(user_index)
    
    assert "user1" in mh.signatures
    assert "user2" in mh.signatures
    assert len(mh.signatures["user1"]) == 10
    assert len(mh.signatures["user2"]) == 10
