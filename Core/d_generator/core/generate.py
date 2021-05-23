import pkg_resources

def load_plugins(plugin_group):
    plugins=[]
    for ep in pkg_resources.iter_entry_points(group=plugin_group):
        p = ep.load()
        print("{} {}".format(ep.name, p))
        plugin = p()
        plugins.append(plugin)
    return plugins


def generate_frontend():
    generators = load_plugins('frontend_generator')
    print('frontend', generators)

def generate_backend():
    generators = load_plugins('backend_generator')
    print('backend', generators)

def generate_database():
    generators = load_plugins('database_generator')
    print('database', generators)

if __name__ == "__main__":
    generate_frontend()
    generate_backend()
    generate_database()