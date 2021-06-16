class Relationship():
    def __init__(self, relationshipType, source, sourceInjectedField, target, targetInjectedField, parent=None):
        self.relationshipType = relationshipType
        self.source = source
        self.sourceInjectedField = sourceInjectedField
        self.target = target
        self.targetInjectedField = targetInjectedField
        self.parent = parent
    
    def __str__(self):
        return f"{self.source.name}To{self.target.name}"