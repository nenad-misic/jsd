import pkg_resources
import argparse

from os.path import exists, dirname, join, abspath
from os import mkdir
import sys


from d_generator.core.classes.SimpleType import SimpleType
from d_generator.core.classes.ConcreteNonParameterizedConstraint import ConcreteNonParameterizedConstraint
from d_generator.core.classes.ConcreteParameterizedConstraint import ConcreteParameterizedConstraint
from d_generator.core.classes.Entity import Entity
from d_generator.core.classes.NonParameterizedConstraint import NonParameterizedConstraint
from d_generator.core.classes.ParameterizedConstraint import ParameterizedConstraint
from d_generator.core.classes.Property import Property
from d_generator.core.classes.Relationship import Relationship
from d_generator.core.classes.Application import Application
from d_generator.core.classes.Config import Config
from d_generator.core.classes.ConfigProp import ConfigProp
from d_generator.core.classes.InjectedField import InjectedField


from d_generator.core.mapper.ApplicationMapper import applicationToDto

from textx import metamodel_from_file, metamodel_from_str
from textx.export import metamodel_export, model_export

def load_plugins(plugin_group, plugin_params):
    plugins=[]
    for ep in pkg_resources.iter_entry_points(group=plugin_group):
        p = ep.load()
        plugin = p(*plugin_params)
        plugin.name = ep.name
        plugins.append(plugin)
    return plugins



def get_generator(generator_name, plugin_group, plugin_params):
    generators = load_plugins(plugin_group, plugin_params)
    for gen in generators:
        if gen.name == generator_name:
            return gen
    raise Exception(f'{plugin_group} {generator_name} is not supported. Choose one from list: {[gen.name for gen in generators]}')

this_folder = dirname(__file__)
# model_filename = "model/application.dgdl"
# metamodel_filename = "metamodel/grammar.tx"
    
def get_entity_mm():

    metamodel_stream = pkg_resources.resource_stream(__name__, 'metamodel/grammar.tx')
    metamodel_str = metamodel_stream.read().decode()


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

    entity_mm = metamodel_from_str(metamodel_str,
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
    # supported_frontends = ['react']
    # if not application_model.configObject.frontend in supported_frontends:
    #     raise Exception(f'Frontend {application_model.configObject.frontend} is not supported. Choose one from list: {supported_frontends}')

    if application_model.configObject.frontendPort < 1024 or application_model.configObject.frontendPort > 49151:
        raise Exception(f'Frontend port {application_model.configObject.frontendPort} is not supported. Choose value between 1024 and 49151')

    # supported_servers = ['express']
    # if not application_model.configObject.server in supported_servers:
    #     raise Exception(f'Server {application_model.configObject.server} is not supported. Choose one from list: {supported_servers}')

    if application_model.configObject.serverPort < 1024 or application_model.configObject.serverPort > 49151:
        raise Exception(f'Server port {application_model.configObject.serverPort} is not supported. Choose value between 1024 and 49151')

    # supported_dbs = ['sqlite']
    # if not application_model.configObject.database in supported_dbs:
    #     raise Exception(f'Database {application_model.configObject.database} is not supported. Choose one from list: {supported_dbs}')    

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
    

def main():

    parser = argparse.ArgumentParser(prog='d_generator')
    parser.add_argument('-m', nargs='?', help='Path to application dgdl model file')
    parser.add_argument('-s', nargs='?', help='Path to desired generation directory')

    args = parser.parse_args()

    arguments = {'model_path': args.m,
                'srcgen': args.s}

    entity_mm = get_entity_mm()
    application_model = entity_mm.model_from_file(arguments['model_path'])
    semantic_analysis(application_model)

    srcgen_folder = arguments['srcgen']
    if not exists(srcgen_folder):
        mkdir(srcgen_folder)

    # sqlite_generator = SqliteGenerator(applicationToDto(application_model), srcgen_folder, abspath(model_filename))
    # sqlite_generator.generate_code()

    # express_generator = ExpressGenerator(applicationToDto(application_model), srcgen_folder, abspath(model_filename))
    # express_generator.generate_code()

    # react_generator = ReactGenerator(applicationToDto(application_model), srcgen_folder, abspath(model_filename))
    # react_generator.generate_code()

    appDTO = applicationToDto(application_model)
    plugin_params = (appDTO, srcgen_folder, abspath(arguments['model_path']))
    
    db_generator = get_generator(appDTO.configObject.database, 'database_generator', plugin_params)
    db_generator.generate_code()
    backend_generator = get_generator(appDTO.configObject.server, 'backend_generator', plugin_params)
    backend_generator.generate_code()
    frontend_generator = get_generator(appDTO.configObject.frontend, 'frontend_generator', plugin_params)
    frontend_generator.generate_code()
    

    metamodel_export(entity_mm, 'metamodel.dot')
    model_export(application_model, 'model.dot')
    


if __name__ == "__main__":
    main("bruh")