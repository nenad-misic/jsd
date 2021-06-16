class ParameterizedConstraint():
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
    
    def __str__(self):
        return self.name
