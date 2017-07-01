from classes.grocerystore import groceryStore
from classes.grocerystore import groceryIngredientSetup


# TODO write an object to test and check results :)

zehrs_setup = groceryIngredientSetup('./data/store_order_zehrs.csv')
zehrs_setup.load_ingredients_to_list()

zehrs = groceryStore('./data/store_order_zehrs.csv')
# zehrs.load_category_order()  # run as part of init.
zehrs.load_ingredients()
# zehrs.add_ingredient_to_category("drain catcher",9)
zehrs.get_category_for_ingredient("asdf")


print('done')
