class Path:
    def __init__(self, path, method, view, **kwargs):
        self.path = path
        self.method = method
        self.view = view
        self.csrf_exempt = kwargs.get('csrf_exempt', False)
        self.auth_required = kwargs.get('auth_required', False)

    def __repr__(self):
        return f'Path: {self.path}. Method: {self.method}'

    def __eq__(self, other):
        return self.path == other.path and self.method == other.method
