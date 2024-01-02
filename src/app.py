from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
import MySQLdb 
from config import config
import csv
from flask import Response

app= Flask(__name__)

conexion = MySQL(app)

@app.route('/persona', methods=['GET'])
def listar_persona():
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT * FROM persona"
        cursor.execute(sql)
        datos = cursor.fetchall()
        personas = []

        for fila in datos:
            persona = {'id': fila[0], 'DNI': fila[1], 'NOMBRE': fila[2], 'APELLIDO': fila[3], 'EDAD': fila[4], 'FOTO': fila[5]}
            personas.append(persona)

        if personas:
            return jsonify({'personas': personas, 'mensaje': "Personas listadas."})
        else:
            return jsonify({'mensaje': "No hay personas registradas"}, 404)  # Devuelve un código de estado 404 si no hay personas registradas

    except MySQLdb.Error as e:
        print("Error de MySQL:", str(e))
        return jsonify({'mensaje': f"Error de MySQL: {str(e)}"}, 500)  # Devuelve un código de estado 500 para errores internos de servidor
    except Exception as ex:
        print("Excepción general:", str(ex))
        return jsonify({'mensaje': f"Error: {str(ex)}"}, 500)  # También devolvemos un código de estado 500 para otras excepciones no manejadas

    finally:
        cursor.close()

@app.route('/persona/<DNI>', methods=['GET'])    
def leer_persona(DNI):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT * FROM persona WHERE DNI = %s"
        cursor.execute(sql, (DNI,))
        datos = cursor.fetchone()

        if datos:
            persona = {
                'id': datos[0],
                'DNI': datos[1],
                'NOMBRE': datos[2],
                'APELLIDO': datos[3],
                'EDAD': datos[4],
                'FOTO': datos[5]
            }
            return jsonify({'persona': persona, 'mensaje': "DNI ENCONTRADO."})
        else:
            return jsonify({'mensaje': "DNI NO ENCONTRADO"}, 404)  # Devuelve un código de estado 404 si no se encuentra el DNI

    except MySQLdb.Error as e:
        print("Error de MySQL:", str(e))
        return jsonify({'mensaje': f"Error de MySQL: {str(e)}"}, 500)  # Devuelve un código de estado 500 para errores internos de servidor
    except Exception as ex:
        print("Excepción general:", str(ex))
        return jsonify({'mensaje': f"Error: {str(ex)}"}, 500)  # También devolvemos un código de estado 500 para otras excepciones no manejadas

    finally:
        cursor.close()


    
from flask import abort

@app.route('/persona', methods=['POST'])
def registrar_persona():
    try:
        cursor = conexion.connection.cursor()
        # Verificar si ya existe un registro con el mismo DNI
        dni_existente = request.json['DNI']
        sql_verificar_dni = "SELECT id FROM persona WHERE DNI = %s"
        cursor.execute(sql_verificar_dni, (dni_existente,))
        resultado = cursor.fetchone()

        if resultado:
            # Ya existe un registro con el mismo DNI
            return jsonify({'error': "Ya existe un registro con este DNI.", 'codigo': 400}), 400  # Código 400 para indicar una solicitud incorrecta

        # Si no existe, proceder con la inserción
        sql_insertar = """INSERT INTO persona (DNI, NOMBRE, APELLIDO, EDAD, FOTO) 
                          VALUES (%s, %s, %s, %s, %s)"""
        valores = (
            request.json['DNI'],
            request.json['NOMBRE'],
            request.json['APELLIDO'],
            request.json['EDAD'],
            request.json['FOTO']
        )
        cursor.execute(sql_insertar, valores)
        conexion.connection.commit()  # confirma la acción de inserción
        return jsonify({'mensaje': "Persona registrada."})

    except KeyError as ke:
        # Manejar error si falta un campo obligatorio en el JSON de la solicitud
        return jsonify({'error': f"Falta el campo obligatorio: {str(ke)}", 'codigo': 400}), 400
    except Exception as ex:
        # Manejar otros errores generales
        print("Excepción general:", str(ex))
        return jsonify({'error': f"Error al registrar persona: {str(ex)}", 'codigo': 500}), 500  # Cambiado a código 500 para indicar un error interno del servidor
    finally:
        cursor.close()


@app.route('/persona/<DNI>', methods=['DELETE'])
def eliminar_persona(DNI):
    try:
        cursor = conexion.connection.cursor()

        # Verificar si el DNI existe antes de intentar eliminar
        sql_verificar_dni = "SELECT id FROM persona WHERE DNI = %s"
        cursor.execute(sql_verificar_dni, (DNI,))
        resultado = cursor.fetchone()

        if not resultado:
            # Si no hay resultados, el DNI no existe
            return jsonify({'error': f"No existe una persona con DNI {DNI}.", 'codigo': 404}), 404  # Cambiado a código 404 para indicar que no se encontraron datos

        # Si el DNI existe, proceder con la eliminación
        sql_eliminar = "DELETE FROM persona WHERE DNI = %s"
        cursor.execute(sql_eliminar, (DNI,))
        conexion.connection.commit()

        return jsonify({'mensaje': f"Persona con DNI {DNI} eliminada correctamente."})

    except MySQLdb.Error as e:
        print("Error de MySQL:", str(e))
        return jsonify({'error': f"Error de MySQL al eliminar persona: {str(e)}", 'codigo': 500}), 500  # Cambiado a código 500 para indicar un error interno del servidor
    except Exception as ex:
        print("Excepción general:", str(ex))
        return jsonify({'error': f"Error al eliminar persona: {str(ex)}", 'codigo': 500}), 500  # Cambiado a código 500 para indicar un error interno del servidor
    finally:
        cursor.close()


@app.route('/persona/<DNI>', methods=['PUT'])
def actualizar_persona(DNI):
    try:
        cursor = conexion.connection.cursor()

        # Verificar si la persona con el DNI existe
        sql_verificar_dni = "SELECT id FROM persona WHERE DNI = %s"
        cursor.execute(sql_verificar_dni, (DNI,))
        resultado = cursor.fetchone()

        if not resultado:
            # Si no hay resultados, el DNI no existe
            return jsonify({'error': f"No existe una persona con DNI {DNI}.", 'codigo': 404}), 404  # Cambiado a código 404 para indicar que no se encontraron datos

        # Si el DNI existe, proceder con la actualización
        sql_actualizar = "UPDATE persona SET DNI = %s, NOMBRE = %s, APELLIDO = %s, EDAD = %s, FOTO = %s WHERE DNI = %s"
        valores = (
            request.json.get('DNI', ''),
            request.json.get('NOMBRE', ''),
            request.json.get('APELLIDO', ''),
            request.json.get('EDAD', ''),
            request.json.get('FOTO', ''),
            DNI
        )
        cursor.execute(sql_actualizar, valores)
        conexion.connection.commit()

        return jsonify({'mensaje': f"Persona con DNI {DNI} actualizada correctamente."})

    except MySQLdb.Error as e:
        print("Error de MySQL:", str(e))
        return jsonify({'error': f"Error de MySQL al actualizar persona: {str(e)}", 'codigo': 500}), 500  # Cambiado a código 500 para indicar un error interno del servidor
    except Exception as ex:
        print("Excepción general:", str(ex))
        return jsonify({'error': f"Error al actualizar persona: {str(ex)}", 'codigo': 500}), 500  # Cambiado a código 500 para indicar un error interno del servidor
    finally:
        cursor.close()


@app.route('/direccion/<DNI>', methods=['GET'])
def obtener_direcciones_persona(DNI):
    try:
        cursor = conexion.connection.cursor()
        # Modifica la consulta para hacer un JOIN entre las tablas
        sql = """
            SELECT direccion.id, direccion.calle, direccion.num_calle, direccion.ciudad, direccion.DNI
            FROM direccion
            INNER JOIN persona ON direccion.DNI = persona.ID
            WHERE persona.DNI = %s
        """
        cursor.execute(sql, (DNI,))
        datos = cursor.fetchall()

        # Verifica si hay resultados antes de procesarlos
        if datos:
            direcciones = []
            for fila in datos:
                direccion = {'id': fila[0], 'calle': fila[1], 'num_calle': fila[2], 'ciudad': fila[3], 'DNI': fila[4]}
                direcciones.append(direccion)
            return jsonify({'direcciones': direcciones, 'mensaje': f"Direcciones de persona con DNI {DNI} listadas."})
        else:
            return jsonify({'mensaje': f"No hay direcciones registradas para la persona con DNI {DNI}."}), 404  # Cambiado a código 404 para indicar que no se encontraron datos

    except MySQLdb.Error as e:
        print("Error de MySQL:", str(e))
        return jsonify({'error': f"Error de MySQL al obtener direcciones: {str(e)}", 'codigo': 500}), 500  # Cambiado a código 500 para indicar un error interno del servidor
    except Exception as ex:
        print("Excepción general:", str(ex))
        return jsonify({'error': f"Error al obtener direcciones: {str(ex)}", 'codigo': 500}), 500  # Cambiado a código 500 para indicar un error interno del servidor
    finally:
        cursor.close()



@app.route('/direccion/<DNI>', methods=['POST'])
def agregar_direccion_persona(DNI):
    cursor_persona = None
    cursor_direccion = None

    try:
        # Verificar si la persona con el DNI existe antes de agregar la dirección
        cursor_persona = conexion.connection.cursor()
        sql_verificar_persona = "SELECT id FROM persona WHERE DNI = %s"
        cursor_persona.execute(sql_verificar_persona, (DNI,))
        resultado_persona = cursor_persona.fetchone()

        if not resultado_persona:
            # Si no hay resultados, la persona con el DNI no existe
            return jsonify({'error': f"No existe una persona con DNI {DNI}. No se puede agregar la dirección.", 'codigo': 404}), 404

        # Obtener los datos de la dirección desde el cuerpo de la solicitud
        nueva_direccion = {
            'calle': request.json.get('calle', ''),
            'num_calle': request.json.get('num_calle', ''),
            'ciudad': request.json.get('ciudad', ''),
            'id_persona': resultado_persona[0]  # Utilizamos el id de la persona
        }

        # Insertar la nueva dirección en la base de datos
        cursor_direccion = conexion.connection.cursor()
        sql_insertar_direccion = """
            INSERT INTO direccion (calle, num_calle, ciudad, DNI)
            VALUES (%s, %s, %s, %s)
        """
        valores_direccion = (
            nueva_direccion['calle'],
            nueva_direccion['num_calle'],
            nueva_direccion['ciudad'],
            nueva_direccion['id_persona']
        )
        cursor_direccion.execute(sql_insertar_direccion, valores_direccion)
        conexion.connection.commit()

        return jsonify({'mensaje': "Dirección agregada correctamente."})

    except MySQLdb.Error as e:
        print("Error de MySQL:", str(e))
        return jsonify({'error': f"Error de MySQL al agregar dirección: {str(e)}", 'codigo': 500}), 500
    except Exception as ex:
        print("Excepción general:", str(ex))
        return jsonify({'error': f"Error al agregar dirección: {str(ex)}", 'codigo': 500}), 500
    finally:
        if cursor_persona:
            cursor_persona.close()
        if cursor_direccion:
            cursor_direccion.close()


            

@app.route('/direccion/<DNI>/<int:id>', methods=['PUT'])
def editar_direccion_persona(DNI, id):
    cursor_persona = None
    cursor_direccion = None

    try:
        # Verificar si la persona con el DNI existe
        cursor_persona = conexion.connection.cursor()
        sql_verificar_persona = "SELECT id FROM persona WHERE DNI = %s"
        cursor_persona.execute(sql_verificar_persona, (DNI,))
        resultado_persona = cursor_persona.fetchone()

        if not resultado_persona:
            # Si no hay resultados, la persona con el DNI no existe
            return jsonify({'error': f"No existe una persona con DNI {DNI}. No se puede editar la dirección.", 'codigo': 404}), 404

        # Obtener los datos de la dirección desde el cuerpo de la solicitud
        direccion_editada = {
            'calle': request.json.get('calle', ''),
            'num_calle': request.json.get('num_calle', ''),
            'ciudad': request.json.get('ciudad', ''),
        }

        # Editar la dirección en la base de datos
        cursor_direccion = conexion.connection.cursor()
        sql_editar_direccion = """
            UPDATE direccion
            SET calle = %s, num_calle = %s, ciudad = %s
            WHERE id = %s AND DNI = (SELECT id FROM persona WHERE DNI = %s)
        """
        valores_direccion = (
            direccion_editada['calle'],
            direccion_editada['num_calle'],
            direccion_editada['ciudad'],
            id,
            DNI
        )
        cursor_direccion.execute(sql_editar_direccion, valores_direccion)
        conexion.connection.commit()

        if cursor_direccion.rowcount > 0:
            # Se ha editado al menos una fila, lo cual es un éxito
            return jsonify({'mensaje': f"Dirección con ID {id} para persona con DNI {DNI} editada correctamente."}), 200
        else:
            # No se ha editado ninguna fila, la dirección no existe o no ha cambiado
            return jsonify({'error': f"No existe una dirección con ID {id} para la persona con DNI {DNI} o no ha cambiado.", 'codigo': 404}), 404

    except MySQLdb.Error as e:
        print("Error de MySQL:", str(e))
        return jsonify({'error': f"Error de MySQL al editar dirección: {str(e)}", 'codigo': 500}), 500
    except Exception as ex:
        print("Excepción general:", str(ex))
        return jsonify({'error': f"Error al editar dirección: {str(ex)}", 'codigo': 500}), 500
    finally:
        if cursor_persona:
            cursor_persona.close()
        if cursor_direccion:
            cursor_direccion.close()





from flask import jsonify

@app.route('/direccion/<DNI>/<id>', methods=['DELETE'])
def borrar_direccion_persona(DNI, id):
    cursor = None

    try:
        # Verificar si la persona con el DNI existe
        cursor_persona = conexion.connection.cursor()
        sql_verificar_persona = "SELECT id FROM persona WHERE DNI = %s"
        cursor_persona.execute(sql_verificar_persona, (DNI,))
        resultado_persona = cursor_persona.fetchone()

        if not resultado_persona:
            # Si no hay resultados, la persona con el DNI no existe
            return jsonify({'error': f"La persona con DNI {DNI} no existe. No se puede borrar la dirección.", 'codigo': 404}), 404

        # Borrar la dirección en la base de datos
        cursor = conexion.connection.cursor()
        sql_borrar_direccion = """
            DELETE FROM direccion
            WHERE id = %s AND DNI = (SELECT id FROM persona WHERE DNI = %s)
        """
        valores_borrar_direccion = (id, DNI)
        cursor.execute(sql_borrar_direccion, valores_borrar_direccion)
        conexion.connection.commit()  # Confirma la transacción

        if cursor.rowcount > 0:
            # Se ha eliminado al menos una fila, lo cual es un éxito
            return jsonify({'mensaje': f"Dirección con ID {id} para persona con DNI {DNI} eliminada correctamente."}), 200
        else:
            # No se ha eliminado ninguna fila, la dirección no existe
            return jsonify({'error': f"No existe una dirección con ID {id} para la persona con DNI {DNI}.", 'codigo': 404}), 404

    except MySQLdb.Error as e:
        print("Error de MySQL:", str(e))
        return jsonify({'error': f"Error de MySQL al borrar dirección: {str(e)}", 'codigo': 500}), 500
    except Exception as ex:
        print("Excepción general:", str(ex))
        return jsonify({'error': f"Error al borrar dirección: {str(ex)}", 'codigo': 500}), 500
    finally:
        if cursor:
            cursor.close()
        if cursor_persona:
            cursor_persona.close()



def pagina_no_encontrada(error):
    return "<h1> La pag. que intenta ingresar no existe</h1>", 404

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(404,pagina_no_encontrada)
    app.run() 

