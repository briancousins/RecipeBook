import re
import unicodecsv as csv
import classes.wunderpy_wrapper

# contains and deals with the layout of the grocery store. Critical for the groceryList ordering.
# it also manages the categories of ingredients (eg: where, by group, where you would find an ingredient)

class groceryStore:

    # TODO refactor this so it isn't hardcoded.
    ingredient_file = './data/ingredient_categories.csv'  # really not happy about this!

    #set up categories and ingredients automatically
    def __init__(self, store_category_file='./data/store_order_zehrs.csv'):

        # set object variables
        self.store_category_file = store_category_file

        self.ingredient_match_str = re.compile(
            '[0-9?/%-. ]*(tablespoons|teaspoons|cups|tablespoon|teaspoon|pounds|cloves|pound|large|some|pack|cup|tsps|tbsps|tsp|tbsp|lbs|lb|ml|of|oz|mg|g|t|l|C|Q|v|x)*([?+"])*(?(1)\s)+(?P<ingredient>["A-z \']+)',
            re.IGNORECASE)  # want to limit lengths, no ,- allowed.

        #TODO this sucks but 2C of 18% cream and 2L 2% milk and 2% and ... :|
        self.ingredient_milk_match = re.compile('(?P<milk>[0-9]+%)', re.IGNORECASE)  # match anything with x%; most likely milk product. what else uses %s? and will not match the ingredient_match_str?

        # set object placeholders
        self.ingredients = {}  # {'ingredient'} = category
        self.categories = []  # categories[?] = (id, name, order); should be fast to search the list.

        # run init methods
        self.load_category_order() # loads off of self.category_file
        self.load_ingredients() # can be overwritten if the default is no good

    # loads ingredients into the dict from file.
    def load_ingredients(self, file='./data/ingredient_categories.csv'):

        self.ingredients = {}

        with open(file, 'rb') as ingredient_file:
            ingredient_csv = csv.reader(ingredient_file, delimiter=',')
            for row in ingredient_csv:
                try:
                    self.ingredients[row[0]] = int(row[1])
                except TypeError:
                    self.ingredients[row[0]] = self.get_category_id_from_name('Unknown')

    # this is run as part of the init routine. you shouldn't need to run this at all.
    def load_category_order(self):

        with open(self.store_category_file, 'rb') as category_file:
            category_csv = csv.reader(category_file, delimiter=',')
            for row in category_csv:
                try:
                    self.categories.append((int(row[0]), row[1], int(row[2])))
                except AttributeError or TypeError:
                    print('Attribute or Type error loading categories! first and last entries must be int() (no float)')

    def get_category_for_ingredient(self, ingredient):

        try:  # find ingredient in associated_ingredients
            category = next((c for c in self.categories if
                             int(c[0]) == self.ingredients[self.isolate_ingredient_name(ingredient)]), (99, 'Unknown_Failed_Search', 99))

        except KeyError: # ingredient DNE, no problem.
            category = None
        except TypeError:# this is unexpected.. invalid category id?
            category = None
            #print('Type Error trying to find isolated ' + ingredient + ' for category: ' + str(category) )

        return category

    # ensure this is run only after you load_category_order(); no error checking.
    # does isolation as part of the call, so this is the key interface with the class
    #  typically we want to return the category order for sorting in a given store.
    def get_and_fix_category_for_ingredient(self, ingredient, return_category_order = True):

        if return_category_order == True:
            return_column = 2
        else:
            return_column = 0

        category_id = 99  # set default

        category = self.get_category_for_ingredient(ingredient)

        if category is not None:
            category_id = category[return_column]
        else:
            print('Did not find ingredient ' + isolated_ingredient + '.')

            add_to_category = 'l'
            while add_to_category == 'l':

                add_to_category = input('Should we add it to the ingredient list [<cat_id>, L for list, other to put at end of list]? ').lower()

                if add_to_category[0] == 'l':
                    for c in self.categories:
                        print(str(c[0]) + ': ' + c[1])

                elif re.fullmatch('[0-9]+', add_to_category):
                    #1 <= int(add_to_category) <= 99:  #  todo really worried about this.
                    add_to_category_id = int(add_to_category)

                    self.add_ingredient_to_category(isolated_ingredient, add_to_category_id)
                    category_id = self.get_category_order_from_id(add_to_category_id)

                else:
                    print('> Using unknown category as default')
                    category_id = self.get_category_id_from_name('Unknown')

        return category_id

    # TODO finish & check if regex is working. IDE says no. milk match works ok.
    # TODO check for ' x ', etc and address those
    def isolate_ingredient_name(self, ingredient_name):

        milk_result = self.ingredient_milk_match.search(ingredient_name)
        full_result = self.ingredient_match_str.match(ingredient_name).group('ingredient').strip().lower()

        if full_result is None and milk_result is not None:
            full_result = 'milk'
            print("> choosing milk for "+ingredient_name)

        elif full_result is None and milk_result is None:  # really just result is none and not milk
            full_result = ingredient_name

        return full_result

    # TODO test may not work. this seems fine
    # TODO i'd like to refactor ingredient_file
    def add_ingredient_to_category(self, ingredient_name, category):

        if groceryStore.ingredient_file is not None:
            ingredient_name = self.isolate_ingredient_name(ingredient_name)

            with open(groceryStore.ingredient_file, 'ab') as csvfile:
                writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL, quotechar='`')
                writer.writerow([ingredient_name, category])

    def get_category_id_from_name(self, category_name):
        return next((c[0] for c in self.categories if c[1]==category_name),99)

    def get_category_order_from_id(self, category_id):
        return next((c[2] for c in self.categories if c[0] == category_id), 99)


class groceryIngredientSetup(groceryStore):
    def __init__(self, category_order_csv):
        groceryStore.__init__(self, category_order_csv)  # store order doesn't matter.

        # raw list of ingredients. mostly defined as part of our initial setup (subclass grocery_store_setup?)
        self.ingredients_list = []  # will be greated as a set but saved as a list.

        # a list of [ingredient, category_id]
        self.manual_ingredient_category_definition = []  # this gets overwritten in the associate_ingredients function right now

    def pull_all_completed_from_wunderlist(self):
        wp = classes.wunderpy_wrapper.wunderpy_wrapper()

        lists = wp.get_lists()

        # l_details = wp.get_list_details(lists['Kijiji'])
        # bad_list_id_req = wp.get_list_details(0)  # returns None

        l_tasks = wp.get_tasks(lists['Groceries'], True)  # there's a lot of groceries on the completed list!
        l_positions = wp.get_list_positions(lists['Groceries'])

        task_names = [(l['title'], self.isolate_ingredient_name(l['title'])) for l in l_tasks]

        # for i in range(len(task_names)):
        #     try:
        #         print(task_names[i][1].group('ingredient').strip() + '||                  from '+task_names[i][0])
        #     except AttributeError:
        #         print('** ' + task_names[i][0])

        ingredients_set = set()
        for task in task_names:
            try:
                ingredients_set.add(task[1])
            except AttributeError:
                print('failed for ' + task[0])

        self.ingredients_list = list(ingredients_set)
        self.ingredients_list.sort()
        # print('Length: ' + str(len(ingredients)))
        # print(ingredients)
        # I saved this to a txt file...

    def write_ingredients_to_file(self, filename='./data/grocery_items.csv'):
        # requires unicode csv

        with open(filename, 'wb') as csvfile:
            for i in self.ingredients_list:
                writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL, quotechar='"')
                writer.writerow([i])  # not sure.. writerow(i) was bad news bears.

    def load_ingredients_to_list(self, filename='./data/grocery_items_raw.csv'):
        # load ingredients from grocery_items.csv
        # requires unicodecsv

        self.ingredients_list = []

        with open(filename, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                self.ingredients_list.append(', '.join(row))

    def manual_ingredient_category_definition(self, filename='categories.csv'):

        self.associated_ingredients = []

        print("pick category:")

        count = 1
        for i in self.ingredients_list:

            try:
                category = int(input('(' + str(count) + ')' + i + " :"))
            except ValueError:
                print("Could not convert your input to integer.")

            self.associated_ingredients.append((i, category))

            # save as you go.. this list can be LONG!
            self.add_ingredient_to_category(i, category)

            count = count + 1
