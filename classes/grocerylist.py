from operator import itemgetter

# contains and deals with, essentially, the wunderlist and its ordering
# so it just knows ingredient lists, ingredient IDs (from wunderlist). It goes to the groceryStore to find out which
# category an ingredient is part of
class groceryList:

    #setup and populate the grocery_list[] (wunderlist_item_id, category_order, item_name)
    def __init__(self, wunderlist_list_id, wunderpy_wrapper):
        self.wunderlist_list_id = wunderlist_list_id
        self.wp = wunderpy_wrapper

        self.grocery_list = [] # (wunderlist_item_id, category_order, item_name)
        self.wunderlist_tasks = []

        #populate self.grocery_list
        self.get_tasks()

    def get_tasks(self):
        self.wunderlist_tasks = self.wp.get_tasks(self.wunderlist_list_id)

        self.grocery_list = []  # reset and rebuild.

        # now we create the initial grocery_list
        for element in self.wunderlist_tasks:
            self.grocery_list.append([element['id'], None, element['title']])

    # grabs category for an element (actually their order, via implicit argument to grocery_store) by item name
    def get_and_fix_category_for_element(self, element, grocery_store):
        return grocery_store.get_and_fix_category_for_ingredient(element[2])

    def get_category_for_element(self, element, grocery_store):
        category_id_col = 2  # category id we want returned is the cat order, not cat id.

        category = grocery_store.get_category_for_ingredient(element[2])

        if category is None:
            cat_id = None
        else:
            cat_id = category[category_id_col]

        return cat_id

    #gets the categories for each element in grocery list via get_category_for_element
    def get_categories(self, grocery_store):
        for index, element in enumerate(self.grocery_list):
            self.grocery_list[index][1] = self.get_category_for_element(element, grocery_store)

    def set_category_for_item(self,item,category):
        for index, element in enumerate(self.grocery_list):
            if element[2] == item:
                self.grocery_list[index][1] = category


    # order self.grocery_list based on category order
    # local order doesn't upload re-ordering to wonderlist
    def reorder_list(self, local_only=False):

        self.grocery_list.sort(key=itemgetter(1))  # itemgetter tells python which key to use to sort on. in this case category_order.
        if local_only is not True:
            self.wp.reorder_list(self.wunderlist_list_id, [i[0] for i in self.grocery_list])

    def get_next_new_ingredient(self):
        new_ingredients = [e for e in self.grocery_list if e[1] == None]

        if len(new_ingredients) > 0:
            return new_ingredients[0]
        else:
            return None
