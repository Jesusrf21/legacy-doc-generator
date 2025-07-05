class Usuario:
    """Representa un usuario genérico del sistema."""

    def __init__(self, nombre, email):
        self.nombre = nombre
        self.email = email

    def saludar(self):
        """Devuelve un saludo personalizado."""
        return f"Hola, {self.nombre}"

    def despedirse(self):
        print("Hasta luego!")


class Administrador(Usuario):
    """Usuario con privilegios de administración."""

    def reiniciar_sistema(self):
        """Simula el reinicio del sistema."""
        print("Reiniciando sistema...")

    def generar_reporte(self):
        # Sin docstring
        print("Generando reporte...")

    def metodo_largo(self):
        # Este método intencionalmente es muy largo
        for i in range(25):
            print(f"Línea {i+1}")


class Auditor:
    pass  # clase sin métodos


def enviar_correo(destinatario, asunto, mensaje):
    """Simula el envío de un correo."""
    print(f"Enviando correo a {destinatario} con asunto '{asunto}'")


def funcion_sin_docstring():
    print("Esto no debería pasar desapercibido.")


def sumar(a, b):
    """Devuelve la suma de dos números."""
    return a + b


def dividir(a, b):
    """Divide dos números, sin manejo de errores."""
    return a / b
