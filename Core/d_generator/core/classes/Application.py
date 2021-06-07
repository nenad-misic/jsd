from collections import namedtuple

class Application():
    def __init__(self, name, config, auth, entities, relationships):
        self.name = name
        self.config = config
        self.auth = auth
        self.entities = entities
        self.relationships = relationships
        configDict = { i.configPropName : i.value for i in self.config.configProps }
        self.configObject = namedtuple('ConfigObject', configDict.keys())(*configDict.values())
        authDict = { i.authPropName : i.value for i in self.auth.authProps }
        self.authObject = namedtuple('AuthObject', authDict.keys())(*authDict.values())
    
    def __str__(self):
        return self.name