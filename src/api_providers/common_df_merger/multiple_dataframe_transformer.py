class Multiple_df_manager:
    def __init__(self):
        self.fx_list = []
        self.bond_yield_list = []

    def add_to_fx_list(self, passed_fx_df):
        print(type(self.fx_list))
        # print(f"Lenght of fx_list is {len(self.fx_list)}")
        self.fx_list.append(passed_fx_df)
        return self.fx_list

    def add_to_bond_yield_list(self, passed_bond_yield_df):
        self.bond_yield_list.append(passed_bond_yield_df)
        return self.bond_yield_list

    def len_of_lists(self):
        print(f"Length of fx_list is {len(self.fx_list)}")
