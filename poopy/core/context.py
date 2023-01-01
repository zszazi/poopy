class Context:
    def __init__(self, display_name, parent_context=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent_context = parent_context
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None
