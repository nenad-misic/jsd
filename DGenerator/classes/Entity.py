class Entity():
    def __init__(self, name, properties, parent=None):
        self.name = name
        self.properties = properties
        self.parent = parent
    
    def __str__(self):
        return self.name
