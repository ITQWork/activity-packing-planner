from app.models.models import Item, Category
from app.schemas.schemas import ItemCreate, CategoryCreate

def test_item_model():
    item = Item(name="Tent", unit_weight=3000.5, category_id=1)
    assert item.name == "Tent"
    assert item.unit_weight == 3000.5
    assert item.category_id == 1

def test_item_schema():
    item_in = ItemCreate(name="Tent", unit_weight=3000.5, category_id=1)
    assert item_in.name == "Tent"
    assert item_in.unit_weight == 3000.5
    assert item_in.category_id == 1

def test_category_model():
    category = Category(name="Shelter")
    assert category.name == "Shelter"

def test_category_schema():
    category_in = CategoryCreate(name="Shelter")
    assert category_in.name == "Shelter"
