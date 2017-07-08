"""
This file defines two objects:

1. RecipeList is an object for the TOC
2. Recipe is an object for a specific recipe

"""
# TODO Rebuild RecipeBook to be more of a recipe book that can contain recipes, other stuff
# TODO add recipes into a RecipeBook (right now recipeList)
# TODO add an additional column in your recipes to suppress addition or search by name(eg salt)


class RecipeList:
    startRow = 2
    recipeColumn = 'A'
    maxRecipes = 999

    # initialize with the worksheet. assumes we get the workbook separately.
    def __init__(self, worksheet):
        self.worksheet = worksheet
        self.recipes = []

    # I know it does the work each time insteaf of checking. whatever. :D
    def getRecipeList(self):
        row = RecipeList.startRow  # first row, ignore title row
        col = RecipeList.recipeColumn = 'A'

        while (self.worksheet[col + str(row)].value is not None) and (row < RecipeList.maxRecipes):
            self.recipes.append(self.worksheet[col + str(row)].value)
            row = row + 1
            # print str(row) + "  " + recipes[row-row0] + "'"

        return self.recipes

    def showRecipeList(self):
        rlist = [l for l in self.recipes]
        print('\n'.join(rlist))

    def getRecipeNameByID(self, recipe_id):
        return self.recipes[recipe_id]

    def pickRecipeNameFromList(self):

        i = 0
        print("Select recipe by id:")

        for recipe in self.recipes:
            print(str(i) + ": " + str(recipe))
            i = i + 1

        recipe_id = -1
        try:
            recipe_id = int(input("Select ID: "))
        except TypeError:
            print("ID must be an integer.")
        except ValueError:
            print("Could not convert your input to integer.")

        # validate selection and get ingredients
        if (recipe_id < 0) or (recipe_id >= len(self.recipes)):
            print("Invalid recipe selection")
            return False

        return self.getRecipeNameByID(recipe_id)  # assuming we get here; great code style


# Right now you pass in the name and the workbook. It loads the worksheet into the object
class Recipe:

    # Variables here are common across all classes
    count = 0

    recipeStartRow = 4
    recipeColumn = 'A'
    recipeWidth = 2
    blanksAllowed = 1
    maxIngredients = 45

    def __init__(self, name, workbook):
        self.name = name
        self.worksheetName = name  # so far there isn't any difference with name; no ID for example
        self.worksheet = workbook[self.worksheetName]
        self.ingredientList = []

        Recipe.count = Recipe.count + 1

    def listIngredients(self):
        rlist = [l for l in self.ingredientList]
        print('\n'.join(rlist))

    def getIngredients(self):
        
        blank_counter = 0
        row = Recipe.recipeStartRow

        self.ingredientList = []  # clear ingredients and restart

        print('getting ingredients for '+self.name)

        while blank_counter <= Recipe.blanksAllowed and row < Recipe.maxIngredients + Recipe.recipeStartRow:

            # while shorter and faster this does not address the 'None" elemnt issue. Need a reject-None method?
            # this_ingredient = ' '.join([str(self.worksheet[chr(c + ord(Recipe.recipeColumn)) + str(row)].value).strip()
            #                                 for c in range(Recipe.recipeWidth)]).strip()

            this_ingredient = []
            for i in range(Recipe.recipeWidth):
                part = self.worksheet[chr(ord(Recipe.recipeColumn) + i) + str(row)].value
                if part is not None:
                    this_ingredient.append(str(part).strip())
            this_ingredient = " ".join(this_ingredient).strip()

            # print this_ingredient

            if this_ingredient == '':
                # skip & add to blanks if needed
                blank_counter = blank_counter + 1
            else:
                # reset blanks and save ingredient
                blank_counter = 0
                self.ingredientList.append(this_ingredient)

            row = row + 1

        print(" ... got " + str(len(self.ingredientList)) + " ingredients")

        return self.ingredientList

    def addMealToWunderlist(self, wunder_list_id, wunderlist_client):
        wunderlist_client.create_task(wunder_list_id, self.name)
        print(" ... done adding meal to list")
        return True

    def addListToWunderlist(self, wunder_list_id, wunderlist_client):

        if len(self.ingredientList) == 0:
            self.getIngredients()

        if 0 < len(self.ingredientList) < Recipe.maxIngredients:
            # print("adding " + str(len(self.ingredientList)) + " ingredients")
            for element in self.ingredientList:
                if element != "":
                    # print "sending "+element+" to "+list_id
                    element_task = wunderlist_client.create_task(wunder_list_id, element)
                else:
                    print("ERR: ingredient blank somehow... Debug req.")
            print("  ... done adding ingredient tasks")
            return True

        else:
            print("There are either 0 or more than " + str(Recipe.maxIngredients) + "elements.")
            print("Tried to get ingredients again, didn't work. Maybe Max elemnts is the issue")
            print("Current ingredient list is:")
            for element in self.ingredientList:
                print(element)
            return False
