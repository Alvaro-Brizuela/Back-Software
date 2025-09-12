from typing import List, Optional

from sqlalchemy import ARRAY, Boolean, CHAR, CheckConstraint, Column, Date, DateTime, ForeignKeyConstraint, Identity, Integer, Numeric, PrimaryKeyConstraint, SmallInteger, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship
from sqlalchemy.orm.base import Mapped

Base = declarative_base()


class Afp(Base):
    __tablename__ = 'afp'
    __table_args__ = (
        PrimaryKeyConstraint('id_afp', name='afp_pkey'),
    )

    id_afp = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1))
    nombre = mapped_column(String(30))
    porcentaje_descuento = mapped_column(Numeric(5, 2))

    trabajador: Mapped[List['Trabajador']] = relationship('Trabajador', uselist=True, back_populates='afp')


class CajaCompensaciones(Base):
    __tablename__ = 'caja_compensaciones'
    __table_args__ = (
        PrimaryKeyConstraint('id_caja', name='caja_compensaciones_pkey'),
    )

    id_caja = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1))
    nombre = mapped_column(String(120))

    empresa_seguridad: Mapped[List['EmpresaSeguridad']] = relationship('EmpresaSeguridad', uselist=True, back_populates='caja_compensaciones')


class MutualSeguridad(Base):
    __tablename__ = 'mutual_seguridad'
    __table_args__ = (
        PrimaryKeyConstraint('id_mutual', name='mutual_seguridad_pkey'),
    )

    id_mutual = mapped_column(Integer)
    nombre = mapped_column(String(120))
    tipo = mapped_column(Boolean)

    empresa_seguridad: Mapped[List['EmpresaSeguridad']] = relationship('EmpresaSeguridad', uselist=True, back_populates='mutual_seguridad')


class Nacionalidad(Base):
    __tablename__ = 'nacionalidad'
    __table_args__ = (
        PrimaryKeyConstraint('id_nacionalidad', name='nacionalidad_pkey'),
    )

    id_nacionalidad = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1))
    nacionalidad = mapped_column(String(50))


class RegimenTributario(Base):
    __tablename__ = 'regimen_tributario'
    __table_args__ = (
        PrimaryKeyConstraint('id_regimen', name='regimen_tributario_pkey'),
    )

    id_regimen = mapped_column(Integer)
    descripcion = mapped_column(String(120))
    tipo = mapped_column(String(120))

    empresa_tipo: Mapped[List['EmpresaTipo']] = relationship('EmpresaTipo', uselist=True, back_populates='regimen_tributario')


class Salud(Base):
    __tablename__ = 'salud'
    __table_args__ = (
        PrimaryKeyConstraint('id_salud', name='salud_pkey'),
    )

    id_salud = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1))
    nombre = mapped_column(String(30), nullable=False)
    tipo = mapped_column(Boolean, nullable=False)

    trabajador: Mapped[List['Trabajador']] = relationship('Trabajador', uselist=True, back_populates='salud')


class Territorial(Base):
    __tablename__ = 'territorial'
    __table_args__ = (
        PrimaryKeyConstraint('id_territorial', name='territorial_pkey'),
    )

    id_territorial = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1))
    region = mapped_column(String(100), nullable=False)
    provincia = mapped_column(String(100), nullable=False)
    comuna = mapped_column(String(100), nullable=False)

    empresa: Mapped[List['Empresa']] = relationship('Empresa', uselist=True, back_populates='territorial')
    usuario: Mapped[List['Usuario']] = relationship('Usuario', uselist=True, back_populates='territorial')
    trabajador: Mapped[List['Trabajador']] = relationship('Trabajador', uselist=True, back_populates='territorial')


class TipoActividad(Base):
    __tablename__ = 'tipo_actividad'
    __table_args__ = (
        PrimaryKeyConstraint('id_tipo_actividad', name='tipo_actividad_pkey'),
    )

    id_tipo_actividad = mapped_column(Integer)
    codigo = mapped_column(Integer)
    tipo_actividad = mapped_column(ARRAY(String(length=100)))
    iva = mapped_column(String(10))
    categoria_tributaria = mapped_column(String(10))
    disponible_internet = mapped_column(String(4))

    empresa_tipo: Mapped[List['EmpresaTipo']] = relationship('EmpresaTipo', uselist=True, back_populates='tipo_actividad')


class TipoSociedad(Base):
    __tablename__ = 'tipo_sociedad'
    __table_args__ = (
        PrimaryKeyConstraint('id_tipo_sociedad', name='tipo_sociedad_pkey'),
    )

    id_tipo_sociedad = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1))
    nombre = mapped_column(String(50))
    maximo_socios = mapped_column(Integer)
    maximo_giros = mapped_column(Integer)
    minimos_socios = mapped_column(Integer)
    descripcion = mapped_column(String(250))

    empresa_tipo: Mapped[List['EmpresaTipo']] = relationship('EmpresaTipo', uselist=True, back_populates='tipo_sociedad')


class Empresa(Base):
    __tablename__ = 'empresa'
    __table_args__ = (
        ForeignKeyConstraint(['id_territorial'], ['territorial.id_territorial'], name='fk_territorial_empresa'),
        PrimaryKeyConstraint('id_empresa', name='empresa_pkey')
    )

    id_empresa = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1))
    id_territorial = mapped_column(Integer)
    rut_empresa = mapped_column(Integer)
    DV_rut = mapped_column(String(1))
    nombre_real = mapped_column(String(120))
    nombre_fantasia = mapped_column(String(120))
    razon_social = mapped_column(String(120))
    giro = mapped_column(String(120))
    fecha_constitucion = mapped_column(Date)
    fecha_inicio_actividades = mapped_column(Date)
    estado_suscripcion = mapped_column(Integer)
    direccion_fisica = mapped_column(Text)
    telefono = mapped_column(String(15))
    correo = mapped_column(String(120))

    territorial: Mapped[Optional['Territorial']] = relationship('Territorial', back_populates='empresa')
    archivo_empresa: Mapped[List['ArchivoEmpresa']] = relationship('ArchivoEmpresa', uselist=True, back_populates='empresa')
    cargo: Mapped[List['Cargo']] = relationship('Cargo', uselist=True, back_populates='empresa')
    empresa_parametros: Mapped['EmpresaParametros'] = relationship('EmpresaParametros', uselist=False, back_populates='empresa')
    empresa_representante: Mapped[List['EmpresaRepresentante']] = relationship('EmpresaRepresentante', uselist=True, back_populates='empresa')
    empresa_seguridad: Mapped['EmpresaSeguridad'] = relationship('EmpresaSeguridad', uselist=False, back_populates='empresa')
    empresa_socio: Mapped[List['EmpresaSocio']] = relationship('EmpresaSocio', uselist=True, back_populates='empresa')
    empresa_tipo: Mapped['EmpresaTipo'] = relationship('EmpresaTipo', uselist=False, back_populates='empresa')
    usuario: Mapped[List['Usuario']] = relationship('Usuario', uselist=True, back_populates='empresa')
    trabajador: Mapped[List['Trabajador']] = relationship('Trabajador', uselist=True, back_populates='empresa')
    epp: Mapped[List['Epp']] = relationship('Epp', uselist=True, back_populates='empresa')


class ArchivoEmpresa(Base):
    __tablename__ = 'archivo_empresa'
    __table_args__ = (
        ForeignKeyConstraint(['id_empresa'], ['empresa.id_empresa'], name='fk_empresa_archivo'),
        PrimaryKeyConstraint('id_archivo', name='archivo_empresa_pkey')
    )

    id_archivo = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1))
    id_empresa = mapped_column(Integer)
    direccion = mapped_column(Integer)
    tipo_archivo = mapped_column(String(10))

    empresa: Mapped[Optional['Empresa']] = relationship('Empresa', back_populates='archivo_empresa')


class Cargo(Base):
    __tablename__ = 'cargo'
    __table_args__ = (
        ForeignKeyConstraint(['id_empresa'], ['empresa.id_empresa'], name='fk_empresa_cargo'),
        PrimaryKeyConstraint('id_cargo', name='cargo_pkey')
    )

    id_cargo = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1))
    nombre = mapped_column(String(120), nullable=False)
    descripcion = mapped_column(String(250), nullable=False)
    id_empresa = mapped_column(Integer)

    empresa: Mapped[Optional['Empresa']] = relationship('Empresa', back_populates='cargo')
    trabajador: Mapped[List['Trabajador']] = relationship('Trabajador', uselist=True, back_populates='cargo')


class EmpresaParametros(Base):
    __tablename__ = 'empresa_parametros'
    __table_args__ = (
        ForeignKeyConstraint(['id_empresa'], ['empresa.id_empresa'], name='fk_empresa_parametros_empresa'),
        PrimaryKeyConstraint('id', name='empresa_parametros_pkey'),
        UniqueConstraint('id_empresa', name='empresa_parametros_empresa_unq')
    )

    id = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1))
    id_empresa = mapped_column(Integer)
    descripcion_gratifiacion = mapped_column(String(120))
    valor_gratificacion = mapped_column(Numeric(12, 3))

    empresa: Mapped[Optional['Empresa']] = relationship('Empresa', back_populates='empresa_parametros')


class EmpresaRepresentante(Base):
    __tablename__ = 'empresa_representante'
    __table_args__ = (
        ForeignKeyConstraint(['id_empresa'], ['empresa.id_empresa'], name='fk_empresa_representante_empresa'),
        PrimaryKeyConstraint('id', name='empresa_representante_pkey')
    )

    id = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1))
    id_empresa = mapped_column(Integer)
    nombre_representante = mapped_column(String(40))
    apellido_paterno = mapped_column(String(50))
    apellido_materno = mapped_column(String(50))
    rut_representante_dv = mapped_column(CHAR(1))

    empresa: Mapped[Optional['Empresa']] = relationship('Empresa', back_populates='empresa_representante')


class EmpresaSeguridad(Base):
    __tablename__ = 'empresa_seguridad'
    __table_args__ = (
        ForeignKeyConstraint(['id_caja_compensacion'], ['caja_compensaciones.id_caja'], name='fk_caja_compensaciones'),
        ForeignKeyConstraint(['id_empresa'], ['empresa.id_empresa'], name='fk_empresa_seguridad_empresa'),
        ForeignKeyConstraint(['id_mutual_seguridad'], ['mutual_seguridad.id_mutual'], name='fk_mutual'),
        PrimaryKeyConstraint('id', name='empresa_seguridad_pkey'),
        UniqueConstraint('id_empresa', name='empresa_seguridad_empresa_unq')
    )

    id = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1))
    id_empresa = mapped_column(Integer)
    id_mutual_seguridad = mapped_column(Integer)
    id_caja_compensacion = mapped_column(Integer)
    tasa_mutual = mapped_column(Numeric(5, 3))
    tasa_caja = mapped_column(Numeric(5, 3))

    caja_compensaciones: Mapped[Optional['CajaCompensaciones']] = relationship('CajaCompensaciones', back_populates='empresa_seguridad')
    empresa: Mapped[Optional['Empresa']] = relationship('Empresa', back_populates='empresa_seguridad')
    mutual_seguridad: Mapped[Optional['MutualSeguridad']] = relationship('MutualSeguridad', back_populates='empresa_seguridad')


class EmpresaSocio(Base):
    __tablename__ = 'empresa_socio'
    __table_args__ = (
        ForeignKeyConstraint(['id_empresa'], ['empresa.id_empresa'], name='fk_empresa_socio_empresa'),
        PrimaryKeyConstraint('id_socio', name='empresa_socio_pkey')
    )

    id_socio = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1))
    id_empresa = mapped_column(Integer)
    nombre_socio = mapped_column(String(40))
    apellido_materno_socio = mapped_column(String(40))
    apellido_paterno_socio = mapped_column(String(40))
    aporte_total = mapped_column(Integer)
    cantidad_acciones = mapped_column(Integer)
    porcentaje_participacion = mapped_column(Integer)

    empresa: Mapped[Optional['Empresa']] = relationship('Empresa', back_populates='empresa_socio')
    pago_acciones: Mapped[List['PagoAcciones']] = relationship('PagoAcciones', uselist=True, back_populates='empresa_socio')


class EmpresaTipo(Base):
    __tablename__ = 'empresa_tipo'
    __table_args__ = (
        ForeignKeyConstraint(['id_empresa'], ['empresa.id_empresa'], name='fk_empresa_tipo_empresa'),
        ForeignKeyConstraint(['id_regimen_tributario'], ['regimen_tributario.id_regimen'], name='fk_regimen_tributario'),
        ForeignKeyConstraint(['id_tipo_actividad'], ['tipo_actividad.id_tipo_actividad'], name='fk_tipo_actividad'),
        ForeignKeyConstraint(['id_tipo_sociedad'], ['tipo_sociedad.id_tipo_sociedad'], name='fk_tipo_sociedad'),
        PrimaryKeyConstraint('id', name='empresa_tipo_pkey'),
        UniqueConstraint('id_empresa', name='empresa_tipo_empresa_unq')
    )

    id = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1))
    id_empresa = mapped_column(Integer)
    id_tipo_sociedad = mapped_column(Integer)
    id_tipo_propiedad = mapped_column(Integer)
    id_tipo_actividad = mapped_column(Integer)
    id_regimen_tributario = mapped_column(Integer)

    empresa: Mapped[Optional['Empresa']] = relationship('Empresa', back_populates='empresa_tipo')
    regimen_tributario: Mapped[Optional['RegimenTributario']] = relationship('RegimenTributario', back_populates='empresa_tipo')
    tipo_actividad: Mapped[Optional['TipoActividad']] = relationship('TipoActividad', back_populates='empresa_tipo')
    tipo_sociedad: Mapped[Optional['TipoSociedad']] = relationship('TipoSociedad', back_populates='empresa_tipo')


class Usuario(Base):
    __tablename__ = 'usuario'
    __table_args__ = (
        ForeignKeyConstraint(['id_empresa'], ['empresa.id_empresa'], ondelete='CASCADE', name='fk_usuario_empresa'),
        ForeignKeyConstraint(['id_territorial'], ['territorial.id_territorial'], name='fk_usuario_territorial'),
        PrimaryKeyConstraint('id_usuario', name='usuario_pkey')
    )

    id_usuario = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1))
    id_empresa = mapped_column(Integer)
    id_territorial = mapped_column(Integer)
    nombre = mapped_column(String(40))
    apellido_paterno = mapped_column(String(50))
    apellido_materno = mapped_column(String(50))
    direccion_exacta = mapped_column(String(100))

    empresa: Mapped[Optional['Empresa']] = relationship('Empresa', back_populates='usuario')
    territorial: Mapped[Optional['Territorial']] = relationship('Territorial', back_populates='usuario')
    login_usuario: Mapped[List['LoginUsuario']] = relationship('LoginUsuario', uselist=True, back_populates='usuario')


class LoginUsuario(Base):
    __tablename__ = 'login_usuario'
    __table_args__ = (
        ForeignKeyConstraint(['id_usuario'], ['usuario.id_usuario'], ondelete='CASCADE', name='fk_usuario'),
        PrimaryKeyConstraint('id_login', name='login_usuario_pkey')
    )

    id_login = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1))
    telefono = mapped_column(String(15), nullable=False)
    correo = mapped_column(String(150), nullable=False)
    password = mapped_column(Text, nullable=False)
    id_usuario = mapped_column(Integer)
    tipo_usuario = mapped_column(SmallInteger)
    email_verificado_at = mapped_column(DateTime(True))
    email_verificacion_hash = mapped_column(CHAR(64))
    email_verificacion_expira = mapped_column(DateTime(True))

    usuario: Mapped[Optional['Usuario']] = relationship('Usuario', back_populates='login_usuario')
    sesiones: Mapped[List['Sesiones']] = relationship('Sesiones', uselist=True, back_populates='login_usuario')


class PagoAcciones(Base):
    __tablename__ = 'pago_acciones'
    __table_args__ = (
        ForeignKeyConstraint(['id_socio'], ['empresa_socio.id_socio'], name='fk_socio'),
        PrimaryKeyConstraint('id', name='pago_acciones_pkey')
    )

    id = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1))
    id_socio = mapped_column(Integer)
    cantidad_acciones = mapped_column(Integer)
    forma_pago = mapped_column(String(100))
    descripcion_forma_pago = mapped_column(String(250))

    empresa_socio: Mapped[Optional['EmpresaSocio']] = relationship('EmpresaSocio', back_populates='pago_acciones')


class Trabajador(Base):
    __tablename__ = 'trabajador'
    __table_args__ = (
        ForeignKeyConstraint(['id_afp'], ['afp.id_afp'], name='fk_afp'),
        ForeignKeyConstraint(['id_cargo'], ['cargo.id_cargo'], name='fk_cargo'),
        ForeignKeyConstraint(['id_empresa'], ['empresa.id_empresa'], name='fk_trabajador_empresa'),
        ForeignKeyConstraint(['id_salud'], ['salud.id_salud'], name='fk_salud'),
        ForeignKeyConstraint(['id_territorial'], ['territorial.id_territorial'], name='fk_trabajador_territorial'),
        PrimaryKeyConstraint('id_trabajador', name='trabajador_pkey')
    )

    id_trabajador = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1))
    id_empresa = mapped_column(Integer, nullable=False)
    id_afp = mapped_column(Integer, nullable=False)
    id_territorial = mapped_column(Integer, nullable=False)
    id_cargo = mapped_column(Integer)
    id_salud = mapped_column(Integer)

    afp: Mapped['Afp'] = relationship('Afp', back_populates='trabajador')
    cargo: Mapped[Optional['Cargo']] = relationship('Cargo', back_populates='trabajador')
    empresa: Mapped['Empresa'] = relationship('Empresa', back_populates='trabajador')
    salud: Mapped[Optional['Salud']] = relationship('Salud', back_populates='trabajador')
    territorial: Mapped['Territorial'] = relationship('Territorial', back_populates='trabajador')
    contrato: Mapped[List['Contrato']] = relationship('Contrato', uselist=True, back_populates='trabajador')
    licencia: Mapped[List['Licencia']] = relationship('Licencia', uselist=True, back_populates='trabajador')


class ContactoTrabajador(Trabajador):
    __tablename__ = 'contacto_trabajador'
    __table_args__ = (
        ForeignKeyConstraint(['id_trabajador'], ['trabajador.id_trabajador'], name='fk_trabajador_contacto'),
        PrimaryKeyConstraint('id_trabajador', name='contacto_trabajador_pkey')
    )

    id_trabajador = mapped_column(Integer)
    corrreo_principal = mapped_column(String(50), nullable=False)
    celular_principal = mapped_column(String(15), nullable=False)
    correo_segundario = mapped_column(String(50))
    celular_segundario = mapped_column(String(15))


class Contrato(Base):
    __tablename__ = 'contrato'
    __table_args__ = (
        ForeignKeyConstraint(['id_trabajador'], ['trabajador.id_trabajador'], name='fk_contrato_trabajador'),
        PrimaryKeyConstraint('id_contrato', name='contrato_pkey')
    )

    id_contrato = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1))
    id_trabajador = mapped_column(Integer)
    direccion_contrato = mapped_column(Text)
    fecha_subida = mapped_column(DateTime(True))
    fecha_inicial = mapped_column(DateTime(True))
    fecha_termino = mapped_column(DateTime(True))

    trabajador: Mapped[Optional['Trabajador']] = relationship('Trabajador', back_populates='contrato')


class DatosTrabajador(Trabajador):
    __tablename__ = 'datos_trabajador'
    __table_args__ = (
        ForeignKeyConstraint(['id_trabajador'], ['trabajador.id_trabajador'], name='fk_datos_trabajador_trabajador'),
        PrimaryKeyConstraint('id_trabajador', name='datos_trabajador_pkey')
    )

    id_trabajador = mapped_column(Integer)
    nombre = mapped_column(String(40), nullable=False)
    apellido_paterno = mapped_column(String(40), nullable=False)
    apellido_materno = mapped_column(String(40), nullable=False)
    fecha_nacimiento = mapped_column(Date, nullable=False)
    rut = mapped_column(Integer, nullable=False)
    DV_rut = mapped_column(String(1), nullable=False)
    nacionalidad = mapped_column(String(50), nullable=False)
    direccion_real = mapped_column(Text, nullable=False)


class FotoPerfil(Trabajador):
    __tablename__ = 'foto_perfil'
    __table_args__ = (
        ForeignKeyConstraint(['id_trabajador'], ['trabajador.id_trabajador'], name='fk_foto_perfil_trabajador'),
        PrimaryKeyConstraint('id_trabajador', name='foto_perfil_pkey')
    )

    id_trabajador = mapped_column(Integer)
    direccion = mapped_column(Text)


class Licencia(Base):
    __tablename__ = 'licencia'
    __table_args__ = (
        ForeignKeyConstraint(['id_trabajador'], ['trabajador.id_trabajador'], name='fk_licencia_trabajador'),
        PrimaryKeyConstraint('id_licencia', name='licencia_pkey')
    )

    id_licencia = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1))
    id_trabajador = mapped_column(Integer)
    archivo = mapped_column(Text)
    fecha_inicio = mapped_column(DateTime(True))
    fecha_final = mapped_column(DateTime(True))

    trabajador: Mapped[Optional['Trabajador']] = relationship('Trabajador', back_populates='licencia')


class Epp(Base):
    __tablename__ = 'epp'
    __table_args__ = (
        ForeignKeyConstraint(['id_empresa'], ['empresa.id_empresa'], name='fk_epp_empresa'),
        PrimaryKeyConstraint('id_epp', name='epp_pkey'),
        UniqueConstraint('epp', name='epp_nombre_unique'),
        UniqueConstraint('descripcion', name='epp_descripcion_unique')
    )

    id_epp = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1))
    id_empresa = mapped_column(Integer, nullable=False)
    epp = mapped_column(String(100), nullable=False)
    descripcion = mapped_column(String(250), nullable=False)

    empresa: Mapped['Empresa'] = relationship('Empresa', back_populates='epp')

class Odi(Base):
    __tablename__ = 'odi'
    __table_args__ = (
        PrimaryKeyConstraint('id_odi', name='odi_pkey'),
        UniqueConstraint('tarea', name='odi_tarea_unique'),
    )

    id_odi = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1))
    tarea = mapped_column(String(200), nullable=False)
    riesgo = mapped_column(String(200), nullable=False)
    consecuencias = mapped_column(String(600), nullable=False)
    precaucion = mapped_column(String(600), nullable=False)


class Sesiones(Base):
    __tablename__ = 'sesiones'
    __table_args__ = (
        CheckConstraint('limite_sesion > fecha_sesion', name='chk_sesion_fechas'),
        ForeignKeyConstraint(['idusuario'], ['login_usuario.id_login'], ondelete='CASCADE', name='fk_sesiones_usuario'),
        PrimaryKeyConstraint('id', name='sesiones_pkey'),
        UniqueConstraint('tokenrefresh_hash', name='sesiones_tokenrefresh_hash_key')
    )

    id = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1))
    idusuario = mapped_column(Integer, nullable=False)
    tokenrefresh_hash = mapped_column(String(255), nullable=False)
    fecha_sesion = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    limite_sesion = mapped_column(DateTime(True), nullable=False)
    revoked_at = mapped_column(DateTime(True))
    user_agent = mapped_column(Text)
    ip = mapped_column(Text)

    login_usuario: Mapped['LoginUsuario'] = relationship('LoginUsuario', back_populates='sesiones')
