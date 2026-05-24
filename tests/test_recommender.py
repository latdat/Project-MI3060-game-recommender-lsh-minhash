import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.Recommender import Recommender
from models.User import User
from models.Item import Item

def test_recommender_cold_start():
    u1 = User("user1")
    u1.add_item("item1", 5.0)
    
    # user2 is cold start because they have less than MIN_INTERACTION (3)
    u2 = User("user2")
    u2.add_item("item2", 4.0)
    
    item1 = Item("item1")
    item1.add_interaction("user1", 5.0)
    
    item2 = Item("item2")
    item2.add_interaction("user2", 4.0)
    
    user_index = {"user1": u1, "user2": u2}
    item_index = {"item1": item1, "item2": item2}
    
    rec = Recommender(user_index, item_index, num_hashes=10, num_bands=5, rows_per_band=2)
    
    assert rec.is_cold_start("user2") == True
    
    # Recommendations for cold start user should fallback to popular items
    recommendations = rec.recommend("user2", top_k=2)
    assert len(recommendations) > 0

def test_recommender_recommendation():
    u1 = User("user1")
    u1.add_item("item1", 5.0)
    u1.add_item("item2", 4.0)
    u1.add_item("item3", 4.0)
    
    u2 = User("user2")
    u2.add_item("item1", 5.0)
    u2.add_item("item2", 4.0)
    u2.add_item("item4", 5.0)
    
    item1 = Item("item1")
    item2 = Item("item2")
    item3 = Item("item3")
    item4 = Item("item4")
    
    user_index = {"user1": u1, "user2": u2}
    item_index = {"item1": item1, "item2": item2, "item3": item3, "item4": item4}
    
    rec = Recommender(user_index, item_index, num_hashes=10, num_bands=5, rows_per_band=2)
    
    assert rec.is_cold_start("user1") == False
    
    recommendations = rec.recommend("user1", top_k=5)
    # user1 and user2 are similar, so item4 should be recommended to user1
    rec_items = [asin for asin, score in recommendations]
    assert "item4" in rec_items
