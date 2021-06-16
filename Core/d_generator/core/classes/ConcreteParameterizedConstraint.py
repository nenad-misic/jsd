class ConcreteParameterizedConstraint():
    def __init__(self, parameterizedConstraint, value, parent=None):
        self.parameterizedConstraint = parameterizedConstraint
        self.value = value
        self.parent = parent
    
    def __str__(self):
        return self.parameterizedConstraint.name
