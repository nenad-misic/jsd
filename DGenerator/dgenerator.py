from os.path import exists, dirname, join, abspath
from os import mkdir
import sys


from textx import metamodel_from_file
from textx.export import metamodel_export, model_export


this_folder = dirname(__file__)

def get_entity_mm():
    
    entity_mm = metamodel_from_file(join(this_folder, 'metamodel/grammar.tx'))

    return entity_mm

if __name__ == "__main__":
    entity_mm = get_entity_mm()
    metamodel_export(entity_mm, 'metamodel.dot')