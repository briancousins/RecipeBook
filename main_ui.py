
#works in qtpy (since it's uniform for ptqy5 i think)
import sys
from qtpy import QtCore, QtGui, uic, QtWidgets
import openpyxl

from classes import grocerystore
from classes import grocerylist
from classes import recipes

from classes import wunderpy_wrapper
wp = wunderpy_wrapper.wunderpy_wrapper()

grocery_store = grocerystore.groceryStore('./data/store_order_zehrs.csv')
groceries = grocerylist.groceryList(wp.WUNDERLIST_GROCERY, wp)
groceries.get_categories(grocery_store)

# load the UI class objects
UiMainWindow, QtBaseClass = uic.loadUiType('./ui/recipeBookUI.ui')

# UI class definition
class GroceryAppUI(QtWidgets.QMainWindow, UiMainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        UiMainWindow.__init__(self)
        self.setupUi(self)

        self.recipe_book = None
        self.recipe_book_url = './data/recipes.xlsm'

        self.missing_ingredient = None  # assume the list is great. Will be set if it's not.

        # init pages (just do them all...)
        # self.initPage_missingCategory()
        # self.initPage_addRecipe()

        # now using auto naming convention
        # setup menubar
        # self.QActionSort_grocery_list.triggered.connect(self.on_QActionSort_grocery_list_triggered)
        # self.QActionAdd_recipe_to_list.triggered.connect(self.on_QActionAdd_recipe_to_list_triggered)

        self.on_QActionSort_grocery_list_triggered()

    # Menubar functions

    def on_QActionSort_grocery_list_triggered(self):
        groceries.get_tasks()  # pick up the tasks again for when you activate via menu
        self.initPage_missingCategory()  # best to re-init each time. List may have changed.
        self.stackedWidget.setCurrentWidget(self.pageMissingCategory)

    def on_QActionAdd_recipe_to_list_triggered(self):
        self.initPage_addRecipe()
        self.stackedWidget.setCurrentWidget(self.pageAddRecipe)

    # todo understand why ptqt fucks up and clicked() executes twice; now i need to use pressed. I swear I updated nothing.
    def on_QbuttonSelectCategory_pressed(self):
        # save the category to the grocerylist and the .csv file for future access
        self.set_category_for_item(add_permanently=True)

    def on_QbuttonSkipCategory_pressed(self):
        # allow the addition of a category in the grocery list without saving it to the .csv file
        self.set_category_for_item(add_permanently=False)

    # Missing category functions

    def initPage_missingCategory(self):

        # setup missing ingredient page:
        if self.QlistCategories.count() == 0:
            self.populate_categories()

        self.get_next_missing_ingredient()

        # done automatically due to good naming convention (hoorah)
        # if self.missing_ingredient is not None:
        #     self.QbuttonSelectCategory.clicked.connect(self.on_QbuttonSelectCategory_clicked)
        #     self.QbuttonSkipCategory.clicked.connect(self.on_QbuttonSkipCategory_clicked)

    # populate QlistCategories from grocery store
    def populate_categories(self):
        # this adds items and creates QListWidgetItem as you go; no secondary data; search?
        for cat in grocery_store.categories:

            thisItem = QtWidgets.QListWidgetItem(cat[1])  # grab the name.

            # read self.QlistCategories.item(<selected>).data(99)
            # id, name, order_id
            thisItem.setData(99, cat[0])
            thisItem.setData(98, cat[1])
            thisItem.setData(97, cat[2])

            self.QlistCategories.addItem(thisItem)

    # get the next missing ingredient and set the text box
    def get_next_missing_ingredient(self):
        self.missing_ingredient = groceries.get_next_new_ingredient()

        if self.missing_ingredient is None:
            groceries.reorder_list()
            self.set_missing_ingredient_text('List re-ordered.')
            self.QlastAction.setText('')

            self.QbuttonSelectCategory.setDisabled(True)
            self.QbuttonSkipCategory.setDisabled(True)

        else:
            self.set_missing_ingredient_text(self.missing_ingredient[2])

    # actually save & pull next ingredient.
    def set_category_for_item(self, add_permanently=True):
        ingred_cat_id = self.get_selected_cagetory(self.QlistCategories)

        update_str = ''

        if self.missing_ingredient is not None and ingred_cat_id is not None:
            ingred_order_id = grocery_store.get_category_order_from_id(ingred_cat_id)

            update_str = 'Added ' + self.missing_ingredient[2] + ' to ' + \
                         grocery_store.get_category_name_from_id(ingred_cat_id)

            # todo should have category order AND category stored together in groceries?
            groceries.set_category_for_item(self.missing_ingredient[2], ingred_order_id)

            if add_permanently is True:
                grocery_store.add_ingredient_to_category(self.missing_ingredient[2], ingred_cat_id)
                update_str += ' permanently'

            self.get_next_missing_ingredient()

        elif ingred_cat_id is None and self.missing_ingredient[2] is not None:
            update_str = 'Please select a category for ' + self.missing_ingredient[2]
        else:
            update_str = 'No missing ingredients. No action to take.'

        self.QlastAction.setText(update_str)

    # on set_category_for_item get the selectedItem() from QlistCategories and return sorting-value
    # Sorting options are id, name, order_id (see self.populate_categories)
    def get_selected_cagetory(self, Qlist):

        selectedItems = Qlist.selectedItems()
        selected_category_id = None

        if len(selectedItems) == 1:
            # selected_category = selectedItems[0].text()   # this is the category name
            selected_category_id = selectedItems[0].data(99)   # this is the category id
            # selected_category_order_id = selectedItems[0].data(97)  # this is the category id

        return selected_category_id

    # set the correct element to indicate what the next missing ingredient is
    def set_missing_ingredient_text(self, text):
        self.QtextMissing_ingredient.setText(text)


    ## Add recipe page functions

    def initPage_addRecipe(self):
        if self.QlistRecipes.count() == 0:
            self.populate_recipes()
        # self.QbuttonAddRecipe.clicked.connect(self.add_recipe)  # used autoconnect naming

    def populate_recipes(self):
        self.recipe_book = openpyxl.load_workbook(self.recipe_book_url)

        recipeList = recipes.RecipeList(self.recipe_book['TOC'])

        for index, recipe_name in enumerate(recipeList.getRecipeList()):
            thisItem = QtWidgets.QListWidgetItem(recipe_name)
            thisItem.setData(99, index)  # read self.QlistRecipes.item(<selected>).data(99)
            self.QlistRecipes.addItem(thisItem)

    def on_QbuttonAddRecipe_pressed(self):
        recipeName = self.QlistRecipes.selectedItems()[0].text()  # self.get_selected_cagetory(self.QlistRecipes, 'name')



        if recipeName is not None:
            newRecipe = recipes.Recipe(recipeName, self.recipe_book)
            newRecipe.getIngredients()
            newRecipe.addMealToWunderlist(wp.WUNDERLIST_MEALS, wp.client)
            newRecipe.addListToWunderlist(wp.WUNDERLIST_GROCERY, wp.client)


################
# main program
if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    window = GroceryAppUI()
    window.show()

    sys.exit(app.exec_())