class Generator():
    def __init__(self, model, srcgen_folder, model_filename):
        self.model = model
        self.srcgen_folder = srcgen_folder
        self.model_filename = model_filename

    def generate_code(self):
        raise NotImplementedError('Abstract method generate_code in Generator class.')