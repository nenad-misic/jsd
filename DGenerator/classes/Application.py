from collections import namedtuple

class Application():
    def __init__(self, name, config, entities, relationships):
        self.name = name
        self.config = config
        self.entities = entities
        self.relationships = relationships
        configDict = { i.configPropName : i.value for i in self.config.configProps }
        self.configObject = namedtuple('ConfigObject', configDict.keys())(*configDict.values())
    
    def __str__(self):
        return self.name