# Guion de la demo: Constructora Andina (docs/ejemplo-obras.json)

Cargar: **Fuentes → Importar JSON** → `ejemplo-obras.json` (trae `replace: true`: reemplaza todo).
34 nodos, 41 conexiones. Nodo central: **Constructora Andina S.A.** (tipo Empresa, archivo maestro), unido a las 4 obras.

| Obra | Estado | Plan de acción |
|---|---|---|
| Torre Alvear | En ejecución (35 %) | Estructura del piso 5 |
| Puente Río Suquía | En ejecución (10 %) | Excavación para pilotes |
| Ampliación Escuela N° 45 | En ejecución (70 %) | Instalación eléctrica y techos |
| Barrio Los Álamos | **Pausada** (permiso municipal) | Detenido |

## Errores escondidos (y cómo se ven en el grafo)

1. **Una máquina en dos obras a la vez**: el *Generador 60 kVA* (1 unidad) está asignado a Torre y a Escuela.
   Se ve como un nodo con dos líneas «asignada a» hacia obras distintas.
2. **Empleado en dos obras al 100 %**: *Diego Luna* (dedicación 100 %) asignado a Torre y a Escuela.
   Contraste: *Paula Vera* también está en dos obras, pero su nota dice 50 % y 50 % (correcto).
3. **Operador con la licencia vencida**: *Jorge Paz* opera la grúa torre; su licencia venció el 2026-09-15 (ver Detalles).
4. **Empleado de licencia asignado**: *Sergio Ríos* (licencia médica hasta 2026-11-20) figura en el Puente.
5. **Máquina en mantenimiento asignada**: la *Retroexcavadora JCB 3CX* está en mantenimiento hasta el 2026-11-10,
   pero es la que el Plan del Puente «requiere» para excavar.
6. **Lo que el plan necesita está en otra obra**: el Plan del Puente «requiere» la *Excavadora CAT 320*, que está
   asignada al Barrio pausado y sin uso (la línea cruza de un grupo a otro).
7. **Máquina alquilada sin obra**: la *Compactadora vibratoria* queda suelta, sin conexiones, y se paga igual.
8. **Material duplicado**: *Cemento Portland 50 kg* y *Cemento portland x50kg* son lo mismo, de dos proveedores
   y con precios distintos, los dos en la Escuela (se pidió dos veces).
9. **Falta material**: *Hormigón H-30* requiere 120 m³ y hay 80 en stock (Torre).
10. **Obra sin responsable de seguridad**: la Escuela no tiene a nadie de seguridad e higiene (Paula está en Torre y Puente).
11. **Material parado**: 8000 *ladrillos huecos* acopiados en el Barrio pausado.

## Reasignar en vivo (lo que el software facilita)

- **Mover la excavadora al Puente**: clic en *Excavadora CAT 320* → en la conexión «asignada a Barrio Los Álamos»,
  botón ⇄ (Reasignar) → elegir *Puente Río Suquía* → Guardar. Hacer lo mismo con su operador, *Ramiro Gómez*.
  Resuelve los errores 5 y 6 sin esperar a la retroexcavadora.
- **Sacar a Diego de una obra**: clic en *Diego Luna* → en «asignado a Ampliación Escuela N° 45», botón Quitar.
- **Poner a alguien de seguridad en la Escuela**: clic en *Paula Vera* → ⇄ en «asignado a Puente» → Escuela,
  o «Conectar con…» si se la quiere en las tres obras.
- **Llevar los ladrillos a la Escuela**: clic en *Ladrillo hueco 18 cm* → ⇄ → Ampliación Escuela N° 45.
- Cada cambio queda en la pestaña **Historial** del nodo (quién y cuándo).
