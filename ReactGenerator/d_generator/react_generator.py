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

this_folder = dirname(__file__)

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

class ReactGenerator(Generator):
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
        
    def generateEmptyFile(self, filename):
        with open(join(self.srcgen_folder, filename), 'w') as f:
            f.write('')

    def generate_code(self):

        jinja_env = jinja2.Environment(
            loader=jinja2.FunctionLoader(load_template),
            trim_blocks=True,
            lstrip_blocks=True)

        
        jinja_env.filters['strftime'] = lambda x: x.strftime("%d.%m.%Y %H:%M:%S")
        jinja_env.filters['lowercase'] = lambda x: x.lower()
        jinja_env.filters['replace_'] = lambda x: x.replace('_', ' ')
        jinja_env.filters['firstUppercase'] = lambda x: x.capitalize()
        jinja_env.filters['primaryKeyProp'] = _getPrimaryKeyProperty
        jinja_env.filters['propsExceptPk'] = _getAllPropsExceptPrimaryKey
        
        
        self.generateFolder('react')
        self.generateFolder('react/public')
        self.generateFolder('react/src')
        self.generateFolder('react/src/Environment')
        self.generateFolder('react/src/Services')
        self.generateFolder('react/src/Services/autogenerated')

        # Generating package.json
        template = jinja_env.get_template('packagejson.jinja')
        self.generateModelTemplate(template, 'react/package.json')
        template = jinja_env.get_template('env.jinja')
        self.generateModelTemplate(template, 'react/.env')

        # Generating gitignore
        template = jinja_env.get_template('gitignore.jinja')
        self.generateModelTemplate(template, 'react/.gitignore')

        
        # Generating index.css
        self.generateEmptyFile('react/public/index.css')


        # Generating index.html
        template = jinja_env.get_template('indexhtml.jinja')
        self.generateModelTemplate(template, 'react/public/index.html')

        
        # Generating App.js
        template = jinja_env.get_template('appjs.jinja')
        self.generateModelTemplate(template, 'react/src/App.js')

        # Generating index.js
        template = jinja_env.get_template('indexjs.jinja')
        self.generateModelTemplate(template, 'react/src/index.js')

        
        # Generating reportWebVitals.js, serviceWorker.js and setupTests.js
        template = jinja_env.get_template('reportWebVitalsjs.jinja')
        self.generateModelTemplate(template, 'react/src/reportWebVitals.js')
        template = jinja_env.get_template('serviceWorkerjs.jinja')
        self.generateModelTemplate(template, 'react/src/serviceWorker.js')
        template = jinja_env.get_template('setupTestsjs.jinja')
        self.generateModelTemplate(template, 'react/src/setupTests.js')

        # Generating src/index.css
        self.generateEmptyFile('react/src/index.css')


        # Generating environment.js
        template = jinja_env.get_template('environmentjs.jinja')
        self.generateModelTemplate(template, 'react/src/Environment/environment.js')

        # Generating src/NavBar
        self.generateFolder('react/src/NavBar')
        template = jinja_env.get_template('Components/NavBar.jinja')
        self.generateModelTemplate(template, 'react/src/NavBar/NavBar.js')

        # Generating src/Welcome
        self.generateFolder('react/src/Welcome')
        template = jinja_env.get_template('Components/Welcome.jinja')
        self.generateModelTemplate(template, 'react/src/Welcome/Welcome.js')

        for entity in self.model.entities:

            # Generating baseServices
            template = jinja_env.get_template('autogenerated/baseEntityService.jinja')
            self.generateEntityTemplate(template, f'react/src/Services/autogenerated/base_{entity.name.lower()}Service.js', entity)
            
            # Generating services
            template = jinja_env.get_template('Services/entityService.jinja')
            self.generateEntityTemplate(template, f'react/src/Services/{entity.name.lower()}_service.js', entity)
