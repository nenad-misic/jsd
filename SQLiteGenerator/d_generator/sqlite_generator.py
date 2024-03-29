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


def _getPrimaryKeyProperty(entity):
        pk = next((prop for prop in entity.properties if next((constraint for constraint in prop.constraints if (hasattr(constraint, 'nonParameterizedConstraint') and constraint.nonParameterizedConstraint.name=='primaryKey')), None) != None), None)
        if pk is None:
            raise Exception(f"Entity {entity.name} does not have primary key property.")
        return pk 

def _sqliteType(s):
    """
    Maps type names from SimpleType to Java.
    """
    return {
        'integer': 'INTEGER',
        'string': 'TEXT',
        'boolean': 'INTEGER',
        'float': 'REAL'
    }.get(s.name, s.name)

def _sqliteConstraint(constraint):
    if constraint.__class__.__name__ == 'ConcreteNonParameterizedConstraint':
        return {
            'required': 'NOT NULL',
            'unique': 'UNIQUE',
            'emailPattern': '',
            'strongPasswordPattern': '',
            'primaryKey': 'PRIMARY KEY',
            'autoincrement': 'AUTOINCREMENT'
        }.get(constraint.nonParameterizedConstraint.name, constraint.nonParameterizedConstraint.name)
    elif constraint.__class__.__name__ == 'ConcreteParameterizedConstraint':
        if isinstance(constraint.value, bool):
            defaultValue = str(int(constraint.value))
        elif isinstance(constraint.value, str):
            defaultValue = f'"{constraint.value}"' 
        else:
            defaultValue = str(constraint.value)
        
        return {
            'min': '',
            'max': '',
            'pattern': '',
            'default': 'DEFAULT ' + defaultValue
        }.get(constraint.parameterizedConstraint.name, constraint.parameterizedConstraint.name)

def load_template(name):
    template_stream = pkg_resources.resource_stream(__name__, 'template/' + name)
    template = template_stream.read().decode()
    return template
        
        

class SQLiteGenerator(Generator):
    def __init__(self, model, srcgen_folder, model_filename):
        super().__init__(model, srcgen_folder, model_filename)
    
    def prepare_model(self):

        for relationship in self.model.relationships:
            if relationship.relationshipType == "OneToOne":
                if not (relationship.targetInjectedField is None or relationship.sourceInjectedField is None):
                    # Bidirect relation
                    raise Exception('Both source and target injected fields are present. Relation cannot be bidirect.')
                if not (relationship.sourceInjectedField is None):
                    # Source has pointer to target
                    if not hasattr(relationship.source, 'relationships'):
                        relationship.source.relationships = []
                    relationship.source.relationships.append(relationship)
                elif not (relationship.targetInjectedField is None):
                    # Target has pointer to source
                    if not hasattr(relationship.target, 'relationships'):
                        relationship.target.relationships = []
                    relationship.target.relationships.append(relationship)
                else:
                    # No pointer
                    raise Exception('Neither source nor target injected fields are present. Relation invalid.')

            elif relationship.relationshipType == "OneToMany":
                if relationship.sourceInjectedField is None and not (relationship.targetInjectedField is None):
                    # Target points to source
                    if not hasattr(relationship.target, 'relationships'):
                        relationship.target.relationships = []
                    relationship.target.relationships.append(relationship)
                else:
                    raise Exception('Relation invalid. OneToMany relation needs only target injected field assigned.')

            elif relationship.relationshipType == "ManyToMany":
                if not (relationship.sourceInjectedField is None) and not (relationship.targetInjectedField is None):
                    # Both sides have pointer
                    properties = [
                        Property('id', SimpleType('integer'), [ConcreteNonParameterizedConstraint(NonParameterizedConstraint('primaryKey')),ConcreteNonParameterizedConstraint(NonParameterizedConstraint('autoincrement'))]),
                        # Property(relationship.sourceInjectedField.fieldName, getPrimaryKeyProperty(relationship.target).type, []),
                        # Property(relationship.targetInjectedField.fieldName, getPrimaryKeyProperty(relationship.source).type, []),
                    ]
                    entity = Entity(relationship.source.name + 'To' + relationship.target.name, properties)
                    entity.relationships = [
                        Relationship('OneToMany', relationship.source, None, entity, relationship.targetInjectedField),
                        Relationship('OneToMany', relationship.target, None, entity, relationship.sourceInjectedField)
                    ]
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

        jinja_env.filters['sqliteType'] = _sqliteType
        jinja_env.filters['sqliteConstraint'] = _sqliteConstraint
        jinja_env.filters['strftime'] = lambda x: x.strftime("%d.%m.%Y %H:%M:%S")
        jinja_env.filters['primaryKeyProp'] = _getPrimaryKeyProperty
        
        template = jinja_env.get_template('sqlite.jinja')

        if not exists(join(self.srcgen_folder, 'sql')):
            mkdir(join(self.srcgen_folder, 'sql'))

        with open(join(self.srcgen_folder, 'sql/schema.sql'), 'w') as f:
            f.write(template.render(application=self.model, timestamp=datetime.now(), model_filename=self.model_filename))
    