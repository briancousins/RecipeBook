import wunderpy2 # from https://pypi.python.org/pypi/wunderpy2
import csv

class wunderpy_wrapper:

    def __init__(self):

        self.load_tokens()

        self.wp_api = wunderpy2.WunderApi()
        self.client = self.wp_api.get_client(self.access_token, self.client_id)
        self.lists = []

    # load all the wudnerlist config tokens. I know it's a hack. I'd rather have a tokens dict and use it
    # but here we are
    # I was bad about methods to access data previously and now we're stuck keeping self.<var> as is.
    def load_tokens(self, file = './data/tokens.csv'):
        with open(file, 'r') as csvfile:
            reader = csv.DictReader(csvfile, ['name','key'])
            keys = [r['key'] for r in reader]
            self.access_token   = keys[0]
            self.client_id      = keys[1]
            self.client_secret  = keys[2]

            self.WUNDERLIST_GROCERY = keys[3]
            self.WUNDERLIST_MEALS   = keys[4]

    # Return list dict where the name is then key & id is the data. Can be used with get_list_details.
    def get_lists(self):
        self.lists = self.client.get_lists()
        lists_dict = {}

        for list in self.lists:
            lists_dict[list['title']] = list['id']

        return lists_dict

    def get_list_details(self, list_id):
        # find first element for 'id'. return None if list is exhausted
        # would also work: self.client.get_list(list_id)
        return next((li for li in self.lists if li['id'] == list_id), None)

    def get_list_positions(self, list_id):

        # get task names (and list positions -- unnecessary?)
        return self.client.get_task_positions_obj(list_id)  # list id of form self.lists[wunderpy2.List.ID] ?

        return associated_list

    def get_tasks(self, list_id, completed = False):
        return self.client.get_tasks(list_id, completed)

    # as an example...
    def get_task_positions_obj(self, list_id):

        return self.client.get_task_positions_obj(list_id)

    def reorder_list(self, list_id, new_order):

        position_obj = self.client.get_task_positions_obj(list_id)

        pos_id = position_obj[wunderpy2.List.ID]
        revision = position_obj[wunderpy2.List.REVISION]   # why do we need reivision?

        self.client.update_task_positions_obj(pos_id, revision , new_order)