class Usuario:
    """
    Representa a un usuario básico de la aplicación.
    """

    def __init__(self, nombre, email):
        """
        Inicializa un nuevo usuario con nombre y email.
        """
        self.nombre = nombre
        self.email = email
        self.activo = True

    def desactivar(self):
        """
        Marca al usuario como inactivo.
        """
        self.activo = False

    def mostrar_info(self):
        """
        Devuelve un resumen de los datos del usuario.
        """
        estado = "Activo" if self.activo else "Inactivo"
        return f"{self.nombre} ({self.email}) - {estado}"


class Administrador(Usuario):
    """
    Usuario con privilegios de administración.
    """

    def __init__(self, nombre, email):
        """
        Inicializa un administrador usando la clase base Usuario.
        """
        super().__init__(nombre, email)
        self.privilegios = ["moderar", "borrar usuarios", "ver estadísticas"]

    def agregar_privilegio(self, privilegio):
        """
        Añade un privilegio al administrador.
        """
        if privilegio not in self.privilegios:
            self.privilegios.append(privilegio)

    def mostrar_info(self):
        """
        Devuelve información del administrador, incluyendo privilegios.
        """
        base = super().mostrar_info()
        return base + f" | Privilegios: {', '.join(self.privilegios)}"


def crear_usuarios():
    """
    Crea una lista de usuarios de ejemplo.
    """
    u1 = Usuario("Laura", "laura@example.com")
    u2 = Usuario("Carlos", "carlos@example.com")
    u3 = Administrador("Sofía", "sofia@example.com")
    u3.agregar_privilegio("editar perfiles")

    return [u1, u2, u3]


def imprimir_resumen(usuarios):
    """
    Imprime la información de una lista de usuarios.
    """
    for usuario in usuarios:
        print(usuario.mostrar_info())


# Ejecución de ejemplo
if __name__ == "__main__":
    usuarios = crear_usuarios()
    usuarios[1].desactivar()
    imprimir_resumen(usuarios)
