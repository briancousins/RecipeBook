from classes import wunderpy_wrapper
from classes import grocerylist
from classes import grocerystore

wp = wunderpy_wrapper.wunderpy_wrapper('../data/tokens.csv')
obj = wp.get_task_positions_obj(wp.WUNDERLIST_GROCERY)

grocery_store = grocerystore.groceryStore('../data/store_order_zehrs.csv', '../data/ingredient_categories.csv') # use the default zehrs store; good enough

groceries = grocerylist.groceryList(wp.WUNDERLIST_GROCERY, wp)
groceries.get_tasks()

groceries.get_category_for_element(groceries.grocery_list[0], grocery_store)
groceries.get_categories(grocery_store)
groceries.reorder_list(wp)
# wp.update_list_order(groceries.wunderlist_order_obj)

# TODO check reloading of a list when you enter the right sheet
# TODO sort by cat order value, not cat id.

print('done')