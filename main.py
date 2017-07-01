# from openpyxl import Workbook #see https://openpyxl.readthedocs.org/en/2.3.4/
import openpyxl

# Import the recipeList and recipe objects
from classes import recipes
from classes import grocerystore
from classes import grocerylist

from classes import wunderpy_wrapper
wp = wunderpy_wrapper.wunderpy_wrapper()


if __name__ == "__main__":
    action = None
    while (action is None):
        action = input("[A]dd a recipe or [S]ort grocery list? ([Q] to quit): ").lower()
        action = action[0]
        if all([action is not 'a', action is not 's', action is not 'q']):
            action = None

    if action == 'a':

        # Load the recipe workbook and get a new list
        wb = openpyxl.load_workbook('recipes.xlsm')

        recipeList = recipes.RecipeList(wb['TOC'])
        recipeList.getRecipeList()
        recipeName = recipeList.pickRecipeNameFromList()

        newRecipe = recipes.Recipe(recipeName, wb)
        newRecipe.getIngredients()

        newRecipe.addMealToWunderlist(wp.WUNDERLIST_MEALS, wp.client)
        newRecipe.addListToWunderlist(wp.WUNDERLIST_GROCERY,wp.client)

    elif action == 's':

        # Re-order the grocery-list based on zehrs
        grocery_store = grocerystore.groceryStore('./data/store_order_zehrs.csv')  # use the default zehrs store; good enough

        groceries = grocerylist.groceryList(wp.WUNDERLIST_GROCERY, wp)
        groceries.get_tasks()

        groceries.get_categories(grocery_store)
        groceries.reorder_list()

    if action is not 'q':
        input('Press any key to quit.')