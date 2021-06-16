from d_generator.core.classes.Application import Application
from d_generator.core.classes.SimpleType import SimpleType
from d_generator.core.classes.ConcreteNonParameterizedConstraint import ConcreteNonParameterizedConstraint
from d_generator.core.classes.ConcreteParameterizedConstraint import ConcreteParameterizedConstraint
from d_generator.core.classes.Entity import Entity
from d_generator.core.classes.NonParameterizedConstraint import NonParameterizedConstraint
from d_generator.core.classes.ParameterizedConstraint import ParameterizedConstraint
from d_generator.core.classes.Property import Property
from d_generator.core.classes.Relationship import Relationship
from d_generator.core.classes.Config import Config
from d_generator.core.classes.ConfigProp import ConfigProp
from d_generator.core.classes.Auth import Auth
from d_generator.core.classes.AuthProp import AuthProp
from d_generator.core.classes.InjectedField import InjectedField

def applicationToDto(model):
    configProps = [ConfigProp(configProp.configPropName, configProp.value) for configProp in model.config.configProps]
    config = Config(configProps)
    authProps = [AuthProp(authProp.authPropName, authProp.value) for authProp in model.auth.authProps]
    auth = Auth(authProps)

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

    application = Application(model.name, config, auth, entities, relationships)
    return application