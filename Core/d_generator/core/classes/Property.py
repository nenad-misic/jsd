
class Property():
    def __init__(self, name, type, constraints, parent=None):
        self.name = name
        self.type = type
        self.constraints = constraints
        self.parent = parent
    
    def __str__(self):
        return self.name