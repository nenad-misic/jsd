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


from textx import metamodel_from_file
from textx.export import metamodel_export, model_export


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

if __name__ == "__main__":
    entity_mm = get_entity_mm()
    application_model = entity_mm.model_from_file(join(this_folder, model_filename))

    metamodel_export(entity_mm, 'metamodel.dot')
    model_export(application_model, 'model.dot')