class AuthProp():
    def __init__(self, authPropName, value, parent=None):
        self.authPropName = authPropName
        self.value = value
        self.parent = parent
    
    def __str__(self):
        return self.name
