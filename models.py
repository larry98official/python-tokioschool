import db
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


class Usuario(db.Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)

    email = Column(String(50), nullable=False)

    password = Column(String(50), nullable=False)

    tipo_usuario = Column(String(50), nullable=False)

    datas = Column(Boolean, nullable=False)

    def __init__(self, email, password, tipo_usuario, datas=False):
        # Recordemos que el id no es necesario crearlo manualmente, lo añade la base de datos automaticamente

        self.email = email

        self.password = password

        self.tipo_usuario = tipo_usuario

        self.datas = datas

        def __repr__(self):
            return "Usuario {}, {}, {}".format(self.id, self.email, self.password)

        def __str__(self):
            return "Usuario {}, {}, {}".format(self.id, self.email, self.password)


class Proveedor(db.Base):
    __tablename__ = "proveedores"

    id = Column(Integer, primary_key=True, autoincrement=True)  # Identificador único de cada producto (no puede haber dos productos con el mismo id, por eso es primary key)

    nombre_empresa = Column(String(50), nullable=False)

    telefono = Column(Integer, nullable=False)

    direccion = Column(String(50), nullable=False)

    email = Column(String, ForeignKey("usuarios.email"))

    ciudad = Column(String(50), nullable=False)

    provincia = Column(String(50), nullable=False)

    iva = Column(String(50), nullable=False)

    def __init__(self, nombre_empresa, telefono, direccion, email, ciudad, provincia, iva):
        # Recordemos que el id no es necesario crearlo manualmente, lo añade la base de datos automaticamente

        self.nombre_empresa = nombre_empresa

        self.telefono = telefono

        self.direccion = direccion

        self.email = email

        self.ciudad = ciudad

        self.provincia = provincia

        self.iva = iva

        def __repr__(self):
            return "Proveedor {}, {}, {}".format(self.id, self.nombre_empresa, self.email)

        def __str__(self):
            return "Proveedor {}, {}, {}".format(self.id, self.nombre_empresa, self.email)


class Cliente(db.Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, autoincrement=True)

    nombre = Column(String(50), nullable=False)

    apellido = Column(String(50), nullable=False)

    email = Column(String, ForeignKey("usuarios.email"))

    telefono = Column(Integer, nullable=False)

    direccion = Column(String(50), nullable=False)

    ciudad = Column(String(50), nullable=False)

    provincia = Column(String(50), nullable=False)

    def __init__(self, nombre, apellido, email, telefono, direccion, ciudad, provincia):
        # Recordemos que el id no es necesario crearlo manualmente, lo añade la base de datos automaticamente

        self.nombre = nombre

        self.apellido = apellido

        self.email = email

        self.telefono = telefono

        self.direccion = direccion

        self.ciudad = ciudad

        self.provincia = provincia

        def __repr__(self):
            return "Cliente {}, {}, {}".format(self.id, self.nombre, self.email)

        def __str__(self):
            return "Cliente {}, {}, {}".format(self.id, self.nombre, self.email)


class Admin(db.Base):
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True, autoincrement=True)

    email = Column(String, ForeignKey("usuarios.email"))

    def __init__(self, email):
        # Recordemos que el id no es necesario crearlo manualmente, lo añade la base de datos automaticamente

        self.email = email

        def __repr__(self):
            return "Admin {}, {}".format(self.id, self.email)

        def __str__(self):
            return "Admin {}, {}".format(self.id, self.email)


class Producto(db.Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, autoincrement=True)  # Identificador único de cada producto (no puede haber dos productos con el mismo id, por eso es primary key)

    nombre = Column(String(200), nullable=False)

    descripcion = Column(String(200), nullable=False)  # descripcion del producto, un texto de máximo 200 caracteres

    stock_maximo = Column(Integer, nullable=False)

    stock = Column(Integer, nullable=False)

    stock_minimo = Column(Integer, nullable=False)

    deposito = Column(String(50), nullable=False)

    referencia = Column(String(50), nullable=False)

    categoria = Column(String(50), nullable=False)

    nombre_provedor = Column(String, ForeignKey("proveedores.nombre_empresa"))

    id_provedor = Column(Integer, ForeignKey("proveedores.id"))

    precio = Column(Integer, nullable=False)

    activo = Column(Boolean, nullable=False)

    def __init__(self, nombre, descripcion, stock_maximo, stock, stock_minimo, deposito, referencia, categoria, nombre_provedor, id_provedor, precio, activo=True):
        # Recordemos que el id no es necesario crearlo manualmente, lo añade la base de datos automaticamente

        self.nombre = nombre

        self.descripcion = descripcion

        self.stock_maximo = stock_maximo

        self.stock = stock

        self.stock_minimo = stock_minimo

        self.deposito = deposito

        self.referencia = referencia

        self.categoria = categoria

        self.nombre_provedor = nombre_provedor

        self.id_provedor = id_provedor

        self.precio = precio

        self.activo = activo

        def __repr__(self):
            return "Producto {}, {}, {}".format(self.id, self.nombre, self.precio)

        def __str__(self):
            return "Producto {}, {}, {}".format(self.id, self.nombre, self.precio)


class Compras(db.Base):
    __tablename__ = "compras"

    id = Column(Integer, primary_key=True, autoincrement=True)

    id_producto = Column(Integer, ForeignKey("productos.id"))

    nombre_producto = Column(String(50), ForeignKey("productos.nombre"))

    categoria_producto = Column(String(50), ForeignKey("productos.categoria"))

    id_comprador = Column(Integer, ForeignKey("clientes.id"))

    nombre_comprador = Column(String(50), ForeignKey("clientes.nombre"))

    apellido_comprador = Column(String(50), ForeignKey("clientes.apellido"))

    cantidad = Column(Integer, nullable=False)

    def __init__(self, id_producto, nombre_producto, categoria_producto, id_comprador, nombre_comprador, apellido_comprador, cantidad):
        # Recordemos que el id no es necesario crearlo manualmente, lo añade la base de datos automaticamente

        self.id_producto = id_producto

        self.nombre_producto = nombre_producto

        self.categoria_producto = categoria_producto

        self.id_comprador = id_comprador

        self.nombre_comprador = nombre_comprador

        self.apellido_comprador = apellido_comprador

        self.cantidad = cantidad

        def __repr__(self):
            return "Compras {}, {}, {}, {}".format(self.id, self.id_producto, self.id_comprador, self.cantidad)

        def __str__(self):
            return "Compras {}, {}, {}, {}".format(self.id, self.id_producto, self.id_comprador, self.cantidad)