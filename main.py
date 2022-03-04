from flask import Flask, render_template, request, redirect, url_for, session
import os
import db
from models import Producto, Proveedor, Usuario, Cliente, Compras
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import seaborn as sns


app = Flask(__name__)


# funcion home
@app.route("/")
def home():
    if not session.get('logged_in'):
        return render_template('index.html')
    # Se carga  el  template  index.html


# funcion para crear usuario general
@app.route("/register")
def homeUsuario():
    return render_template("register.html")


# funcion para los cliente, inviamos tambien todos los productos que se pueden comprar
@app.route("/client/<email_usuario>")
def homeClient(email_usuario):
    cliente = db.session.query(Cliente).filter_by(email=email_usuario).first()
    todos_los_productos = db.session.query(Producto).all()
    return render_template("client.html", cliente=cliente, todos_los_productos=todos_los_productos)


# funcion por el admin, TO DO
@app.route("/admin/<email_usuario>")
def homeAdmin(email_usuario):
    usuario = db.session.query(Usuario).filter_by(email=email_usuario).first()
    todos_los_productos = db.session.query(Producto).all()
    todos_los_proveedores = db.session.query(Proveedor).all()
    todos_los_clientes = db.session.query(Cliente).all()
    todas_las_compras = db.session.query(Compras).all()

    return render_template("admin.html",
                           admin=usuario,
                           todos_los_productos=todos_los_productos,
                           todos_los_proveedores=todos_los_proveedores,
                           todos_los_clientes=todos_los_clientes,
                           todas_las_compras=todas_las_compras)


# funcion que non envia a la pagina principal para el proveedor
# enviamos los datos del proveedor, y los productos relacionados con el
@app.route("/proveedor/<email_usuario>")
def homeProveedor(email_usuario):
    proveedor = db.session.query(Proveedor).filter_by(email=email_usuario).first()
    todos_los_productos = db.session.query(Producto).filter_by(id_provedor=proveedor.id).all()

    return render_template("provider.html", proveedor=proveedor, todos_los_productos=todos_los_productos)


# funcion que non envia a la pagina de las estadisticas para el admin
# enviamos la email del admin
@app.route("/stats-admin/<email_admin>")
def lookShopStats(email_admin):
    admin = db.session.query(Usuario).filter_by(email=email_admin).first()
    todos_los_productos = db.session.query(Producto).all()
    todas_las_compras = db.session.query(Compras).all()

    global data_stats
    global data_stats_ventas
    global data_stats_producto
    global lista_cantidad_producto_comprado
    global lista_nombre_producto_comprado
    global lista_cantidad_producto_comprado
    global lista_nombre_producto
    global lista_categoria_producto

    data_stats = {}
    data_stats_ventas = {}
    data_stats_producto = {}
    lista_cantidad_producto_comprado = []
    lista_nombre_producto_comprado = []
    lista_categoria_producto_comprado = []
    lista_nombre_producto = []
    lista_categoria_producto = []

    for compra in todas_las_compras:
        compra_nombre = compra.nombre_producto
        compra_categoria = compra.categoria_producto
        compra_cantidad = compra.cantidad
        lista_cantidad_producto_comprado.append(compra_cantidad)
        lista_nombre_producto_comprado.append(compra_nombre)
        lista_categoria_producto_comprado.append(compra_categoria)
        data_stats.update({"nombre_producto_comprado": lista_nombre_producto_comprado,
                           "categoria_producto_comprado": lista_categoria_producto_comprado,
                           "cantidad_producto_comprado": lista_cantidad_producto_comprado})
        data_stats_ventas.update({"nombre_producto_comprado": lista_nombre_producto_comprado,
                           "categoria_producto_comprado": lista_categoria_producto_comprado,
                           "cantidad_producto_comprado": lista_cantidad_producto_comprado})

    for producto in todos_los_productos:
        nombre_producto = producto.nombre
        categoria_producto = producto.categoria
        lista_nombre_producto.append(nombre_producto)
        lista_categoria_producto.append(categoria_producto)
        data_stats.update({"nombre_producto_vendido": lista_nombre_producto,
                           "categoria_producto_vendido": lista_categoria_producto})
        data_stats_producto.update({"nombre_producto_vendido": lista_nombre_producto,
                                    "categoria_producto_vendido": lista_categoria_producto})

    # dataframe de los productos en la tienda
    df_productos = pd.DataFrame(data_stats_producto)

    # dataframe de las ventas en la tienda
    df_compras = pd.DataFrame(data_stats_ventas)
    # ragrupamos por nombre productos
    df_nombre_compra_group = df_compras.groupby(by='nombre_producto_comprado').sum()
    # hacemos un dataframe con el index de ese nuevo dataframe, que son los nombres de los productos
    dataframe_nombre_compra = df_nombre_compra_group.index.values
    # ragrupamos por categoria de los productos comprados
    df_categoria_compra_group = df_compras.groupby(by='categoria_producto_comprado').sum()
    # hacemos un dataframe con el index de ese nuevo dataframe, que son las categorias de los productos
    dataframe_categoria_compra = df_categoria_compra_group.index.values

    # convertimos en array la cantidad de los productos comprados segun el nombre
    cantidad_nombre_producto_comprado = df_nombre_compra_group['cantidad_producto_comprado'].tolist()
    # convertimos en array los nombres de los productos
    nombre_producto_comprado = dataframe_nombre_compra.tolist()
    # convertimos en array la cantidad de los productos comprados segun la categoria
    cantidad_categoria_producto_comprado = df_categoria_compra_group['cantidad_producto_comprado'].tolist()
    # convertimos en array las categorias de los productos
    categoria_producto_comprado = dataframe_categoria_compra.tolist()

    chart_bar_nombre_vs_cantidad_url = createBarChartNombreCantidad(nombre_producto_comprado,
                                                                    cantidad_nombre_producto_comprado)

    chart_pie_nombre_vs_cantidad_url = createPieChartNombreCantidad(nombre_producto_comprado,
                                                                    cantidad_nombre_producto_comprado)

    chart_bar_categoria_vs_cantidad_url = createBarChartNombreCantidad(categoria_producto_comprado,
                                                                       cantidad_categoria_producto_comprado)

    chart_pie_categoria_vs_cantidad_url = createPieChartCategoriaCantidad(categoria_producto_comprado,
                                                                          cantidad_categoria_producto_comprado)

    return render_template("statsAdmin.html",
                           admin=admin,
                           chart_bar_nombre_vs_cantidad_url=chart_bar_nombre_vs_cantidad_url,
                           chart_bar_categoria_vs_cantidad_url=chart_bar_categoria_vs_cantidad_url,
                           chart_pie_nombre_vs_cantidad_url=chart_pie_nombre_vs_cantidad_url,
                           chart_pie_categoria_vs_cantidad_url=chart_pie_categoria_vs_cantidad_url)


# bar chart por el nombre de los productos comprados y sus cantidades
def createBarChartNombreCantidad(nombre_producto_comprado, cantidad_nombre_producto_comprado):
    imgBarA = BytesIO()
    sns.set_style("darkgrid")
    barA = plt
    barA.figure(figsize=(10, 6), facecolor='#DBCECE')

    barA.bar(nombre_producto_comprado,
             cantidad_nombre_producto_comprado,
             width=0.3)

    barA.ylabel("Cantidad")
    barA.legend()
    barA.savefig(imgBarA, format='png')
    barA.close()
    imgBarA.seek(0)
    chart_bar_nombre_vs_cantidad_url = base64.b64encode(imgBarA.getvalue()).decode('utf8')
    return chart_bar_nombre_vs_cantidad_url


# bar chart por la categoria de los productos comprados y sus cantidades
def createBarChartCategoriaCantidad(categoria_producto_comprado, cantidad_categoria_producto_comprado):
    imgBarB = BytesIO()
    sns.set_style("lightgrid")
    barB = plt
    barB.figure(figsize=(10, 6), facecolor='#DBCECE')
    barB.ylabel("Cantidad")

    barB.bar(categoria_producto_comprado,
             cantidad_categoria_producto_comprado,
             # color='green',
             width=0.3)

    barB.legend()
    barB.savefig(imgBarB, format='png')
    barB.close()
    imgBarB.seek(0)
    chart_bar_categoria_vs_cantidad_url = base64.b64encode(imgBarB.getvalue()).decode('utf8')
    return chart_bar_categoria_vs_cantidad_url


# pie chart por el nombre de los productos comprados y sus cantidades
def createPieChartNombreCantidad(nombre_producto_comprado, cantidad_nombre_producto_comprado):
    imgPieA = BytesIO()
    pieA = plt
    fig = plt.figure(figsize=(10, 6), facecolor='#DBCECE')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('equal')
    pieA.pie(cantidad_nombre_producto_comprado,
            labels=nombre_producto_comprado,
            autopct='%1.1f%%')
    pieA.legend()
    pieA.savefig(imgPieA, format='png')
    pieA.close()
    imgPieA.seek(0)
    chart_pie_nombre_vs_cantidad_url = base64.b64encode(imgPieA.getvalue()).decode('utf8')
    return chart_pie_nombre_vs_cantidad_url


# pie chart por la categoria de los productos comprados y sus cantidades
def createPieChartCategoriaCantidad(categoria_producto_comprado, cantidad_categoria_producto_comprado):
    imgPieB = BytesIO()
    pieB = plt
    fig = plt.figure(figsize=(10, 6), facecolor='#DBCECE')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('equal')
    pieB.pie(cantidad_categoria_producto_comprado,
            labels=categoria_producto_comprado,
            autopct='%1.2f%%')
    pieB.legend()
    pieB.savefig(imgPieB, format='png')
    pieB.close()
    imgPieB.seek(0)
    chart_pie_categoria_vs_cantidad_url = base64.b64encode(imgPieB.getvalue()).decode('utf8')
    return chart_pie_categoria_vs_cantidad_url


# funcion para la pagina de los productos comprados del cliente
@app.route("/client-orders/<id_cliente>")
def lookClientOrders(id_cliente):
    cliente = db.session.query(Cliente).filter_by(id=int(id_cliente)).first()
    id_cliente = cliente.id
    todas_las_compras = db.session.query(Compras).filter_by(id_comprador=int(id_cliente)).all()
    global lista_productos
    lista_productos = []
    for producto_comprado in todas_las_compras:
        id_producto_comprado = producto_comprado.id_producto
        producto = db.session.query(Producto).filter_by(id=int(id_producto_comprado)).first()
        lista_productos.append(producto)
        # lista_productos.append(producto_comprado.cantidad)

    return render_template("comprasCliente.html", cliente=cliente, lista_productos=lista_productos)


# funcion para la pagina register, nos envia a la home
@app.route("/back-register")
def backRegister():
    return redirect(url_for("home"))


# funcion para la pagina creacion producto, nos envia a la home del proveedor
@app.route("/back-create-edit/<email_proveedor>")
def backCreate(email_proveedor):
    proveedor = db.session.query(Proveedor).filter_by(email=email_proveedor).first()
    email_proveedor = proveedor.email
    return redirect(url_for("homeProveedor", email_usuario=email_proveedor))


# funcion para la pagina cabar compra, nos envia a la home del cliente
@app.route("/back-client-home/<id_cliente>")
def backClient(id_cliente):
    cliente = db.session.query(Cliente).filter_by(id=int(id_cliente)).first()
    email_cliente = cliente.email
    return redirect(url_for("homeClient", email_usuario=email_cliente))


# funcion para la pagina cabar compra, nos envia a la home del cliente
@app.route("/back-admin-home/<email_admin>")
def backAdmin(email_admin):
    admin = db.session.query(Usuario).filter_by(email=email_admin).first()
    email_admin = admin.email
    return redirect(url_for("homeAdmin", email_usuario=email_admin))


# funcion para el boton crear en la home proveedor
# nos envia a la pagina para crear un producto y envia los datos del proveedor
@app.route("/crear/<id_provedor>")
def crear(id_provedor):
    proveedor = db.session.query(Proveedor).filter_by(id=int(id_provedor)).first()
    return render_template("createProduct.html", proveedor=proveedor)


# funcion para el boton editar en la home proveedor
# nos envia a la pagina para editar un producto y envia los datos del proveedor y del producto seleccionado
@app.route("/editar/<id_producto><id_proveedor>")
def editar(id_producto, id_proveedor):
    producto = db.session.query(Producto).filter_by(id=int(id_producto)).first()
    proveedor = db.session.query(Proveedor).filter_by(id=int(id_proveedor)).first()
    return render_template("editProduct.html", productoSeleccionado=producto, proveedor=proveedor)


# funcion de login
# aqui sacamos todos lo usuarios y controlamos si la email y la password son iguales
# segun el tipo del usuario lo renviamos a su home
@app.route("/login", methods=['POST'])
def login():
    todos_los_usuarios = db.session.query(Usuario).all()
    email = request.form['email_usuario']
    password = request.form['password_usuario']
    error_general = False
    error_password = False
    error_both = False
    error_mail = False
    if todos_los_usuarios:
        for usuario in todos_los_usuarios:
            if ((email == usuario.email) and (password == usuario.password)):
                if (usuario.tipo_usuario == 'Cliente'):
                    session['logged_in'] = True
                    if (usuario.datas == 1):
                        email_usuario = usuario.email
                        return redirect(url_for("homeClient", email_usuario=email_usuario))
                    else:
                        return render_template("createClient.html", usuario=usuario)
                elif (usuario.tipo_usuario == 'Administrador'):
                    session['logged_in'] = True
                    email_usuario = usuario.email
                    return redirect(url_for("homeAdmin", email_usuario=email_usuario))
                elif (usuario.tipo_usuario == 'Proveedor'):
                    session['logged_in'] = True
                    if (usuario.datas == 1):
                        email_usuario = usuario.email
                        return redirect(url_for("homeProveedor", email_usuario=email_usuario))
                    else:
                        return render_template("createProvedor.html", usuario=usuario)
            elif not email and email == "" and not password and password == "":
                error_both = True
            elif not email and email == "":
                error_mail = True
            elif not password and password == "":
                error_password = True
            else:
                error_general = True
    else:
        error_general_no_users = "Los datos no son correctos"
        return render_template("index.html", error=error_general_no_users)

    if error_general:
        error_general_mensaje = "Los datos no son correctos"
        return render_template("index.html", error=error_general_mensaje)
    elif error_password:
        error_password_mensaje = "Es necesaria una password"
        return render_template("index.html", error=error_password_mensaje)
    elif error_both:
        error_both_mensaje = "Es necesaria una mail y una password"
        return render_template("index.html", error=error_both_mensaje)
    elif error_mail:
        error_mail_mensaje = "Es necesario una mail"
        return render_template("index.html", error=error_mail_mensaje)


# funcion en la pagina register para crear un nuevo usuario
# controlamos la mail y la password y renviamos a la home general para hacer el login
@app.route('/crear-usuario', methods=['POST'])
def crearUsuario():
    new_email = request.form['nueva_email']
    new_password = request.form['nueva_password']
    todos_los_usuarios = db.session.query(Usuario).all()
    for usuario in todos_los_usuarios:
        if new_email == usuario.email:
            error_mail = "Email ya utilizada"
            return render_template("register.html", error_mail=error_mail)
    if not new_email and new_email == "" and not new_password and new_password == "":
        error_both = "Es necesaria una mail y una password"
        return render_template("register.html", error_both=error_both)
    elif not new_email and new_email == "":
        error_mail = "Es necesario una mail"
        return render_template("register.html", error_mail=error_mail)
    elif not new_password and new_password == "":
        error_password = "Es necesaria una password"
        return render_template("register.html", error_password=error_password)
    else:
        nuevo_usuario = Usuario(email=new_email,
                                password=new_password,
                                tipo_usuario=request.form['nuevo_tipo'])
        message = "El usuario se ha creado correctamente"

        db.session.add(nuevo_usuario)
        db.session.commit()
        db.session.close()

    return render_template("index.html", message=message)


# funcion de logout, renviamos a la home general
@app.route("/logout", methods=['GET'])
def logout():
    session['logged_in'] = False
    return redirect(url_for("home"))


# funcion que sirve para completar los datos del proveedor
# si el usuario(proveedor) tiene el parametro datos en false y eso es obligatorio la primera vez
# despues del login reenviamos el usuairo(proveedor) en una pagina para completar sus datos
# requeremos el id para determinar el usuario y coger su email para conectar el usuario al proveedor
# reenviamos a la home general donde el usuario tendra un mensaje
# el mensaje confirma que el perfil se ha completado y ahora puede efectuar el acceso
@app.route('/crear-provedor/<id_usuario>', methods=['POST'])
def crearProvedor(id_usuario):
    usuario = db.session.query(Usuario).filter_by(id=int(id_usuario)).first()
    nombre_empresa = request.form['nombre_empresa']
    telefono_empresa = request.form['telefono_empresa']
    direccion_empresa = request.form['direccion_empresa']
    ciudad_empresa = request.form['ciudad_empresa']
    provincia_empresa = request.form['provincia_empresa']
    iva_empresa = request.form['iva_empresa']

    if not nombre_empresa and nombre_empresa == "":
        error_general = "Son necesarios todos los datos"
        return render_template("createProvedor.html", error_general=error_general)
    elif not telefono_empresa and telefono_empresa == "":
        error_general = "Son necesarios todos los datos"
        return render_template("createProvedor.html", error_general=error_general)
    elif not direccion_empresa and direccion_empresa == "":
        error_general = "Son necesarios todos los datos"
        return render_template("createProvedor.html", error_general=error_general)
    elif not ciudad_empresa and ciudad_empresa == "":
        error_general = "Son necesarios todos los datos"
        return render_template("createProvedor.html", error_general=error_general)
    elif not provincia_empresa and provincia_empresa == "":
        error_general = "Son necesarios todos los datos"
        return render_template("createProvedor.html", error_general=error_general)
    elif not iva_empresa and iva_empresa == "":
        error_general = "Son necesarios todos los datos"
        return render_template("createProvedor.html", error_general=error_general)
    else:
        proveedor = Proveedor(nombre_empresa=nombre_empresa,
                              telefono=telefono_empresa,
                              direccion=direccion_empresa,
                              email=usuario.email,
                              ciudad=ciudad_empresa,
                              provincia=provincia_empresa,
                              iva=iva_empresa)
        usuario.datas = True
        message = "Perfil completato correctamente"

    # id no es necesario asignarlo manualmente, porque la primary key se genera automaticamente
    db.session.add(proveedor)  # Añadir el objeto de Producto a la base de datos
    db.session.commit()  # Ejecutar la operación pendiente de la base de datos
    db.session.close()
    return render_template("index.html", message=message)


# funcion para crear el producto, venimos desde la funcion crear que enviaba los datos del proveedor
# en la pagina enviamos el id del proveedor que crea el producto
# creamos el producto y lo relacionamos al proveedor a traves del nombre de la empresa y del id
# cuando acabamos reenviamos el proveedor a su home y enviamos el id para que se cargen todos sus productos
@app.route('/crear-producto/<id_provedor>', methods=['POST'])
def crearProducto(id_provedor):
    proveedor = db.session.query(Proveedor).filter_by(id=int(id_provedor)).first()
    nombre = request.form['nombre_producto']
    descripcion = request.form['descripcion_producto']
    stock_maximo_str = request.form['stock_maximo_producto']
    deposito = request.form['deposito_producto']
    referencia = request.form['referencia_producto']
    categoria = request.form['categoria_producto']
    nombre_provedor = proveedor.nombre_empresa
    id_provedor = proveedor.id
    email_proveedor = proveedor.email
    precio_str = request.form['precio_producto']

    stock_maximo = int(stock_maximo_str)
    precio = float(precio_str)

    if not nombre and nombre == "":
        error_general = "Son necesarios todos los datos requeridos"
        return render_template("createProduct.html", proveedor=proveedor, error_general=error_general)
    elif not descripcion and descripcion == "":
        error_general = "Son necesarios todos los datos requeridos"
        return render_template("createProduct.html", proveedor=proveedor, error_general=error_general)
    elif not stock_maximo and stock_maximo == "":
        error_general = "Son necesarios todos los datos requeridos"
        return render_template("createProduct.html", proveedor=proveedor, error_general=error_general)
    elif not deposito and deposito == "":
        error_general = "Son necesarios todos los datos requeridos"
        return render_template("createProduct.html", proveedor=proveedor, error_general=error_general)
    elif not referencia and referencia == "":
        error_general = "Son necesarios todos los datos requeridos"
        return render_template("createProduct.html", proveedor=proveedor, error_general=error_general)
    elif not categoria and categoria == "":
        error_general = "Son necesarios todos los datos requeridos"
        return render_template("createProduct.html", proveedor=proveedor, error_general=error_general)
    elif not precio and precio == "":
        error_general = "Son necesarios todos los datos requeridos"
        return render_template("createProduct.html", proveedor=proveedor, error_general=error_general)
    elif type(precio) == str:
        error_general = "Stock tiene que ser un numero entero"
        return render_template("createProduct.html", proveedor=proveedor, error_general=error_general)
    elif type(stock_maximo) == str or type(stock_maximo) == float:
        error_general = "Stock tiene que ser un numero entero"
        return render_template("createProduct.html", proveedor=proveedor, error_general=error_general)
    else:
        stock_minimo = ((stock_maximo * 90) / 100)
        stock_minimo_int = int(stock_minimo)
        producto = Producto(nombre=nombre,
                            descripcion=descripcion,
                            stock_maximo=stock_maximo,
                            stock=stock_maximo,
                            stock_minimo=stock_minimo_int,
                            deposito=deposito,
                            referencia=referencia,
                            categoria=categoria,
                            nombre_provedor=nombre_provedor,
                            id_provedor=id_provedor,
                            precio=precio)

    # id no es necesario asignarlo manualmente, porque la primary key se genera automaticamente
    db.session.add(producto)  # Añadir el objeto de Producto a la base de datos
    db.session.commit()  # Ejecutar la operación pendiente de la base de datos
    db.session.close()
    return redirect(url_for("homeProveedor", email_usuario=email_proveedor))


@app.route('/recargar-producto/<id_producto><id_proveedor>')
def recargarProducto(id_producto, id_proveedor):
    # cojo el producto seleccionado
    producto = db.session.query(Producto).filter_by(id=int(id_producto)).first()
    proveedor = db.session.query(Proveedor).filter_by(id=int(id_proveedor)).first()
    email_proveedor = proveedor.email

    producto.stock = producto.stock_maximo

    db.session.commit()  # Ejecutar la operación pendiente de la base de datos
    db.session.close()
    return redirect(url_for("homeProveedor", email_usuario=email_proveedor))

# funcion para editar el producto
# venimos de la funcion editar que enviaba los datos del producto seleccionado y los datos del proveedor
# en la pagina de editing enviamos el id del producto que queremos editar y el id del proveedor que edita
# en esa funcion cogemos el producto querido a traves de id y lo mismo hacemos con el provedor
# una vez acabado reenviamos el proveedor a su home y junto a su id para que se cargen todos sus productos
@app.route('/editar-producto/<id_producto><id_proveedor>', methods=['POST'])
def editarProducto(id_producto, id_proveedor):
    # cojo el producto seleccionado
    producto = db.session.query(Producto).filter_by(id=int(id_producto)).first()
    proveedor = db.session.query(Proveedor).filter_by(id=int(id_proveedor)).first()
    email_proveedor = proveedor.email
    # cogemos los datos
    vieja_nombre = request.form['vieja_nombre']
    nueva_nombre = request.form['nueva_nombre']
    if nueva_nombre:
        if nueva_nombre == "" or not nueva_nombre:
            producto.nombre = vieja_nombre
        else:
            producto.nombre = nueva_nombre
    else:
        producto.nombre = vieja_nombre
    vieja_descripcion = request.form['vieja_descripcion']
    nueva_descripcion = request.form['nueva_descripcion']
    if nueva_descripcion:
        if nueva_descripcion == "" or not nueva_descripcion:
            producto.descripcion = vieja_descripcion
        else:
            producto.descripcion = nueva_descripcion
    else:
        producto.descripcion = vieja_descripcion
    vieja_stock_maximo = request.form['vieja_stock_maximo']
    nueva_stock_maximo = request.form['nueva_stock_maximo']
    if nueva_stock_maximo:
        if nueva_stock_maximo == "" or not nueva_stock_maximo:
            producto.stock_maximo = vieja_stock_maximo
            producto.stock = vieja_stock_maximo
        else:
            producto.stock_maximo = nueva_stock_maximo
            producto.stock = nueva_stock_maximo
            stock_int = int(nueva_stock_maximo)
            stock_minimo = ((stock_int * 90) / 100)
            producto.stock_minimo = stock_minimo
    else:
        producto.stock_maximo = vieja_stock_maximo
        producto.stock = vieja_stock_maximo

    vieja_deposito = request.form['vieja_deposito']
    nueva_deposito = request.form['nueva_deposito']
    if nueva_deposito:
        if nueva_deposito == "" or not nueva_deposito:
            producto.deposito = vieja_deposito
        else:
            producto.deposito = nueva_deposito
    else:
        producto.deposito = vieja_deposito
    vieja_referencia = request.form['vieja_referencia']
    nueva_referencia = request.form['nueva_referencia']
    if nueva_referencia:
        if nueva_referencia == "" or not nueva_referencia:
            producto.referencia = vieja_referencia
        else:
            producto.referencia = nueva_referencia
    else:
        producto.referencia = vieja_referencia
    vieja_categoria = request.form['vieja_categoria']
    nueva_categoria = request.form['nueva_categoria']
    if nueva_categoria:
        if nueva_categoria == "" or not nueva_categoria:
            producto.categoria = vieja_categoria
        else:
            producto.categoria = nueva_categoria
    else:
        producto.categoria = vieja_categoria
    vieja_provedor = request.form['vieja_provedor']
    nueva_provedor = request.form['nueva_provedor']
    if nueva_provedor:
        if nueva_provedor == "" or not nueva_provedor:
            producto.provedor = vieja_provedor
        else:
            producto.provedor = nueva_provedor
    else:
        producto.provedor = vieja_provedor
    vieja_precio = request.form['vieja_precio']
    nueva_precio = request.form['nueva_precio']
    if nueva_precio:
        if nueva_precio == "" or not nueva_precio:
            producto.precio = vieja_precio
        else:
            producto.precio = nueva_precio
    else:
        producto.precio = vieja_precio

    db.session.commit()
    # Ejecutar la operación pendiente de la base de datos
    db.session.close()
    return redirect(url_for('homeProveedor', email_usuario=email_proveedor))


# funcion para eliminar un producto
# enviamos el id del producto para determinar cual quereos eliminar
# reenviamos a la home del proveedor con el id para que se carguen todos sus productos
@app.route('/eliminar-producto/<id_producto><id_proveedor>')
def eliminarProducto(id_producto, id_proveedor):
    producto = db.session.query(Producto).filter_by(id=int(id_producto)).first()
    producto.activo = False
    proveedor = db.session.query(Proveedor).filter_by(id=int(id_proveedor)).first()
    email_proveedor = proveedor.email
    # Se busca dentro de la base de datos, aquel registro cuyo id coincida con el aportado por el parametro de la ruta. Cuando se encuentra se elimina
    db.session.commit()
    # Ejecutar la operación pendiente de la base de datos
    db.session.close()
    return redirect(url_for('homeProveedor', email_usuario=email_proveedor))
    # Esto nos redirecciona a la función home() y si ha ido bien, al refrescar, la tarea eliminada ya no aparecera en el listado


# funcion que sirve para completar los datos del cliente
# si el usuario(cliente) tiene el parametro datos en false y eso es obligatorio la primera vez
# despues del login reenviamos el usuairo(cliente) en una pagina para completar sus datos
# requeremos el id para determinar el usuario y coger su email para conectar el usuario al cliente
# reenviamos a la home general donde el usuario tendra un mensaje
# el mensaje confirma que el perfil se ha completado y ahora puede efectuar el acceso
@app.route('/crear-cliente/<id_usuario>', methods=['POST'])
def crearCliente(id_usuario):
    usuario = db.session.query(Usuario).filter_by(id=int(id_usuario)).first()
    nombre_cliente = request.form['nombre_cliente']
    apellido_cliente = request.form['apellido_cliente']
    telefono_cliente = request.form['telefono_cliente']
    direccion_cliente = request.form['direccion_cliente']
    ciudad_cliente = request.form['ciudad_cliente']
    provincia_cliente = request.form['provincia_cliente']

    if not nombre_cliente and nombre_cliente == "":
        error_general = "Son necesarios todos los datos"
        return render_template("createProvedor.html", error_general=error_general)
    elif not apellido_cliente and apellido_cliente == "":
        error_general = "Son necesarios todos los datos"
        return render_template("createProvedor.html", error_general=error_general)
    elif not telefono_cliente and telefono_cliente == "":
        error_general = "Son necesarios todos los datos"
        return render_template("createProvedor.html", error_general=error_general)
    elif not direccion_cliente and direccion_cliente == "":
        error_general = "Son necesarios todos los datos"
        return render_template("createProvedor.html", error_general=error_general)
    elif not ciudad_cliente and ciudad_cliente == "":
        error_general = "Son necesarios todos los datos"
        return render_template("createProvedor.html", error_general=error_general)
    elif not provincia_cliente and provincia_cliente == "":
        error_general = "Son necesarios todos los datos"
        return render_template("createProvedor.html", error_general=error_general)
    else:
        cliente = Cliente(nombre=nombre_cliente,
                          apellido=apellido_cliente,
                          email=usuario.email,
                          telefono=telefono_cliente,
                          direccion=direccion_cliente,
                          ciudad=ciudad_cliente,
                          provincia=provincia_cliente)
        usuario.datas = True
        message = "Perfil completato correctamente"

    # id no es necesario asignarlo manualmente, porque la primary key se genera automaticamente
    db.session.add(cliente)  # Añadir el objeto de Producto a la base de datos
    db.session.commit()  # Ejecutar la operación pendiente de la base de datos
    db.session.close()
    return render_template("index.html", message=message)


@app.route("/buy-redirect/<email_comprador><id_producto>")
def buyRedirect(email_comprador, id_producto):
    # con todos_los_productos cogemos cual producto hemos elegido
    todos_los_productos = db.session.query(Producto).filter_by(id=int(id_producto)).first()
    precio_producto = todos_los_productos.precio
    # con cliente cogemos cual cliente esta comprando
    cliente = db.session.query(Cliente).filter_by(email=email_comprador).first()
    # con precio enviamos el precio de ese producto que se ha comprado
    precio = precio_producto
    return render_template("comprar.html", producto=todos_los_productos, cliente=cliente, precio=precio)


# funcion que non envia a la pagina para cerrar la compra
# enviamos los datos del proveedor, y los productos relacionados con el
@app.route("/comprar/<email_comprador><id_producto>", methods=["POST"])
def comprar(email_comprador, id_producto):
    # con todos_los_productos cogemos cual producto hemos elegido
    todos_los_productos = db.session.query(Producto).filter_by(id=id_producto).first()
    producto_comprado = todos_los_productos.id
    nombre_producto = todos_los_productos.nombre
    categoria_producto = todos_los_productos.categoria
    # con cliente cogemos cual cliente esta comprando
    cliente = db.session.query(Cliente).filter_by(email=email_comprador).first()
    email_comprador = cliente.email
    nombre_comprador = cliente.nombre
    apellido_comprador = cliente.apellido
    id_comprador = cliente.id
    # con cantidad enviamos la cantidad de ese producto que se ha comprado
    cantidad = request.form['cantidad_producto']
    cantidad_producto = cantidad
    if not cantidad_producto or cantidad_producto == 0:
        message = "Tienes que seleccionar una cantidad o vuelve atras"
        return render_template("comprar.html", producto=todos_los_productos, cliente=cliente, message=message)
    else:
        nueva_compra = Compras(id_producto=producto_comprado,
                               nombre_producto=nombre_producto,
                               categoria_producto=categoria_producto,
                               id_comprador=id_comprador,
                               nombre_comprador=nombre_comprador,
                               apellido_comprador=apellido_comprador,
                               cantidad=cantidad_producto)

        nuevo_stock = (int(todos_los_productos.stock) - int(cantidad_producto))
        todos_los_productos.stock = nuevo_stock


    db.session.add(nueva_compra)
    db.session.commit()
    db.session.close()
    return redirect(url_for("homeClient", email_usuario=email_comprador))


if __name__ == "__main__":
    db.Base.metadata.create_all(db.engine)  # Creamos el modelo de datos
    app.secret_key = os.urandom(12)
    app.run(debug=True)
