class Mercedes:

    def __init__(self):
        self.estado = "reposo"
        self.x = 400
        self.y = 300

    def saludar(self):
        self.estado = "saludar"

    def izquierda(self):
        self.estado = "izquierda"
        self.x -= 10

    def derecha(self):
        self.estado = "derecha"
        self.x += 10

    def arriba(self):
        self.estado = "arriba"
        self.y -= 10

    def abajo(self):
        self.estado = "abajo"
        self.y += 10

    def saltar(self):
        self.estado = "saltar"
        self.y -= 50

    def agacharse(self):
        self.estado = "agacharse"

    def sorpresa(self):
        self.estado = "sorpresa"

    def reposo(self):
        self.estado = "reposo"