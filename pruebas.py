import sys
import time

from PyQt5 import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QHeaderView, QInputDialog, QMessageBox
from ventana1 import Ui_Form
from PyQt5.uic import loadUi
import sqlite3
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from PyQt5.QtGui import QTextDocument, QTextCursor, QTextTableFormat, QTextLength
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTextBrowser
import tabulate

class ClaseImportarForm(QMainWindow, Ui_Form):
    def __init__(self, parent=None):
        super(ClaseImportarForm, self).__init__(parent)
        loadUi("login.ui", self)
        self.btnIngresar.clicked.connect(self.ingresar)

    def ingresar(self):
        self.MenuPrincipal = ClaseMenuPrincipal()
        self.MenuPrincipal.show()
        self.close()


class ClaseMenuPrincipal(QMainWindow, Ui_Form):
    def __init__(self, parent=None):
        super(ClaseMenuPrincipal, self).__init__(parent)
        loadUi("menup.ui", self)


        self.stackedWidget = self.StackedWidget
        self.productosticket=[]
        self.total=0.0

        self.btnPreciosProveedor.clicked.connect(self.paginaPreciosProveedor)
        self.btnActualizar.clicked.connect(self.paginaActualizar)
        self.btnInventario.clicked.connect(self.paginaInventario)
        self.btnVender.clicked.connect(self.paginavender)
        self.nuevoProd.clicked.connect(self.agregarProducto)
        self.borrarProd.clicked.connect(self.eliminarProducto)
        self.btnActualizarInv.clicked.connect(self.actualizarInv)
        self.btnBuscarInv.clicked.connect(self.buscarInv)
        self.btnBuscarAct.clicked.connect(self.buscarAct)
        self.btnActUn.clicked.connect(self.ActUn)
        self.leVender.textChanged.connect(self.agregarAlTicket)
        self.btnEliminarVender.clicked.connect(self.eliminarUltimaFilaVender)
        self.btnProdNN.clicked.connect(self.agregarProductoNN)
        self.btnImprimirTicket.clicked.connect(self.imprimirTicket)
        self.btnIngresoManual.clicked.connect(self.ingresoManual)
        self.btnActualizarPro.clicked.connect(self.actualizarPrecios)
        self.cargarInventario()
        self.sbAumentar.setRange(0,999)
        self.sbDisminuir.setRange(0, 999)

    def cargarInventario(self):
        # Limpiar la tabla antes de cargar nuevos datos
        self.tablaInventario.clearContents()
        self.tablaInventario.setRowCount(0)

        # Conectar a la base de datos
        conn = sqlite3.connect('bbddminimercadogg.db')
        cursor = conn.cursor()

        # Obtener los nombres de las columnas
        cursor.execute("PRAGMA table_info(productos)")
        column_info = cursor.fetchall()
        column_names = [info[1] for info in column_info]

        # Ejemplo de consulta SELECT
        cursor.execute("SELECT * FROM productos")
        resultados = cursor.fetchall()

        # Cerrar la conexión
        conn.close()

        # Llenar el QTableWidget con los resultados de la consulta
        for fila in resultados:
            # Obtener la cantidad de filas actual
            fila_actual = self.tablaInventario.rowCount()

            # Agregar una nueva fila
            self.tablaInventario.insertRow(fila_actual)

            # Llenar la fila con los valores
            for columna, valor in enumerate(fila):
                item = QTableWidgetItem(str(valor))
                self.tablaInventario.setItem(fila_actual, columna, item)
        # Ajustar las columnas al contenido
        self.tablaInventario.resizeColumnsToContents()
        # Ajustar las filas al contenido
        self.tablaInventario.resizeRowsToContents()

    def actualizarPrecios(self):
        # Obtener el proveedor ingresado en el lineedit
        proveedor = self.leProveedorAct.text()

        # Verificar si se ha ingresado un proveedor
        if not proveedor:
            QMessageBox.warning(self, 'Actualizar Precios', 'Ingrese un proveedor para actualizar los precios.',
                                QMessageBox.Ok)
            return

        # Obtener el porcentaje de aumento o disminución desde los SpinBox
        porcentaje = 0
        if self.rbAumentar.isChecked():
            porcentaje = self.sbAumentar.value()
        elif self.rbDisminuir.isChecked():
            porcentaje = -self.sbDisminuir.value()


        # Conectar a la base de datos
        conn = sqlite3.connect('bbddminimercadogg.db')
        cursor = conn.cursor()

        # Obtener los productos del proveedor específico
        cursor.execute("SELECT * FROM productos WHERE proveedor=?", (proveedor,))
        productos = cursor.fetchall()
        cursor.close()
        if productos==[]:
            QMessageBox.warning(self, 'Actualizar Precios ERROR', 'El proveedor ingresado no tiene ningun producto registrado.',
                                QMessageBox.Ok)
            return

        # Conectar a la base de datos
        conn = sqlite3.connect('bbddminimercadogg.db')
        cursor = conn.cursor()

        # Obtener los productos del proveedor específico
        cursor.execute("SELECT * FROM productos WHERE proveedor=?", (proveedor,))
        productos = cursor.fetchall()

        # Actualizar los precios de los productos según el porcentaje
        for producto in productos:
            nuevo_precio = producto[4] * (1 + porcentaje / 100)
            nuevo_precio=round(nuevo_precio)
            cursor.execute("UPDATE productos SET precio=? WHERE codigo=?", (nuevo_precio, producto[0]))

        # Guardar los cambios y cerrar la conexión
        conn.commit()
        conn.close()

        # Actualizar la tabla de inventario después de la actualización
        QMessageBox.information(self, 'Actualizar Precios', 'Precios actualizados correctamente.', QMessageBox.Ok)

    def imprimirTicket(self):
        if self.tablaVender.rowCount()==0:
            QMessageBox.information(self, 'VENTA', 'No hay ningun producto en el ticket', QMessageBox.Ok)
            return

        producto, ok1 = QInputDialog.getDouble(self, 'Ingrese pago', 'Ingrese el pago:',max=9999999999999999)
        if ok1:
            pago = float(producto)
            vuelto = pago - self.total
            QMessageBox.information(self, "cambio", f"total: {self.total} pago:{pago} su vuelto: {vuelto}")


            # Crear un documento de texto
        ticket_doc = QTextDocument()
            # Configurar el formato del texto
        cursor = QTextCursor(ticket_doc)
        cursor.movePosition(QTextCursor.Start)
        # Título y subtitulo
        titulo = "Minimercado Gauchito Gil"
        subtitulo = "Ticket no válido como factura"
        cursor.insertText(f"{titulo}\n{subtitulo}\n\n")

        # Encabezados
        headers = ["Detalle", "Importe"]
        table_data = []

        # Agregar detalles de cada producto a la tabla de datos
        for row in range(self.tablaVender.rowCount()):
            producto = self.tablaVender.item(row, 0).text()
            marca = self.tablaVender.item(row, 1).text()
            descripcion = self.tablaVender.item(row, 2).text()
            precio_unitario = float(self.tablaVender.item(row, 3).text())
            cantidad = int(self.tablaVender.item(row, 4).text())
            subtotal = float(self.tablaVender.item(row, 5).text())

            # Añadir detalles a la tabla de datos
            detalle_left = f"{producto} - {marca} - {descripcion} - ${precio_unitario:.2f} - X {cantidad}"
            detalle_right = f"${subtotal:.2f}"


            table_data.append([detalle_left, detalle_right])

        column_width = 75



        # Agregar guiones al detalle para alcanzar el ancho deseado
        for row in table_data:
            detalle_left = row[0] + '-' * (column_width - len(row[0]))
            row[0] = detalle_left

        # Formatear la tabla usando tabulate y stralign para establecer el ancho
        formatted_table = tabulate.tabulate(table_data, headers, tablefmt='plain')

        cursor.insertText(formatted_table)
        cursor.insertText(f"\nTotal: ${self.total:.2f}\n")

        # Configurar la impresora
        printer = QPrinter()
        printer.setPrinterName('Impresora')
        printer.setOutputFormat(QPrinter.NativeFormat)

        # Configurar el cuadro de diálogo de impresión
        print_dialog = QPrintDialog(printer, self)
        if print_dialog.exec_() == QPrintDialog.Accepted:
            # Mostrar la vista previa antes de imprimir
            preview_dialog = QPrintPreviewDialog(printer, self)
            preview_dialog.paintRequested.connect(ticket_doc.print_)
            preview_dialog.exec_()
        # restar stock

        for producto in self.productosticket:
            codigo_producto = producto[0]
            cantidad_vendida = producto[1]


            # Conectar a la base de datos
            conn = sqlite3.connect('bbddminimercadogg.db')
            cursor = conn.cursor()

            # Obtener el stock actual del producto
            cursor.execute("SELECT cantidad FROM productos WHERE codigo=?", (codigo_producto,))

            resultado=cursor.fetchone()
            stock_actual = resultado[0]

            # Actualizar el stock restando la cantidad vendida
            nuevo_stock = stock_actual - cantidad_vendida
            cursor.execute("UPDATE productos SET cantidad=? WHERE codigo=?", (nuevo_stock, codigo_producto))

            # Guardar los cambios y cerrar la conexión
            conn.commit()
            conn.close()
            # Eliminar todas las filas de la tablaVender
            self.tablaVender.setRowCount(0)

            # También puedes restablecer el total a cero
            self.total = 0.0

            # Actualizar el texto del QLabel que muestra el total
            self.lblTotal.setText(f'$ {self.total:.2f}')

    def ingresoManual(self):
        producto, ok1 = QInputDialog.getText(self, 'Ingreso Manual', 'Ingrese el codigo del producto:')
        if ok1:
            codigo_agregar = producto

            # Validar si se ingresó el código
            if codigo_agregar:
                # Conectar a la base de datos
                conn = sqlite3.connect('bbddminimercadogg.db')
                cursor = conn.cursor()

                # Ejemplo de consulta SELECT con filtro por código
                cursor.execute("SELECT * FROM productos WHERE codigo=?", (codigo_agregar,))
                producto_encontrado = cursor.fetchone()

                # Cerrar la conexión
                conn.close()

                if producto_encontrado:
                    # Obtener la cantidad desde el SpinBox
                    cantidad = self.sbPor.value()

                    # Calcular el precio sumado
                    precio_sumado = producto_encontrado[4] * cantidad

                    # Obtener los datos del producto excluyendo la primera columna (código)
                    datos_producto = producto_encontrado[1:]

                    # Agregar el producto al ticket
                    fila_actual = self.tablaVender.rowCount()
                    self.tablaVender.insertRow(fila_actual)

                    for columna, valor in enumerate(datos_producto):
                        item = QTableWidgetItem(str(valor))
                        self.tablaVender.setItem(fila_actual, columna, item)

                    # Añadir la cantidad y el precio sumado a las columnas correspondientes
                    self.tablaVender.setItem(fila_actual, 4, QTableWidgetItem(str(cantidad)))
                    self.tablaVender.setItem(fila_actual, 5, QTableWidgetItem(str(precio_sumado)))

                    self.total += precio_sumado

                    # Actualizar el texto del QLabel
                    self.lblTotal.setText(f'$ {self.total:.2f}')

                    # Ajustar las columnas al contenido
                    self.tablaVender.resizeColumnsToContents()
                    # Ajustar las filas al contenido
                    self.tablaVender.resizeRowsToContents()
                    self.productosticket.append([codigo_agregar, cantidad])
                else:
                    QMessageBox.warning(self, 'Agregar al Ticket', 'Producto no encontrado.', QMessageBox.Ok)
            else:
                QMessageBox.warning(self, 'Agregar al Ticket', 'Ingrese un código para agregar al ticket.', QMessageBox.Ok)
        self.leVender.setFocus()


    def agregarProductoNN(self):
        # Obtener datos del nuevo producto mediante QInputDialog
        producto, ok1 = QInputDialog.getText(self, 'Nuevo Producto', 'Ingrese el nombre del producto:')
        precio_unitario, ok2 = QInputDialog.getDouble(self, 'Nuevo Producto', 'Ingrese el precio unitario:', 0.0, 0.0,
                                                      1000000.0)
        cantidad, ok3 = QInputDialog.getInt(self, 'Nuevo Producto', 'Ingrese la cantidad:', 0, 0, 2147483647)

        # Validar si se ingresaron todos los datos
        if ok1 and ok2 and ok3:
            # Agregar el nuevo producto a la tablaVender con espacios en blanco como guiones
            fila_actual = self.tablaVender.rowCount()
            self.tablaVender.insertRow(fila_actual)

            # Llenar la fila con los valores
            valores = [producto, '-', '-', precio_unitario, cantidad, precio_unitario * cantidad]
            for columna, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                self.tablaVender.setItem(fila_actual, columna, item)

            # Sumar el precio sumado del nuevo producto al total
            self.total += precio_unitario * cantidad

            # Actualizar el texto del QLabel
            self.lblTotal.setText(f'$ {self.total:.2f}')
            # Ajustar las columnas al contenido
            self.tablaVender.resizeColumnsToContents()
            # Ajustar las filas al contenido
            self.tablaVender.resizeRowsToContents()
        self.leVender.setFocus()

    def eliminarUltimaFilaVender(self):
        # Obtener el número de filas en la tablaVender
        num_filas = self.tablaVender.rowCount()

        # Validar que haya al menos una fila para eliminar
        if num_filas > 0:
            # Obtener el precio sumado de la última fila
            precio_sumado = float(self.tablaVender.item(num_filas - 1, 5).text())

            # Restar el precio sumado del total
            self.total -= precio_sumado

            # Actualizar el texto del QLabel
            self.lblTotal.setText(f'$ {self.total:.2f}')

            # Eliminar la última fila de la tablaVender
            self.tablaVender.removeRow(num_filas - 1)
        self.leVender.setFocus()


    def agregarAlTicket(self):

        # Obtener el código del producto a agregar al ticket
        codigo_agregar = self.leVender.text()

        # Validar si se ingresó el código
        if codigo_agregar:
            # Conectar a la base de datos
            conn = sqlite3.connect('bbddminimercadogg.db')
            cursor = conn.cursor()

            # Ejemplo de consulta SELECT con filtro por código
            cursor.execute("SELECT * FROM productos WHERE codigo=?", (codigo_agregar,))
            producto_encontrado = cursor.fetchone()

            # Cerrar la conexión
            conn.close()

            if producto_encontrado:
                # Obtener la cantidad desde el SpinBox
                cantidad = self.sbPor.value()

                # Calcular el precio sumado
                precio_sumado = producto_encontrado[4] * cantidad

                # Obtener los datos del producto excluyendo la primera columna (código)
                datos_producto = producto_encontrado[1:]

                # Agregar el producto al ticket
                fila_actual = self.tablaVender.rowCount()
                self.tablaVender.insertRow(fila_actual)

                for columna, valor in enumerate(datos_producto):
                    item = QTableWidgetItem(str(valor))
                    self.tablaVender.setItem(fila_actual, columna, item)

                # Añadir la cantidad y el precio sumado a las columnas correspondientes
                self.tablaVender.setItem(fila_actual, 4, QTableWidgetItem(str(cantidad)))
                self.tablaVender.setItem(fila_actual, 5, QTableWidgetItem(str(precio_sumado)))

                self.total += precio_sumado

                # Actualizar el texto del QLabel
                self.lblTotal.setText(f'$ {self.total:.2f}')

                # Ajustar las columnas al contenido
                self.tablaVender.resizeColumnsToContents()
                # Ajustar las filas al contenido
                self.tablaVender.resizeRowsToContents()
                time.sleep(0.3)
                self.leVender.clear()
                self.productosticket.append([codigo_agregar, cantidad])
                return
            else:
                QMessageBox.warning(self, 'Agregar al Ticket', 'Producto no encontrado.', QMessageBox.Ok)
                self.leVender.clear()
                return

        self.leVender.setFocus()

    def ActUn(self):
        # Obtener el código del producto a actualizar
        codigo_actualizar = self.leActualizarUn.text()

        # Validar si se ingresó el código
        if codigo_actualizar:
            # Conectar a la base de datos
            conn = sqlite3.connect('bbddminimercadogg.db')
            cursor = conn.cursor()

            # Verificar si el producto existe antes de actualizarlo
            cursor.execute("SELECT * FROM productos WHERE codigo=?", (codigo_actualizar,))
            producto_existente = cursor.fetchone()

            if producto_existente:
                try:
                    # Obtener los nuevos datos de los campos line edits
                    nuevo_codigo = int(self.leCodigo.text())
                    nuevo_producto = self.leProducto.text()
                    nueva_marca = self.leMarca.text()
                    nueva_descripcion = self.leDescripcion.text()
                    nuevo_precio = float(self.lePrecio.text())
                    nuevo_proveedor = self.leProveedor.text()
                    nueva_cantidad = int(self.leCantidad.text())

                    # Actualizar el producto en la base de datos
                    cursor.execute(
                        "UPDATE productos SET codigo=?, producto=?, marca=?, descripcion=?, precio=?, proveedor=?, cantidad=? WHERE codigo=?",
                        (nuevo_codigo, nuevo_producto, nueva_marca, nueva_descripcion, nuevo_precio, nuevo_proveedor,
                         nueva_cantidad, codigo_actualizar))

                    # Guardar los cambios y cerrar la conexión
                    conn.commit()
                    conn.close()

                    # Mostrar mensaje de éxito
                    QMessageBox.information(self, 'Actualizar Producto', 'Producto actualizado correctamente.',
                                            QMessageBox.Ok)

                    # Limpiar los campos después de la actualización
                    self.leCodigo.clear()
                    self.leProducto.clear()
                    self.leMarca.clear()
                    self.leDescripcion.clear()
                    self.lePrecio.clear()
                    self.leProveedor.clear()
                    self.leCantidad.clear()
                    return

                except ValueError:
                    QMessageBox.warning(self, 'Actualizar Producto', 'Ingrese valores válidos para los campos.',
                                        QMessageBox.Ok)
                    return
            else:
                QMessageBox.warning(self, 'Actualizar Producto', 'Producto no encontrado.', QMessageBox.Ok)
                return
        else:
            QMessageBox.warning(self, 'Actualizar Producto', 'Ingrese un código para buscar.', QMessageBox.Ok)
            return
        return

    def buscarAct(self):
        # Obtener el código del producto a buscar
        codigo_buscar = self.leActualizarUn.text()

        # Validar si se ingresó el código
        if codigo_buscar:
            # Conectar a la base de datos
            conn = sqlite3.connect('bbddminimercadogg.db')
            cursor = conn.cursor()

            # Ejemplo de consulta SELECT con filtro por código
            cursor.execute("SELECT * FROM productos WHERE codigo=?", (codigo_buscar,))
            producto_encontrado = cursor.fetchone()

            # Cerrar la conexión
            conn.close()

            if producto_encontrado:
                # Llenar los campos correspondientes con los datos del producto
                self.leCodigo.setText(str(producto_encontrado[0]))
                self.leProducto.setText(str(producto_encontrado[1]))
                self.leMarca.setText(str(producto_encontrado[2]))
                self.leDescripcion.setText(str(producto_encontrado[3]))
                self.lePrecio.setText(str(producto_encontrado[4]))
                self.leProveedor.setText(str(producto_encontrado[5]))
                self.leCantidad.setText(str(producto_encontrado[6]))
            else:
                QMessageBox.warning(self, 'Buscar Producto', 'Producto no encontrado.', QMessageBox.Ok)
        else:
            QMessageBox.warning(self, 'Buscar Producto', 'Ingrese un código para buscar.', QMessageBox.Ok)

    def buscarInv(self):
        # Limpiar la tabla antes de insertar el producto buscado
        self.tablaInventario.setRowCount(0)

        # Obtener el código del producto a buscar
        codigo_buscar = self.leCodigInv.text()

        # Validar si se ingresó el código
        if codigo_buscar:
            # Conectar a la base de datos
            conn = sqlite3.connect('bbddminimercadogg.db')
            cursor = conn.cursor()

            # Ejemplo de consulta SELECT con filtro por código
            cursor.execute("SELECT * FROM productos WHERE codigo=?", (codigo_buscar,))
            producto_encontrado = cursor.fetchone()

            # Cerrar la conexión
            conn.close()

            if producto_encontrado:
                # Agregar el producto encontrado a la tabla
                fila_actual = self.tablaInventario.rowCount()
                self.tablaInventario.insertRow(fila_actual)

                for columna, valor in enumerate(producto_encontrado):
                    item = QTableWidgetItem(str(valor))
                    self.tablaInventario.setItem(fila_actual, columna, item)

                # Ajustar las columnas al contenido
                self.tablaInventario.resizeColumnsToContents()
                # Ajustar las filas al contenido
                self.tablaInventario.resizeRowsToContents()
            else:
                QMessageBox.warning(self, 'Buscar Producto', 'Producto no encontrado.', QMessageBox.Ok)
        else:
            QMessageBox.warning(self, 'Buscar Producto', 'Ingrese un código para buscar.', QMessageBox.Ok)

    def actualizarInv(self):
        # Limpiar la tabla antes de insertar las filas actualizadas
        self.tablaInventario.setRowCount(0)

        # Conectar a la base de datos
        conn = sqlite3.connect('bbddminimercadogg.db')
        cursor = conn.cursor()

        # Ejemplo de consulta SELECT
        cursor.execute("SELECT * FROM productos")
        resultados = cursor.fetchall()

        # Cerrar la conexión
        conn.close()

        # Llenar el QTableWidget con los resultados de la consulta
        for fila in resultados:
            # Obtener la cantidad de filas actual
            fila_actual = self.tablaInventario.rowCount()

            # Agregar una nueva fila
            self.tablaInventario.insertRow(fila_actual)

            # Llenar la fila con los valores
            for columna, valor in enumerate(fila):
                item = QTableWidgetItem(str(valor))
                self.tablaInventario.setItem(fila_actual, columna, item)

        # Ajustar las columnas al contenido
        self.tablaInventario.resizeColumnsToContents()
        # Ajustar las filas al contenido
        self.tablaInventario.resizeRowsToContents()

    def agregarProducto(self):
        # Obtener datos del nuevo producto mediante QInputDialog
        codigo_texto, ok1 = QInputDialog.getText(self, 'Nuevo Producto', 'Ingrese el código:')

        # Intentar convertir el código a un entero
        try:
            codigo = int(codigo_texto)
        except ValueError:
            # Manejar el caso en que la conversión a entero falle
            QMessageBox.warning(self, 'Error', 'El código debe ser un número entero.')
            return

        producto, ok2 = QInputDialog.getText(self, 'Nuevo Producto', 'Ingrese el nombre del producto:')
        marca, ok3 = QInputDialog.getText(self, 'Nuevo Producto', 'Ingrese la marca:')
        descripcion, ok4 = QInputDialog.getText(self, 'Nuevo Producto', 'Ingrese la descripción:')
        precio, ok5 = QInputDialog.getDouble(self, 'Nuevo Producto', 'Ingrese el precio:', 0.0, 0.0, 1000000.0)
        proveedor, ok6 = QInputDialog.getText(self, 'Nuevo Producto', 'Ingrese el proveedor:')
        cantidad, ok7 = QInputDialog.getInt(self, 'Nuevo Producto', 'Ingrese la cantidad:', 0, 0, 2147483647)

        # Validar si se ingresaron todos los datos
        if ok1 and ok2 and ok3 and ok4 and ok5 and ok6 and ok7:
            # Conectar a la base de datos
            conn = sqlite3.connect('bbddminimercadogg.db')
            cursor = conn.cursor()

            # Ejemplo de consulta INSERT
            cursor.execute(
                "INSERT INTO productos (codigo, producto, marca, descripcion, precio, proveedor, cantidad) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (codigo, producto, marca, descripcion, precio, proveedor, cantidad))

            # Guardar los cambios y cerrar la conexión
            conn.commit()
            conn.close()

            # Actualizar la tabla después de agregar el nuevo producto
            self.paginaInventario()

    def eliminarProducto(self):
        # Obtener el código del producto a eliminar mediante QInputDialog
        codigo, ok = QInputDialog.getText(self, 'Eliminar Producto', 'Ingrese el código del producto a eliminar:')

        # Validar si se ingresó el código
        if ok:
            # Conectar a la base de datos
            conn = sqlite3.connect('bbddminimercadogg.db')
            cursor = conn.cursor()

            # Verificar si el producto existe antes de eliminarlo
            cursor.execute("SELECT * FROM productos WHERE codigo=?", (codigo,))
            producto_existente = cursor.fetchone()

            if producto_existente:
                # Confirmar la eliminación con un QMessageBox
                respuesta = QMessageBox.question(self, 'Eliminar Producto',
                                                 '¿Está seguro de que desea eliminar este producto?',
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

                if respuesta == QMessageBox.Yes:
                    # Ejemplo de consulta DELETE
                    cursor.execute("DELETE FROM productos WHERE codigo=?", (codigo,))

                    # Guardar los cambios y cerrar la conexión
                    conn.commit()
                    conn.close()

                    # Actualizar la tabla después de eliminar el producto
                    self.paginaInventario()
            else:
                QMessageBox.warning(self, 'Eliminar Producto', 'Producto no encontrado.', QMessageBox.Ok)

    def paginaPreciosProveedor(self):
        self.stackedWidget.setCurrentIndex(0)

    def paginaActualizar(self):
        self.stackedWidget.setCurrentIndex(1)

    def paginaInventario(self):
        self.cargarInventario()
        self.stackedWidget.setCurrentIndex(2)

    def paginavender(self):
        self.stackedWidget.setCurrentIndex(3)


def main():
    app = QApplication(sys.argv)
    ventana = ClaseImportarForm()
    ventana.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
