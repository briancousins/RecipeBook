from operator import itemgetter

# contains and deals with, essentially, the wunderlist and its ordering
# so it just knows ingredient lists, ingredient IDs (from wunderlist). It goes to the groceryStore to find out which
# category an ingredient is part of
class groceryList:

    def __init__(self, wunderlist_list_id, wunderpy_wrapper):
        self.wunderlist_list_id = wunderlist_list_id
        self.wp = wunderpy_wrapper

        self.grocery_list = [] # (wunderlist_item_id, category_order, item_name)
        self.wunderlist_tasks = []
        # self.wunderlist_order_obj  = []

    def get_tasks(self):
        self.wunderlist_tasks = self.wp.get_tasks(self.wunderlist_list_id)

        self.grocery_list = []  # reset and rebuild.

        # now we create the initial grocery_list
        for element in self.wunderlist_tasks:
            self.grocery_list.append([element['id'], None, element['title']])

    # grabs categories (actually their order via implicit argument to groceryStore) by item name
    def get_category_for_element(self, list_element, grocery_store):
        return grocery_store.get_and_fix_category_for_ingredient(list_element[2])

    def get_categories(self, grocery_store):
        for index, list_element in enumerate(self.grocery_list):
            self.grocery_list[index][1] = self.get_category_for_element(list_element, grocery_store)

    def reorder_list(self, local_only = False):

        self.grocery_list.sort(key=itemgetter(1))  # itemgetter tells python which key to use to sort on. in this case category_order.
        if local_only is not True:
            self.wp.reorder_list(self.wunderlist_list_id, [i[0] for i in self.grocery_list])