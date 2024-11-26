class NotError(Exception):
    def __init__(self):
        super().__init__("Não é um erro!")
