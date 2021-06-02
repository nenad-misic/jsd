class Config():
    def __init__(self, configProps, parent=None):
        self.configProps = configProps
        self.parent = parent
    
    def __str__(self):
        return f"Config props: {str(len(self.configProps))}"
