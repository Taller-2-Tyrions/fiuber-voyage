[![codecov](https://codecov.io/gh/Taller-2-Tyrions/fiuber-voyage/branch/main/graph/badge.svg?token=98bKdacJw1)](https://codecov.io/gh/Taller-2-Tyrions/fiuber-voyage)

# Fiuber-Voyage
Microservicio para el manejo de los distintos viajes que se llevan a cabo dentro de la plataforma.

# Documentación
Documentación técnica: https://taller-2-tyrions.github.io/fiuber-documentation-tecnica/

## Run Tests

```bash
python3 -m pytest tests/
```

## Historias involucradas

#### Búsqueda de destino por dirección (Front)

Como pasajero quiero poder realizar búsquedas de destinos utilizando la dirección del mismo y así poder iniciar el proceso de viaje

#### Cotización del viaje

Como pasajero quiero poder saber previamente cual es el precio estimado del viaje a realizar, sabiendo el destino seleccionado y la modalidad de viaje.

#### Confirmación de viaje

Como pasajero quiero poder confirmar la realización del viaje

#### Aceptar/rechazar un viaje

Como chofer quiero poder aceptar o rechazar la realización de un viaje

#### Guía de viaje (Front)

Como pasajero/chofer quiero poder visualizar el recorrido a realizar y conocer la posición actual.

#### Aviso de fin 

Como chofer quiero poder indicar que el viaje ha finalizado

# Microservicio de viajes

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


## Logica De Pagos


price_voyage = PRICE_PER_METER * distancia + PRICE_PER_MINUTE * duracion
  seniority del driver indica antiguedad. Al tener mas antiguedad el Driver
       tendria mas beneficio en el precio de su viaje
  misma idea con viajes por dia/mes
price_driver = seniority * DISCOUNT_SENIORITY_DRIVER +  voyage_in_date *
      DISCOUNT_DAILY_DRIVER + voyage_in_mounth * DISCOUNT_MONTHLY_DRIVER
  seniority del client simil al Driver
  misma idea con viajes por dia/mes
price_client = seniority * DISCOUNT_SENIORITY_CLIENT + voyage_in_date *
      DISCOUNT_DAILY_CLIENT + voyage_in_mounth * DISCOUNT_MONTHLY_DRIVER
price_time_await = time_confirmacion * PRICE_WAIT_CONF +
  time_driver_to_origin * PRICE_ARRIVAL

total_price = (price_voyage + price_driver + price_client + price_time_await)
      * PRICE_PER_VIP * NIGHT_PLUS

Características del conductor (viajes en el día, viajes en el mes,
      antigüedad) -> AVERAGE_DRIVER_PRICE
Características del pasajero (viajes en el día, viajes en el mes, antigüedad
      , saldo)
Método de pago

Características del viaje
(duración --> Google Maps, distancia, posición geográfica, fecha y hora)
Cantidad de viajes que se realizaron en la última ventana temporal
(Hora, 30 mins, 10 mins) -> Nosotros
Día y horario de la realización del viaje
Tiempo de espera del pasajero para:
Tiempo hasta que un conductor le confirme
el viaje --> Variable Actualizable
Tiempo hasta que el conductor llegue a buscarlo --> Google Maps
