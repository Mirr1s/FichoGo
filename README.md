# FichoGo
Aplicación móvil para mejorar el acceso a comedores universitarios mediante un ficho digital integrado con el carnet estudiantil. Reduce filas, optimiza la gestión del servicio y garantiza un control eficiente, mejorando la experiencia de los estudiantes.


# 📊 Diagramas UML del Proyecto *Lechuga*

A continuación se presentan los diagramas UML desarrollados para comprender y modelar la lógica del sistema **Lechuga**, una aplicación que permite a los estudiantes solicitar fichos digitales para acceder al comedor universitario. Estos diagramas ayudan a representar de forma clara y estructurada cómo interactúan los actores, cuáles son las clases principales del sistema, los flujos de acciones, y la lógica detrás de los procesos.

---

## 1. 🧑‍💼 Diagrama de Casos de Uso

Este diagrama muestra los **actores** que interactúan con el sistema y los **casos de uso** principales que pueden realizar.

**Actores principales:**
- **Estudiante**: Solicita el ficho digital, consulta cupos, recibe confirmación.
- **Personal del Comedor**: Escanea el código QR/NFC y decide si permitir o denegar el acceso.
- **Administrador**: Configura los parámetros del comedor como la capacidad y los horarios.

**Propósito:** Identificar y organizar las funcionalidades del sistema desde el punto de vista del usuario final.

![Diagrama de Casos de Uso](ruta_a_imagen_casos_de_uso)

---

## 2. 🔄 Diagrama de Actividad – Flujo de solicitud del ficho

Este diagrama muestra paso a paso cómo un estudiante solicita un ficho desde que abre la aplicación hasta que recibe la confirmación, o se le informa que no hay cupos disponibles.

**Puntos clave del flujo:**
- Verificación de credenciales.
- Consulta de disponibilidad de cupos.
- Generación del código QR/NFC si hay disponibilidad.
- Notificación final al estudiante.

**Propósito:** Representar gráficamente el flujo de trabajo lógico de la funcionalidad más importante de la app.

![Diagrama de Actividad](ruta_a_imagen_actividad)

---

## 3. 🧱 Diagrama de Clases

El diagrama de clases presenta las **entidades principales** del sistema, sus atributos, métodos y las relaciones entre ellas.

**Clases importantes:**
- `Usuario`: clase base para estudiantes, personal y administradores.
- `FichoDigital`: contiene la lógica de generación y validación del ficho QR/NFC.
- `Comedor`: administra capacidad y horarios.
- `RegistroAcceso`: almacena los accesos aprobados o denegados.

**Propósito:** Modelar la estructura estática del sistema en términos de objetos y relaciones.

![Diagrama de Clases](ruta_a_imagen_clases)

---

## 4. ⏱️ Diagrama de Secuencia – Solicitud de ficho

Este diagrama representa cómo fluye la información entre los diferentes componentes cuando un estudiante solicita un ficho.

**Pasos clave:**
1. El estudiante se autentica.
2. Se verifica la disponibilidad de cupos.
3. Si hay cupos, se genera un ficho y se le entrega un código QR/NFC.
4. En caso contrario, se le notifica que no hay cupos disponibles.

**Propósito:** Entender la **interacción temporal** entre los actores y el sistema, paso a paso.

![Diagrama de Secuencia](ruta_a_imagen_secuencia)
