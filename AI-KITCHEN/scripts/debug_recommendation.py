import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app
from backend.utils.database import db
from backend.models.kitchen import Kitchen
from backend.models.menu import MenuItem
from backend.models.sales import Sales
from datetime import date, timedelta

with app.app_context():
    db.drop_all()
    db.create_all()

    kitchen = Kitchen(name='Debug Kitchen')
    db.session.add(kitchen)
    db.session.commit()
    kitchen_id = kitchen.id

    menu = MenuItem(kitchen_id=kitchen_id, name='Debug Meal', serving_unit='servings', cost_per_serving=50)
    db.session.add(menu)
    db.session.commit()
    meal_id = menu.id

    today = date.today()
    for i in range(9):
        s = Sales(
            kitchen_id=kitchen_id,
            menu_item_id=meal_id,
            sale_date=(today - timedelta(days=(9-i))),
            quantity_sold=20 + i,
            revenue=(20 + i) * 50
        )
        db.session.add(s)
    db.session.commit()

with app.test_client() as client:
    res = client.post('/api/recommendation/', json={'kitchen_id': kitchen_id, 'menu_item_id': meal_id})
    print('STATUS', res.status_code)
    try:
        print('JSON:', res.get_json())
    except Exception as e:
        print('Response data:', res.data)
