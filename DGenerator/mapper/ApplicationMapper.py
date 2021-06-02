from classes.Application import Application
from classes.SimpleType import SimpleType
from classes.ConcreteNonParameterizedConstraint import ConcreteNonParameterizedConstraint
from classes.ConcreteParameterizedConstraint import ConcreteParameterizedConstraint
from classes.Entity import Entity
from classes.NonParameterizedConstraint import NonParameterizedConstraint
from classes.ParameterizedConstraint import ParameterizedConstraint
from classes.Property import Property
from classes.Relationship import Relationship
from classes.Config import Config
from classes.ConfigProp import ConfigProp
from classes.InjectedField import InjectedField

def applicationToDto(model):
    configProps = [ConfigProp(configProp.configPropName, configProp.value) for configProp in model.config.configProps]
    config = Config(configProps)

    entities = []
    for entity in model.entities:
        properties = []
        for prop in entity.properties:
            constraints = []
            for constraint in prop.constraints:
                if isinstance(constraint, ConcreteNonParameterizedConstraint):
                    constraints.append(ConcreteNonParameterizedConstraint(NonParameterizedConstraint(constraint.nonParameterizedConstraint.name)))
                elif isinstance(constraint, ConcreteParameterizedConstraint):
                    constraints.append(ConcreteParameterizedConstraint(ParameterizedConstraint(constraint.parameterizedConstraint.name), constraint.value))
                else:
                    raise Exception('Constraint type invalid.')
            properties.append(Property(prop.name, prop.type, constraints))
        entities.append(Entity(entity.name, properties))

    relationships = []
    for relationship in model.relationships:
        source = next((entity for entity in entities if entity.name == relationship.source.name), None)
        target = next((entity for entity in entities if entity.name == relationship.target.name), None)
        relationships.append(Relationship(relationship.relationshipType, source, relationship.sourceInjectedField, target, relationship.targetInjectedField))

    application = Application(model.name, config, entities, relationships)
    return application