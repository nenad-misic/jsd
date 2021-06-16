from os import mkdir
from os.path import exists, dirname, join, abspath
from datetime import datetime
import pkg_resources

import jinja2

from d_generator.core.generator import Generator 

from d_generator.core.classes.SimpleType import SimpleType
from d_generator.core.classes.ConcreteNonParameterizedConstraint import ConcreteNonParameterizedConstraint
from d_generator.core.classes.ConcreteParameterizedConstraint import ConcreteParameterizedConstraint
from d_generator.core.classes.Entity import Entity
from d_generator.core.classes.NonParameterizedConstraint import NonParameterizedConstraint
from d_generator.core.classes.ParameterizedConstraint import ParameterizedConstraint
from d_generator.core.classes.Property import Property
from d_generator.core.classes.Relationship import Relationship


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


def load_template(name):
    template_stream = pkg_resources.resource_stream(__name__, 'template/' + name)
    template = template_stream.read().decode()
    return template

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
        
        supported_databases = ['sqlite']
        if not self.model.configObject.database in supported_databases:
            raise Exception(f'Database {self.model.configObject.database} is not supported. Choose one from list: {supported_databases}')
            
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
            loader=jinja2.FunctionLoader(load_template),
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

        # Generating environment/environment.js
        self.generateFolder('express/environment')
        environmentTemplate = jinja_env.get_template('environment.jinja')
        self.generateModelTemplate(environmentTemplate, 'express/environment/environment.js')

        # Generating middlewares and index.js
        self.generateFolder('express/middlewares')
        errorhandlerTemplate = jinja_env.get_template('error_handler.jinja')
        self.generateModelTemplate(errorhandlerTemplate, 'express/middlewares/error_handler.js')
        authHandlerTemplate = jinja_env.get_template(f'{self.model.configObject.authentication}_auth_handler.jinja')
        self.generateModelTemplate(authHandlerTemplate, 'express/middlewares/auth_handler.js')
        serverjsTemplate = jinja_env.get_template('indexjs_middlewares.jinja')
        self.generateModelTemplate(serverjsTemplate, 'express/middlewares/index.js')

        # Generating API documentation
        doc_indexhtmlTemplate = jinja_env.get_template('documentation/indexhtml.jinja')
        self.generateModelTemplate(doc_indexhtmlTemplate, 'express/public/index.html')
        doc_indexcssTemplate = jinja_env.get_template('documentation/indexcss.jinja')
        self.generateModelTemplate(doc_indexcssTemplate, 'express/public/index.css')
        doc_indexjsTemplate = jinja_env.get_template('documentation/indexjs.jinja')
        self.generateModelTemplate(doc_indexjsTemplate, 'express/public/index.js')

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
        
        # Generating repositories folder and index.js
        self.generateFolder('express/autogenerated/repositories')
        self.generateFolder('express/repositories')
        serverjsTemplate = jinja_env.get_template('indexjs_repositories.jinja')
        self.generateModelTemplate(serverjsTemplate, 'express/repositories/index.js')
        
        for entity in self.model.entities:
            auth_extension = ''
            if self.model.authObject.userEntity ==  entity.name:
                auth_extension = 'AuthEntity'
                entity._username = self.model.authObject.usernameProp
                entity._password = self.model.authObject.passwordProp

            # Generating baseRoutes
            baseRouterTemplate = jinja_env.get_template(f'autogenerated/baseRouter{auth_extension}.jinja')
            self.generateEntityTemplate(baseRouterTemplate, f'express/autogenerated/routes/base_{entity.name.lower()}_routes.js', entity)
            
            # Generating routes
            routerTemplate = jinja_env.get_template('router.jinja')
            self.generateEntityTemplate(routerTemplate, f'express/routes/{entity.name.lower()}_routes.js', entity)

            # Generating baseServices
            baseServiceTemplate = jinja_env.get_template(f'autogenerated/baseService{auth_extension}.jinja')
            self.generateEntityTemplate(baseServiceTemplate, f'express/autogenerated/services/base_{entity.name.lower()}_service.js', entity)
            
            # Generating services
            serviceTemplate = jinja_env.get_template('service.jinja')
            self.generateEntityTemplate(serviceTemplate, f'express/services/{entity.name.lower()}_service.js', entity)
            

            # Generating baseRepositories
            baseRepositoryTemplate = jinja_env.get_template(f'autogenerated/baseRepository/{self.model.configObject.database}BaseRepository{auth_extension}.jinja')
            self.generateEntityTemplate(baseRepositoryTemplate, f'express/autogenerated/repositories/base_{entity.name.lower()}_repository.js', entity)
            
            # Generating repositories
            repositoryTemplate = jinja_env.get_template(f'repository/{self.model.configObject.database}Repository.jinja')
            self.generateEntityTemplate(repositoryTemplate, f'express/repositories/{entity.name.lower()}_repository.js', entity)

            doc_htmlTemplate = jinja_env.get_template('documentation/entityhtml.jinja')
            self.generateEntityTemplate(doc_htmlTemplate, f'express/public/{entity.name.lower()}_page.html', entity)
            doc_htmlTemplate = jinja_env.get_template('documentation/entityjs.jinja')
            self.generateEntityTemplate(doc_htmlTemplate, f'express/public/{entity.name.lower()}_page.js', entity)
