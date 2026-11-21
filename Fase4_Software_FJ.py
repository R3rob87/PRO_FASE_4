"""UNAD - Programación 213023 - Fase 4.
Sistema integral de clientes, servicios y reservas de Software FJ.
Solo usa la biblioteca estándar; los datos viven en memoria.
Ejecutar: python Fase4_Software_FJ.py
Pruebas automáticas: python Fase4_Software_FJ.py --demo
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
import logging
import sys
import tkinter as tk
from tkinter import ttk, messagebox

# Archivo de eventos y errores; no almacena datos de clientes ni reservas.
LOG_PATH = Path(__file__).with_name('software_fj.log')
logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                    format='%(asctime)s | %(levelname)s | %(message)s', encoding='utf-8')


class ErrorSistema(Exception):
    """Clase base para los errores controlados de la aplicación."""


class DatosInvalidos(ErrorSistema):
    """Se produce cuando una entrada no supera las validaciones."""


class ServicioNoDisponible(ErrorSistema):
    """Se produce cuando no hay disponibilidad para un servicio."""


class ReservaInvalida(ErrorSistema):
    """Se produce cuando una reserva tiene un estado u operación incorrectos."""


def numero_positivo(valor, nombre):
    """Convierte una entrada a Decimal y rechaza cero, negativos y NaN.

    'raise ... from ...' muestra el encadenamiento de excepciones.
    """
    try:
        n = Decimal(str(valor).strip())
    except (InvalidOperation, ValueError, TypeError) as error:
        raise DatosInvalidos(f'{nombre} debe ser numérico.') from error
    if not n.is_finite() or n <= 0:
        raise DatosInvalidos(f'{nombre} debe ser mayor que cero.')
    return n


def porcentaje(valor, nombre):
    """Valida un porcentaje entre 0 y 100."""
    try:
        n = Decimal(str(valor).strip())
    except (InvalidOperation, ValueError, TypeError) as error:
        raise DatosInvalidos(f'{nombre} debe ser numérico.') from error
    if not n.is_finite() or not 0 <= n <= 100:
        raise DatosInvalidos(f'{nombre} debe estar entre 0 y 100.')
    return n


def dinero(n):
    """Redondea un importe monetario a dos decimales."""
    return n.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class Entidad(ABC):
    """Abstracción general: todas las entidades tienen un identificador."""
    def __init__(self, identificador):
        self._id = str(identificador).strip()
        if not self._id:
            raise DatosInvalidos('El identificador es obligatorio.')

    @property
    def identificador(self):
        return self._id

    @abstractmethod
    def describir(self):
        """Devuelve una descripción de la entidad."""


class Cliente(Entidad):
    """Encapsula datos personales mediante atributos privados y propiedades."""
    def __init__(self, identificador, nombre, correo):
        super().__init__(identificador)
        self.__nombre = ''
        self.__correo = ''
        self.nombre = nombre
        self.correo = correo

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        valor = str(valor).strip()
        if len(valor) < 3 or not any(c.isalpha() for c in valor):
            raise DatosInvalidos('El nombre debe contener al menos 3 caracteres y letras.')
        self.__nombre = valor

    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, valor):
        valor = str(valor).strip()
        if valor.count('@') != 1 or '.' not in valor.split('@')[-1] or ' ' in valor:
            raise DatosInvalidos('El correo electrónico no es válido.')
        self.__correo = valor

    def describir(self):
        return f'{self.identificador} | {self.nombre} | {self.correo}'


class Servicio(Entidad, ABC):
    """Contrato abstracto de todos los servicios de Software FJ."""
    def __init__(self, identificador, nombre, tarifa, disponible=True):
        super().__init__(identificador)
        self.nombre = str(nombre).strip()
        if not self.nombre:
            raise DatosInvalidos('El nombre del servicio es obligatorio.')
        self.tarifa = numero_positivo(tarifa, 'La tarifa')
        self.disponible = bool(disponible)

    @abstractmethod
    def validar_parametros(self, duracion):
        """Verifica que la duración sea compatible con el servicio."""

    @abstractmethod
    def calcular_base(self, duracion):
        """Calcula el costo sin impuestos ni descuentos."""

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        """Simula sobrecarga con argumentos opcionales.

        Ejemplos: calcular_costo(2), calcular_costo(2, 19),
        calcular_costo(2, impuesto=19, descuento=10).
        """
        self.validar_parametros(duracion)
        iva = porcentaje(impuesto, 'El impuesto')
        rebaja = porcentaje(descuento, 'El descuento')
        base = self.calcular_base(duracion)
        total = base * (Decimal(1) - rebaja / 100) * (Decimal(1) + iva / 100)
        if total < 0:
            raise DatosInvalidos('El costo no puede ser negativo.')
        return dinero(total)

    def describir(self):
        return f'{self.identificador} | {self.nombre} | ${self.tarifa} por hora'


class Sala(Servicio):
    """Reserva de sala: máximo 8 horas por reserva."""
    def __init__(self, identificador, tarifa, capacidad):
        super().__init__(identificador, 'Reserva de sala', tarifa)
        self.capacidad = int(numero_positivo(capacidad, 'La capacidad'))

    def validar_parametros(self, duracion):
        horas = numero_positivo(duracion, 'La duración')
        if horas > 8:
            raise DatosInvalidos('La sala se reserva por máximo 8 horas.')

    def calcular_base(self, duracion):
        return self.tarifa * numero_positivo(duracion, 'La duración')

    def describir(self):
        return super().describir() + f' | Capacidad: {self.capacidad}'


class Equipo(Servicio):
    """Alquiler de equipos: máximo 72 horas por reserva."""
    def __init__(self, identificador, tarifa, tipo_equipo):
        super().__init__(identificador, 'Alquiler de equipo', tarifa)
        self.tipo_equipo = str(tipo_equipo).strip()
        if not self.tipo_equipo:
            raise DatosInvalidos('Debe indicar el tipo de equipo.')

    def validar_parametros(self, duracion):
        if numero_positivo(duracion, 'La duración') > 72:
            raise DatosInvalidos('El equipo se alquila por máximo 72 horas.')

    def calcular_base(self, duracion):
        return self.tarifa * numero_positivo(duracion, 'La duración')

    def describir(self):
        return super().describir() + f' | Equipo: {self.tipo_equipo}'


class Asesoria(Servicio):
    """Asesoría especializada: máximo 6 horas por reserva."""
    def __init__(self, identificador, tarifa, especialidad):
        super().__init__(identificador, 'Asesoría especializada', tarifa)
        self.especialidad = str(especialidad).strip()
        if not self.especialidad:
            raise DatosInvalidos('Debe indicar la especialidad.')

    def validar_parametros(self, duracion):
        if numero_positivo(duracion, 'La duración') > 6:
            raise DatosInvalidos('La asesoría dura máximo 6 horas.')

    def calcular_base(self, duracion):
        return self.tarifa * numero_positivo(duracion, 'La duración')

    def describir(self):
        return super().describir() + f' | Especialidad: {self.especialidad}'


class Reserva(Entidad):
    """Integra un cliente, un servicio, duración, estado y costo."""
    def __init__(self, identificador, cliente, servicio, duracion, impuesto=0, descuento=0):
        super().__init__(identificador)
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
            raise DatosInvalidos('La reserva requiere un cliente y un servicio válidos.')
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = numero_positivo(duracion, 'La duración')
        self.impuesto = porcentaje(impuesto, 'El impuesto')
        self.descuento = porcentaje(descuento, 'El descuento')
        self.estado = 'Pendiente'
        self.costo = Decimal('0.00')

    def procesar(self):
        """Usa try/except/finally y mantiene el estado consistente ante errores."""
        try:
            if self.estado != 'Pendiente':
                raise ReservaInvalida('Solo se pueden procesar reservas pendientes.')
            if not self.servicio.disponible:
                raise ServicioNoDisponible('El servicio no está disponible.')
            costo = self.servicio.calcular_costo(self.duracion, self.impuesto, self.descuento)
        except ErrorSistema:
            logging.exception('Error al procesar reserva %s', self.identificador)
            raise
        else:
            self.costo = costo
            self.estado = 'Procesada'
            logging.info('Reserva procesada: %s, costo: %s', self.identificador, costo)
            return costo
        finally:
            logging.info('Fin de intento de procesamiento: %s', self.identificador)

    def confirmar(self):
        if self.estado != 'Procesada':
            raise ReservaInvalida('Solo se puede confirmar una reserva procesada.')
        self.estado = 'Confirmada'
        logging.info('Reserva confirmada: %s', self.identificador)

    def cancelar(self):
        if self.estado == 'Cancelada':
            raise ReservaInvalida('La reserva ya está cancelada.')
        self.estado = 'Cancelada'
        logging.info('Reserva cancelada: %s', self.identificador)

    def describir(self):
        return (f'{self.identificador} | {self.cliente.nombre} | {self.servicio.nombre} | '
                f'{self.duracion} h | {self.estado} | ${self.costo}')


class SistemaFJ:
    """Mantiene las listas de objetos; no usa bases de datos."""
    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def agregar_cliente(self, identificador, nombre, correo):
        if any(c.identificador == str(identificador).strip() for c in self.clientes):
            raise DatosInvalidos('Ya existe un cliente con esa identificación.')
        cliente = Cliente(identificador, nombre, correo)
        self.clientes.append(cliente)
        logging.info('Cliente registrado: %s', cliente.identificador)
        return cliente

    def agregar_servicio(self, tipo, identificador, tarifa, detalle):
        if any(s.identificador == str(identificador).strip() for s in self.servicios):
            raise DatosInvalidos('Ya existe un servicio con ese identificador.')
        tipos = {'Sala': Sala, 'Equipo': Equipo, 'Asesoría': Asesoria}
        if tipo not in tipos:
            raise DatosInvalidos('Tipo de servicio desconocido.')
        servicio = tipos[tipo](identificador, tarifa, detalle)
        self.servicios.append(servicio)
        logging.info('Servicio registrado: %s', servicio.identificador)
        return servicio

    def crear_reserva(self, id_cliente, id_servicio, duracion, impuesto=0, descuento=0):
        cliente = next((c for c in self.clientes if c.identificador == id_cliente), None)
        servicio = next((s for s in self.servicios if s.identificador == id_servicio), None)
        if cliente is None or servicio is None:
            raise ReservaInvalida('Cliente o servicio no encontrado.')
        reserva = Reserva(f'R{len(self.reservas) + 1:03}', cliente, servicio,
                          duracion, impuesto, descuento)
        reserva.procesar()  # Si falla, no se agrega una reserva incompleta.
        self.reservas.append(reserva)
        return reserva

    def buscar_reserva(self, identificador):
        reserva = next((r for r in self.reservas if r.identificador == identificador), None)
        if reserva is None:
            raise ReservaInvalida('No existe la reserva indicada.')
        return reserva


def ejecutar_demo():
    """Ejecuta 15 pruebas, incluyendo casos correctos e incorrectos.

    Cada excepción esperada se registra; el bucle sigue con la siguiente prueba.
    """
    sistema = SistemaFJ()
    casos = [
        ('Cliente válido', lambda: sistema.agregar_cliente('C1', 'Ana Pérez', 'ana@correo.com'), True),
        ('Cliente con correo inválido', lambda: sistema.agregar_cliente('C2', 'Luis Díaz', 'correo-mal'), False),
        ('Cliente duplicado', lambda: sistema.agregar_cliente('C1', 'Otro Nombre', 'otro@correo.com'), False),
        ('Segundo cliente válido', lambda: sistema.agregar_cliente('C3', 'Luis Díaz', 'luis@correo.com'), True),
        ('Sala válida', lambda: sistema.agregar_servicio('Sala', 'S1', 40000, 10), True),
        ('Equipo válido', lambda: sistema.agregar_servicio('Equipo', 'S2', 15000, 'Portátil'), True),
        ('Asesoría válida', lambda: sistema.agregar_servicio('Asesoría', 'S3', 80000, 'Python'), True),
        ('Servicio con tarifa negativa', lambda: sistema.agregar_servicio('Sala', 'S4', -1, 10), False),
        ('Reserva exitosa', lambda: sistema.crear_reserva('C1', 'S1', 2), True),
        ('Reserva con descuento e IVA', lambda: sistema.crear_reserva('C3', 'S2', 3, 19, 10), True),
        ('Reserva de asesoría', lambda: sistema.crear_reserva('C1', 'S3', 1), True),
        ('Reserva de cliente inexistente', lambda: sistema.crear_reserva('C9', 'S1', 2), False),
        ('Reserva con duración inválida', lambda: sistema.crear_reserva('C1', 'S1', -2), False),
        ('Reserva demasiado larga', lambda: sistema.crear_reserva('C1', 'S1', 12), False),
        ('Confirmación de reserva', lambda: sistema.buscar_reserva('R001').confirmar(), True),
        ('Cancelación de reserva', lambda: sistema.buscar_reserva('R002').cancelar(), True),
        ('Confirmación incorrecta', lambda: sistema.buscar_reserva('R002').confirmar(), False),
    ]
    resultados = []
    for indice, (nombre, accion, debe_funcionar) in enumerate(casos, 1):
        try:
            accion()
        except ErrorSistema as error:
            logging.exception('Caso %s: %s', indice, nombre)
            exito = not debe_funcionar
            detalle = f'Error controlado: {error}'
        except Exception as error:
            logging.exception('Error inesperado en caso %s: %s', indice, nombre)
            exito = False
            detalle = f'Error inesperado: {error}'
        else:
            exito = debe_funcionar
            detalle = 'Operación completada'
        resultados.append((indice, nombre, exito, detalle))
        print(f'{indice:02} | {"OK" if exito else "FALLO"} | {nombre}: {detalle}')
    print(f'\nResultado: {sum(r[2] for r in resultados)}/{len(resultados)} casos superados.')
    print(f'Archivo de eventos y errores: {LOG_PATH}')
    return resultados


class InterfazFJ:
    """Interfaz Tkinter que permite usar el sistema sin escribir comandos."""
    def __init__(self, ventana):
        self.sistema = SistemaFJ()
        self.ventana = ventana
        ventana.title('Software FJ - Gestión de clientes, servicios y reservas')
        ventana.geometry('1020x740')
        ventana.minsize(820, 600)
        self.estado = tk.StringVar(value='Sistema listo. Los datos se guardan solo en memoria.')
        self.crear_interfaz()

    def campo(self, padre, etiqueta, fila, valor=''):
        ttk.Label(padre, text=etiqueta).grid(row=fila, column=0, sticky='w', padx=6, pady=4)
        entrada = ttk.Entry(padre, width=25)
        entrada.insert(0, valor)
        entrada.grid(row=fila, column=1, sticky='ew', padx=6, pady=4)
        return entrada

    def crear_interfaz(self):
        ttk.Label(self.ventana, text='SOFTWARE FJ | SISTEMA INTEGRAL DE GESTIÓN',
                  font=('Arial', 16, 'bold')).pack(pady=10)
        cont = ttk.Frame(self.ventana)
        cont.pack(fill='x', padx=12)
        cont.columnconfigure((0, 1, 2), weight=1)

        clientes = ttk.LabelFrame(cont, text='1. Registrar cliente', padding=8)
        clientes.grid(row=0, column=0, sticky='nsew', padx=5)
        self.c_id = self.campo(clientes, 'Identificación', 0)
        self.c_nombre = self.campo(clientes, 'Nombre', 1)
        self.c_correo = self.campo(clientes, 'Correo', 2)
        ttk.Button(clientes, text='Registrar cliente', command=self.registrar_cliente).grid(
            row=3, column=0, columnspan=2, pady=8)

        servicios = ttk.LabelFrame(cont, text='2. Registrar servicio', padding=8)
        servicios.grid(row=0, column=1, sticky='nsew', padx=5)
        ttk.Label(servicios, text='Tipo').grid(row=0, column=0, sticky='w')
        self.s_tipo = ttk.Combobox(servicios, values=['Sala', 'Equipo', 'Asesoría'], state='readonly', width=22)
        self.s_tipo.set('Sala')
        self.s_tipo.grid(row=0, column=1, padx=6)
        self.s_id = self.campo(servicios, 'ID servicio', 1)
        self.s_tarifa = self.campo(servicios, 'Tarifa por hora', 2, '40000')
        self.s_detalle = self.campo(servicios, 'Capacidad / tipo / tema', 3, '10')
        ttk.Button(servicios, text='Registrar servicio', command=self.registrar_servicio).grid(
            row=4, column=0, columnspan=2, pady=8)

        reservas = ttk.LabelFrame(cont, text='3. Crear reserva', padding=8)
        reservas.grid(row=0, column=2, sticky='nsew', padx=5)
        self.r_cliente = self.campo(reservas, 'ID cliente', 0)
        self.r_servicio = self.campo(reservas, 'ID servicio', 1)
        self.r_horas = self.campo(reservas, 'Duración (horas)', 2, '2')
        self.r_iva = self.campo(reservas, 'Impuesto (%)', 3, '0')
        self.r_descuento = self.campo(reservas, 'Descuento (%)', 4, '0')
        ttk.Button(reservas, text='Crear y procesar', command=self.crear_reserva).grid(
            row=5, column=0, columnspan=2, pady=8)

        acciones = ttk.Frame(self.ventana)
        acciones.pack(fill='x', padx=18, pady=12)
        ttk.Label(acciones, text='ID reserva:').pack(side='left')
        self.id_reserva = ttk.Entry(acciones, width=12)
        self.id_reserva.pack(side='left', padx=5)
        ttk.Button(acciones, text='Confirmar', command=lambda: self.cambiar_estado('confirmar')).pack(side='left', padx=5)
        ttk.Button(acciones, text='Cancelar', command=lambda: self.cambiar_estado('cancelar')).pack(side='left', padx=5)
        ttk.Button(acciones, text='Ejecutar 17 pruebas (consola)', command=self.pruebas).pack(side='right')

        tabs = ttk.Notebook(self.ventana)
        tabs.pack(fill='both', expand=True, padx=12, pady=4)
        self.tablas = {}
        for nombre, columnas in [('Clientes', ('ID', 'Nombre', 'Correo')),
                                 ('Servicios', ('ID', 'Tipo', 'Tarifa', 'Detalle')),
                                 ('Reservas', ('ID', 'Cliente', 'Servicio', 'Horas', 'Estado', 'Costo'))]:
            marco = ttk.Frame(tabs)
            tabs.add(marco, text=nombre)
            tabla = ttk.Treeview(marco, columns=columnas, show='headings', height=10)
            for col in columnas:
                tabla.heading(col, text=col)
                tabla.column(col, width=130, anchor='center')
            tabla.pack(fill='both', expand=True)
            self.tablas[nombre] = tabla
        ttk.Label(self.ventana, textvariable=self.estado, foreground='#18477b').pack(pady=8)
        ttk.Label(self.ventana, text='Nota: al cerrar el programa se pierden los registros. Los eventos se guardan en software_fj.log.',
                  foreground='#555555').pack(pady=5)

    def ejecutar(self, accion, mensaje):
        """try/except/else: reporta fallos sin cerrar la ventana."""
        try:
            resultado = accion()
        except ErrorSistema as error:
            logging.exception('Error controlado en interfaz: %s', mensaje)
            self.estado.set(f'Error: {error}')
            messagebox.showerror('Error controlado', str(error))
        except Exception as error:
            logging.exception('Error inesperado en interfaz: %s', mensaje)
            self.estado.set('Ocurrió un error inesperado. Consulte el archivo de log.')
            messagebox.showerror('Error', 'Ocurrió un error inesperado. Revise software_fj.log.')
        else:
            self.actualizar()
            self.estado.set(mensaje)
            return resultado

    def registrar_cliente(self):
        self.ejecutar(lambda: self.sistema.agregar_cliente(
            self.c_id.get(), self.c_nombre.get(), self.c_correo.get()), 'Cliente registrado correctamente.')

    def registrar_servicio(self):
        self.ejecutar(lambda: self.sistema.agregar_servicio(
            self.s_tipo.get(), self.s_id.get(), self.s_tarifa.get(), self.s_detalle.get()),
            'Servicio registrado correctamente.')

    def crear_reserva(self):
        def accion():
            r = self.sistema.crear_reserva(self.r_cliente.get().strip(),
                self.r_servicio.get().strip(), self.r_horas.get(), self.r_iva.get(), self.r_descuento.get())
            self.id_reserva.delete(0, tk.END)
            self.id_reserva.insert(0, r.identificador)
            return r
        r = self.ejecutar(accion, 'Reserva creada y procesada correctamente.')
        if r:
            messagebox.showinfo('Reserva procesada', f'ID: {r.identificador}\nCosto total: ${r.costo}')

    def cambiar_estado(self, accion):
        def ejecutar_accion():
            r = self.sistema.buscar_reserva(self.id_reserva.get().strip())
            getattr(r, accion)()
        self.ejecutar(ejecutar_accion, f'Reserva: {accion} ejecutado correctamente.')

    def actualizar(self):
        for tabla in self.tablas.values():
            for item in tabla.get_children():
                tabla.delete(item)
        for c in self.sistema.clientes:
            self.tablas['Clientes'].insert('', 'end', values=(c.identificador, c.nombre, c.correo))
        for s in self.sistema.servicios:
            detalle = (str(s.capacidad) if isinstance(s, Sala) else
                       s.tipo_equipo if isinstance(s, Equipo) else s.especialidad)
            self.tablas['Servicios'].insert('', 'end', values=(s.identificador, s.nombre, str(s.tarifa), detalle))
        for r in self.sistema.reservas:
            self.tablas['Reservas'].insert('', 'end', values=(r.identificador, r.cliente.nombre,
                r.servicio.nombre, str(r.duracion), r.estado, str(r.costo)))

    def pruebas(self):
        resultados = ejecutar_demo()
        messagebox.showinfo('Pruebas automáticas', f'Superadas: {sum(r[2] for r in resultados)}/{len(resultados)}.\n'
                            'Los resultados detallados aparecen en la terminal de VS Code.')


if __name__ == '__main__':
    if '--demo' in sys.argv:
        resultados = ejecutar_demo()
        sys.exit(0 if all(r[2] for r in resultados) else 1)
    else:
        try:
            raiz = tk.Tk()
            InterfazFJ(raiz)
            raiz.mainloop()
        except Exception:
            logging.exception('Error grave al iniciar la aplicación')
            raise
