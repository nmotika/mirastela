# Cómo trabajamos

Mirastela es un servicio de astrología gestionado por Something Digital d.o.o., con sede en Zagreb (Croacia). Aquí explicamos de dónde salen los datos del sitio y cómo se escriben los textos.

## Cálculos

Las posiciones de los planetas, el ascendente y las casas se calculan con Swiss Ephemeris, la biblioteca astronómica que también usan los programas profesionales de astrología. Usamos el zodiaco tropical y las casas Placidus (más allá de los círculos polares, donde Placidus no funciona, el sistema de signos enteros). Para la carta natal usamos la fecha, la hora y el lugar de nacimiento con la zona horaria local.

## Cómo se escriben los textos

Los horóscopos, las descripciones de los signos, las previsiones anuales y los informes personales los escribe un modelo de lenguaje de IA (Claude, de Anthropic), solo a partir de datos que calculamos antes: qué planeta está en qué signo, cuándo cambia de signo y qué área de la vida (casa solar) toca para cada signo. El modelo no calcula nada por sí mismo, así que las fechas y posiciones de los textos coinciden con el cielo. El horóscopo diario se escribe cada mañana a partir del cielo de ese día.

## Qué es la astrología, y qué no es

La astrología es un lenguaje simbólico para reflexionar, no una ciencia ni una predicción de acontecimientos. Nuestros textos no son consejos sobre salud, dinero, derecho o relaciones. Para eso, consulta a un profesional.

## Contacto

Preguntas y correcciones: [hello@mirastela.com](mailto:hello@mirastela.com).
