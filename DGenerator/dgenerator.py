from os.path import exists, dirname, join, abspath
from os import mkdir
import sys


from classes.SimpleType import SimpleType
from classes.ConcreteNonParameterizedConstraint import ConcreteNonParameterizedConstraint
from classes.ConcreteParameterizedConstraint import ConcreteParameterizedConstraint
from classes.Entity import Entity
from classes.NonParameterizedConstraint import NonParameterizedConstraint
from classes.ParameterizedConstraint import ParameterizedConstraint
from classes.Property import Property
from classes.Relationship import Relationship
from classes.Application import Application
from classes.Config import Config
from classes.ConfigProp import ConfigProp
from classes.InjectedField import InjectedField


from mapper.ApplicationMapper import applicationToDto

from textx import metamodel_from_file
from textx.export import metamodel_export, model_export

from generator.sqlite.sqlite_generator import SqliteGenerator
from generator.express.express_generator import ExpressGenerator
from generator.react.react_generator import ReactGenerator

this_folder = dirname(__file__)
model_filename = "model/application.dgdl"
metamodel_filename = "metamodel/grammar.tx"
    
def get_entity_mm():
    type_builtins = {
        'integer': SimpleType('integer'),
        'string': SimpleType('string'),
        'boolean': SimpleType('boolean'),
        'float': SimpleType('float')
    }

    parameterized_constraint_builtins = {
        'min': ParameterizedConstraint('min'),
        'max': ParameterizedConstraint('max'),
        'pattern': ParameterizedConstraint('pattern'),
        'default': ParameterizedConstraint('default'),
    }

    non_parameterized_constraint_builtins = {
        'required': NonParameterizedConstraint('required'),
        'unique': NonParameterizedConstraint('unique'),
        'emailPattern': NonParameterizedConstraint('emailPattern'),
        'strongPasswordPattern': NonParameterizedConstraint('strongPasswordPattern'),
        'primaryKey': NonParameterizedConstraint('primaryKey'),
        'autoincrement': NonParameterizedConstraint('autoincrement'),
    }

    builtins = {**type_builtins, **parameterized_constraint_builtins, **non_parameterized_constraint_builtins}

    entity_mm = metamodel_from_file(join(this_folder, metamodel_filename),
                                    classes=[
                                        SimpleType,
                                        ParameterizedConstraint,
                                        NonParameterizedConstraint,
                                        ConcreteParameterizedConstraint, 
                                        ConcreteNonParameterizedConstraint, 
                                        Property, 
                                        Entity, 
                                        Relationship,
                                        Config,
                                        ConfigProp,
                                        InjectedField,
                                        Application
                                    ],
                                    builtins=builtins)

    return entity_mm

def semantic_analysis(application_model):
    supported_frontends = ['react']
    if not application_model.configObject.frontend in supported_frontends:
        raise Exception(f'Frontend {application_model.configObject.frontend} is not supported. Choose one from list: {supported_frontends}')

    if application_model.configObject.frontendPort < 1024 or application_model.configObject.frontendPort > 49151:
        raise Exception(f'Frontend port {application_model.configObject.frontendPort} is not supported. Choose value between 1024 and 49151')

    supported_servers = ['express']
    if not application_model.configObject.server in supported_servers:
        raise Exception(f'Server {application_model.configObject.server} is not supported. Choose one from list: {supported_servers}')

    if application_model.configObject.serverPort < 1024 or application_model.configObject.serverPort > 49151:
        raise Exception(f'Server port {application_model.configObject.serverPort} is not supported. Choose value between 1024 and 49151')

    supported_dbs = ['sqlite']
    if not application_model.configObject.database in supported_dbs:
        raise Exception(f'Database {application_model.configObject.database} is not supported. Choose one from list: {supported_dbs}')    

    supported_authentications = ['noAuth', 'jwt']
    if not application_model.configObject.authentication in supported_authentications:
        raise Exception(f'Authentication {application_model.configObject.authentication} is not supported. Choose one from list: {supported_authentications}')
    

    supported_themes = ['cerulean', 'cosmo', 'cyborg', 'darkly', 'flatly', 'journal', 'litera', 'lumen', 'lux', 'materia', 'minty', 'morph', 'pulse', 'quartz', 'sandstone', 'simplex', 'sketchy', 'slate', 'solar', 'spacelab', 'superhero', 'united', 'vapor', 'yeti', 'zephyr']
    if not application_model.configObject.bootstrap in supported_themes:
        raise Exception(f'Bootstrap theme {application_model.configObject.bootstrap} is not supported. Choose one from list: {supported_themes}')

    added_entities = [entity.name for entity in application_model.entities]
    if not application_model.authObject.userEntity in added_entities:
        raise Exception(f'Authentication entity {application_model.authObject.userEntity} is not defined. Choose one from list: {added_entities}')
    authEntity = [entity for entity in application_model.entities if entity.name == application_model.authObject.userEntity][0]
    authEntityFields = [field.name for field in authEntity.properties]

    if not application_model.authObject.usernameProp in authEntityFields:
        raise Exception(f'Authentication entity username property {application_model.authObject.usernameProp} is not defined. Choose one from list: {authEntityFields}')
    if not application_model.authObject.passwordProp in authEntityFields:
        raise Exception(f'Authentication entity password property{ application_model.authObject.passwordProp} is not defined. Choose one from list: {authEntityFields}')
    
    


if __name__ == "__main__":
    entity_mm = get_entity_mm()
    application_model = entity_mm.model_from_file(join(this_folder, model_filename))
    semantic_analysis(application_model)

    srcgen_folder = join(this_folder, 'srcgen')
    if not exists(srcgen_folder):
        mkdir(srcgen_folder)

    sqlite_generator = SqliteGenerator(applicationToDto(application_model), srcgen_folder, abspath(model_filename))
    sqlite_generator.generate_code()

    express_generator = ExpressGenerator(applicationToDto(application_model), srcgen_folder, abspath(model_filename))
    express_generator.generate_code()



    react_generator = ReactGenerator(applicationToDto(application_model), srcgen_folder, abspath(model_filename))
    react_generator.generate_code()

    metamodel_export(entity_mm, 'metamodel.dot')
    model_export(application_model, 'model.dot')


