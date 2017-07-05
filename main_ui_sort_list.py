
#works in qtpy (since it's uniform for ptqy5 i think
import sys
from qtpy import QtCore, QtGui, uic, QtWidgets

from classes import grocerystore
from classes import grocerylist

from classes import wunderpy_wrapper
wp = wunderpy_wrapper.wunderpy_wrapper()

grocery_store = grocerystore.groceryStore('./data/store_order_zehrs.csv')
groceries = grocerylist.groceryList(wp.WUNDERLIST_GROCERY, wp)
groceries.get_categories(grocery_store)

# load the UI class objects
UiMainWindow, QtBaseClass = uic.loadUiType('./ui/recipeBookUI.ui')

#UI class definition
class GroceryAppUI(QtWidgets.QMainWindow, UiMainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        UiMainWindow.__init__(self)
        self.setupUi(self)
        
        #setup menubar
        self.QActionSort_grocery_list.triggered.connect(self.show_pageMissingCategory)

        #setup missing ingredient page:
        self.populate_categories()

        self.next_missing_ingredient()

        if self.missing_ingredient is not None:
            self.QbuttonSelect.clicked.connect(self.select_category_and_next)
            self.QbuttonSkip.clicked.connect(self.skip_category_select)

        #next setup goes here:

    #Todo Can we set an input variable? Can we do it by sender somehow? Property on sender Action or Name?
    def show_pageMissingCategory(self):
        self.stackedWidget.setCurrentWidget(self.pageMissingCategory)

    #populate QlistCategories from grocery store
    def populate_categories(self):
        #this adds items and creates QListWidgetItem as you go; no secondary data; search?

        for cat in grocery_store.categories:
            thisItem = QtWidgets.QListWidgetItem(cat[1])
            thisItem.setData(99,cat[0]) # read self.QlistCategories.item(<selected>).data(99)
            self.QlistCategories.addItem(thisItem)

    def next_missing_ingredient(self):
        new_ingred = groceries.get_next_new_ingredient()

        if new_ingred == None:
            self.missing_ingredient = None
            groceries.reorder_list()
            self.set_next_ingredient('List re-ordered.')

            self.QbuttonSelect.setDisabled(True)
            self.QbuttonSkip.setDisabled(True)

        else:
            self.set_next_ingredient(new_ingred[2])
            self.missing_ingredient = new_ingred

    # todo there is some repetition here that would be nice to fix
    def select_category_and_next(self):
        selected_id = self.get_selected_cagetory('id')

        if self.missing_ingredient is not None and selected_id is not None:

            self.QlastAction.setText('Added ' +self.missing_ingredient[2] + ' to ' + grocery_store.get_category_name_from_id(selected_id))

            grocery_store.add_ingredient_to_category(self.missing_ingredient[2], selected_id)
            groceries.set_category_for_item(self.missing_ingredient[2],selected_id)

            self.next_missing_ingredient()

    # todo there is some repetition here that would be nice to fix
    def skip_category_select(self):
        selected_id = self.get_selected_cagetory('id')

        if self.missing_ingredient is not None and selected_id is not None:
            self.QlastAction.setText('Set ' + self.missing_ingredient[2] + ' to ' + grocery_store.get_category_name_from_id(selected_id))

            groceries.set_category_for_item(self.missing_ingredient[2], selected_id)
            self.next_missing_ingredient()

    #on QbuttonSelect click get the selectedItem() from QlistCategories
    def get_selected_cagetory(self, ret='id'):

        selectedItems = self.QlistCategories.selectedItems()

        if len(selectedItems) == 1:
            selected_category = selectedItems[0].text()
            selected_category_id = selectedItems[0].data(99)
        else:
            # > 1 or 0 categories selected. we don't do that.
            selected_category = None
            selected_category_id = None

        # self.QtextMissing_ingredient.setText(selected_category + "  " + str(selected_category_id))

        if ret == 'name':
            return selected_category
        else:
            return selected_category_id


    def set_next_ingredient(self, text):
        self.QtextMissing_ingredient.setText(text)

    #groceries.get_categories(grocery_store)
    #groceries.reorder_list()

# main program
if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    window = GroceryAppUI()
    window.show()

    sys.exit(app.exec_())


"""
#works, uses pyqt5

from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QMainWindow
from PyQt5 import uic
import sys

class DemoImpl(QMainWindow):

    def __init__(self, *args):

        super(DemoImpl, self).__init__(*args)
        uic.loadUi('./ui/missing_ingredient.ui',self)
        #UiMain_window, QtBaseClass = uic.loadUiType('./ui/missing_ingredient.ui')
        self.UiMain_window, self.QtBaseClass = uic.loadUiType('./ui/missing_ingredient.ui')

app = QApplication(sys.argv)
window = DemoImpl()
window.show()
sys.exit(app.exec_())

"""
"""
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import sys


class Form(QWidget):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        nameLabel = QLabel("Name:")
        self.nameLine = QLineEdit()
        self.submitButton = QPushButton("&Submit")

        buttonLayout1 = QVBoxLayout()
        buttonLayout1.addWidget(nameLabel)
        buttonLayout1.addWidget(self.nameLine)
        buttonLayout1.addWidget(self.submitButton)

        self.submitButton.clicked.connect(self.submitContact)

        mainLayout = QGridLayout()
        # mainLayout.addWidget(nameLabel, 0, 0)
        mainLayout.addLayout(buttonLayout1, 0, 1)

        self.setLayout(mainLayout)
        self.setWindowTitle("Hello Qt")

    def submitContact(self):
        name = self.nameLine.text()

        if name == "":
            QMessageBox.information(self, "Empty Field",
                                    "Please enter a name and address.")
            return
        else:
            QMessageBox.information(self, "Success!",
                                    "Hello %s!" % name)

if __name__ == '__main__':


    app = QApplication(sys.argv)

    screen = Form()
    screen.show()

    sys.exit(app.exec_())
"""