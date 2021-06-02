class ConcreteNonParameterizedConstraint():
    def __init__(self, nonParameterizedConstraint, parent=None):
        self.nonParameterizedConstraint = nonParameterizedConstraint
        self.parent = parent
    
    def __str__(self):
        return self.nonParameterizedConstraint.name

