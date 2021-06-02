class InjectedField():
    def __init__(self, fieldName, parent=None):
        self.fieldName = fieldName
    
    def __str__(self):
        return self.fieldName
