class Auth():
    def __init__(self, authProps, parent=None):
        self.authProps = authProps
        self.parent = parent
    
    def __str__(self):
        return f"Auth props: {str(len(self.authProps))}"
