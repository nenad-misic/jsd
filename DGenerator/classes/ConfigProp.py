class ConfigProp():
    def __init__(self, configPropName, value, parent=None):
        self.configPropName = configPropName
        self.value = value
        self.parent = parent
    
    def __str__(self):
        return self.name
