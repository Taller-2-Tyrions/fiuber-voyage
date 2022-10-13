[![codecov](https://codecov.io/gh/Taller-2-Tyrions/fiuber-voyage/branch/main/graph/badge.svg?token=98bKdacJw1)](https://codecov.io/gh/Taller-2-Tyrions/fiuber-voyage)


## Run Tests

```bash
python3 -m pytest tests/
```

# fiuber-voyage

Historias involucradas

# Búsqueda de destino por dirección (Front)

## Como pasajero quiero poder realizar búsquedas de destinos utilizando la dirección del mismo y así poder iniciar el proceso de viaje

==========================================================================================

# Cotización del viaje

## Como pasajero quiero poder saber previamente cual es el precio estimado del viaje a realizar, sabiendo el destino seleccionado y la modalidad de viaje.

==========================================================================================

# Confirmación de viaje

## Como pasajero quiero poder confirmar la realización del viaje

==========================================================================================

# Aceptar/rechazar un viaje

## Como chofer quiero poder aceptar o rechazar la realización de un viaje

==========================================================================================

# Guía de viaje (Front)

## Como pasajero/chofer quiero poder visualizar el recorrido a realizar y conocer la posición actual.

==========================================================================================

# Aviso de fin 

## Como chofer quiero poder indicar que el viaje ha finalizado

==========================================================================================

Microservicio de viajes

3 choferes activos en la aplicacion. 3 pasajeros activos

sit 1: entra un chofer a la aplicacion


chof -> serv: entro a la app con mi ubic actual.
serv -> chof: regresa lista de pasajeros que estan buscando viaje (con sus ids) en radio de ubicacion
chof -> serv: agarra alguno de los viajes.
serv-> cliente: notificion push (firebase) diciendo que un chofer lo agarro.  



sit 2: chofer entra a la app


chof -> serv: entro a la app con mi ubic actual. 
serv -> chof: pasajeros buscando viaje (con sus ids) en radio de ubicacion (quizas ninguno)

entra un cliente buscando viaje.

serv -> chofer: notificacion push con nuevo cliente buscando viaje. 
chof -> serv: agarra alguno de los pasajes. 
serv-> cliente: notificion push (firebase) diciendo que un chofer lo agarro.

==================

POST /voyage/price/{idUser}
{
    "src": point,
    "dest": point,
    "is_vip": bool,
}

Chofer -- Tramo 1 --> Cliente -- Tramo 2 --> Destino (FIN)

Viaje:
	Chofer
		Modalidad
	Cliente 
		Modalidad
	Origen
	Destino
	


 - Chequear Gateway

 - Calificacion
 - Denuncia



