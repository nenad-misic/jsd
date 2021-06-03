from os import mkdir
from os.path import exists, dirname, join, abspath
from datetime import datetime

import jinja2

from generator.generator import Generator 

from classes.SimpleType import SimpleType
from classes.ConcreteNonParameterizedConstraint import ConcreteNonParameterizedConstraint
from classes.ConcreteParameterizedConstraint import ConcreteParameterizedConstraint
from classes.Entity import Entity
from classes.NonParameterizedConstraint import NonParameterizedConstraint
from classes.ParameterizedConstraint import ParameterizedConstraint
from classes.Property import Property
from classes.Relationship import Relationship

this_folder = dirname(__file__)

def _defaultValueOfType(type):
    types = {
        'integer': 0,
        'string': '\"\"',
        'float': 0.0,
        'boolean': 'false' 
    }

    return types[type.name]

def _getPrimaryKeyProperty(entity):
        pk = next((prop for prop in entity.properties if next((constraint for constraint in prop.constraints if (hasattr(constraint, 'nonParameterizedConstraint') and constraint.nonParameterizedConstraint.name=='primaryKey')), None) != None), None)
        if pk is None:
            raise Exception(f"Entity {entity.name} does not have primary key property.")
        return pk 
    
def _getAllPropsExceptPrimaryKey(entity):
    pk = _getPrimaryKeyProperty(entity)
    return filter(lambda x: x.name != pk.name, entity.properties)

class ExpressGenerator(Generator):
    def __init__(self, model, srcgen_folder, model_filename):
        super().__init__(model, srcgen_folder, model_filename)
       
    def generateModelTemplate(self, template, filename):
        with open(join(self.srcgen_folder, filename), 'w') as f:
            f.write(template.render(application=self.model, timestamp=datetime.now(), model_filename=self.model_filename))

    def generateEntityTemplate(self, template, filename, entity):
            with open(join(self.srcgen_folder, filename), 'w') as f:
                f.write(template.render(application=self.model, entity=entity, timestamp=datetime.now(), model_filename=self.model_filename))

    def generateFolder(self, folderName):
        if not exists(join(self.srcgen_folder, folderName)):
            mkdir(join(self.srcgen_folder, folderName))

    def prepare_model(self):
            
        for relationship in self.model.relationships:
            if relationship.relationshipType == "OneToOne":
                if not (relationship.targetInjectedField is None or relationship.sourceInjectedField is None):
                    # Bidirect relation
                    raise Exception('Both source and target injected fields are present. Relation cannot be bidirect.')
                if not (relationship.sourceInjectedField is None):
                    # Source has pointer to target
                    if not hasattr(relationship.source, 'properties'):
                        relationship.source.properties = []
                    relationship.source.properties.append(Property(relationship.sourceInjectedField, _getPrimaryKeyProperty(relationship.target).type, []))
                elif not (relationship.targetInjectedField is None):
                    # Target has pointer to source
                    if not hasattr(relationship.target, 'properties'):
                        relationship.target.properties = []
                    relationship.target.properties.append(Property(relationship.targetInjectedField, _getPrimaryKeyProperty(relationship.source).type, []))
                else:
                    # No pointer
                    raise Exception('Neither source nor target injected fields are present. Relation invalid.')

            elif relationship.relationshipType == "OneToMany":
                if relationship.sourceInjectedField is None and not (relationship.targetInjectedField is None):
                    # Target points to source
                    if not hasattr(relationship.target, 'properties'):
                        relationship.target.properties = []
                    relationship.target.properties.append(Property(relationship.targetInjectedField, _getPrimaryKeyProperty(relationship.source).type, []))
                else:
                    raise Exception('Relation invalid. OneToMany relation needs only target injected field assigned.')

            elif relationship.relationshipType == "ManyToMany":
                if not (relationship.sourceInjectedField is None) and not (relationship.targetInjectedField is None):
                    # Both sides have pointer
                    properties = [
                        Property('id', SimpleType('integer'), [ConcreteNonParameterizedConstraint(NonParameterizedConstraint('primaryKey')),ConcreteNonParameterizedConstraint(NonParameterizedConstraint('autoincrement'))]),
                        Property(relationship.sourceInjectedField.fieldName, _getPrimaryKeyProperty(relationship.target).type, []),
                        Property(relationship.targetInjectedField.fieldName, _getPrimaryKeyProperty(relationship.source).type, []),
                    ]
                    entity = Entity(relationship.source.name + 'To' + relationship.target.name, properties)
                    self.model.entities.append(entity)
                    # self.model.relationships.append(entity.relationships)
                else:
                    raise Exception('Relation invalid. ManyToMany relation needs both source and target injected fields assigned.')


    def generate_code(self):
        self.prepare_model()

        jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(join(this_folder, 'template')),
            trim_blocks=True,
            lstrip_blocks=True)

        
        jinja_env.filters['strftime'] = lambda x: x.strftime("%d.%m.%Y %H:%M:%S")
        jinja_env.filters['lowercase'] = lambda x: x.lower()
        jinja_env.filters['replace_'] = lambda x: x.replace('_', ' ')
        jinja_env.filters['firstUppercase'] = lambda x: x.capitalize()
        jinja_env.filters['primaryKeyProp'] = _getPrimaryKeyProperty
        jinja_env.filters['defaultValueOfType'] = _defaultValueOfType
        jinja_env.filters['propsExceptPk'] = _getAllPropsExceptPrimaryKey
        
        
        self.generateFolder('express')
        self.generateFolder('express/autogenerated')
        self.generateFolder('express/public')

        # Generating package.json
        packagejsonTemplate = jinja_env.get_template('packagejson.jinja')
        self.generateModelTemplate(packagejsonTemplate, 'express/package.json')

        # Generating baseServer.js
        serverjsTemplate = jinja_env.get_template('autogenerated/baseServerjs.jinja')
        self.generateModelTemplate(serverjsTemplate, 'express/autogenerated/baseServer.js')

        # Generating server.js
        serverjsTemplate = jinja_env.get_template('serverjs.jinja')
        self.generateModelTemplate(serverjsTemplate, 'express/server.js')

        # Generating middlewares and index.js
        self.generateFolder('express/middlewares')
        errorhandlerTemplate = jinja_env.get_template('error_handler.jinja')
        self.generateModelTemplate(errorhandlerTemplate, 'express/middlewares/error_handler.js')
        serverjsTemplate = jinja_env.get_template('indexjs_middlewares.jinja')
        self.generateModelTemplate(serverjsTemplate, 'express/middlewares/index.js')



        # Generating routes folder and index.js
        self.generateFolder('express/autogenerated/routes')
        self.generateFolder('express/routes')
        serverjsTemplate = jinja_env.get_template('indexjs_routes.jinja')
        self.generateModelTemplate(serverjsTemplate, 'express/routes/index.js')

        
        # Generating services folder and index.js
        self.generateFolder('express/autogenerated/services')
        self.generateFolder('express/services')
        serverjsTemplate = jinja_env.get_template('indexjs_services.jinja')
        self.generateModelTemplate(serverjsTemplate, 'express/services/index.js')
        

        for entity in self.model.entities:
           
            # Generating baseRoutes
            baseRouterTemplate = jinja_env.get_template(f'autogenerated/baseRouter.jinja')
            self.generateEntityTemplate(baseRouterTemplate, f'express/autogenerated/routes/base_{entity.name.lower()}_routes.js', entity)
            
            # Generating routes
            routerTemplate = jinja_env.get_template('router.jinja')
            self.generateEntityTemplate(routerTemplate, f'express/routes/{entity.name.lower()}_routes.js', entity)

            # Generating baseServices
            baseServiceTemplate = jinja_env.get_template(f'autogenerated/baseService.jinja')
            self.generateEntityTemplate(baseServiceTemplate, f'express/autogenerated/services/base_{entity.name.lower()}_service.js', entity)
            
            # Generating services
            serviceTemplate = jinja_env.get_template('service.jinja')
            self.generateEntityTemplate(serviceTemplate, f'express/services/{entity.name.lower()}_service.js', entity)




        

        
