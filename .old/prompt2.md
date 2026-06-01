# FitnessOS - Diseño Completo

## Visión

FitnessOS no es un contador de calorías ni una app tradicional de gimnasio.

Es un coach fitness digital con memoria persistente que:

- Entrevista al usuario.
- Construye un perfil inicial.
- Diseña un plan de acción.
- Registra entrenamientos.
- Registra alimentación.
- Registra estado de salud.
- Se adapta a cambios de contexto.
- Evalúa adherencia.
- Realiza análisis periódicos.
- Ajusta recomendaciones con el tiempo.

La prioridad no es el plan perfecto.

La prioridad es generar adherencia y mejorar decisiones a largo plazo.

---

## Flujo General

### Primer contacto

El usuario escribe por WhatsApp.

Si no existe perfil:

Ejecutar:

> **FitnessSurvey**

Luego

Todos los mensajes futuros pasan por:

> **FitnessFollowUp**

### Periódicamente

Se ejecuta:

> **FitnessAnalysis**

por cron o bajo demanda.

---

## FitnessSurvey

Genera el perfil inicial.

No debe durar demasiado.

Debe ser suficiente para arrancar.

La información faltante puede completarse más adelante.

### Estilo del coach

Primera pregunta.

Opciones:

- Directo
- Equilibrado
- Motivador

Esto modifica el tono futuro de las respuestas.

### Motivación

Pregunta obligatoria:

> ¿Por qué querés lograr este objetivo?

Ejemplos:

- Salud
- Estética
- Fuerza
- Rendimiento
- Confianza
- Competencia

La respuesta se utiliza posteriormente cuando baja la adherencia.

### Datos básicos

- Nombre
- Edad
- Sexo
- Altura
- Peso
- Estado físico

Actividad actual:

- Sedentario
- Poco activo
- Activo
- Muy activo

Composición corporal percibida:

- Delgado
- Promedio
- Sobrepeso
- Obesidad

### Objetivos

Objetivo principal:

- Bajar grasa
- Ganar músculo
- Ganar fuerza
- Mejorar salud
- Mejorar rendimiento deportivo

Objetivo secundario.

### Entrenamiento actual

Preguntar:

- ¿Entrenás actualmente?
- ¿Hace cuánto?
- ¿Con qué frecuencia?

### Conocimiento técnico

Nivel:

- Bajo
- Medio
- Alto

Si es bajo o medio:

- Priorizar aprendizaje técnico.
- Recomendar material educativo.
- Priorizar ejecución correcta antes que carga.

### Disponibilidad

- Días por semana.
- Tiempo disponible por sesión.

### Equipamiento

Opciones:

- Gimnasio completo
- Gimnasio básico
- Casa
- Plaza
- Bandas
- Peso corporal

### Preferencias de entrenamiento

Opciones:

- Heavy Duty
- Push Pull Legs
- Upper Lower
- Full Body
- Sin preferencia

La IA puede sugerir una alternativa mejor adaptada.

### Nutrición

Tipo de alimentación:

- Omnívoro
- Vegetariano
- Vegano

Restricciones:

- Celiaquía
- Lactosa
- Alergias
- Otras

Ayuno intermitente:

- No
- 12/12
- 14/10
- 16/8
- 20/4
- Personalizado

La IA puede sugerir alternativas y cuestionar decisiones poco realistas.

### Salud

Registrar:

- Lesiones
- Dolencias
- Hipertensión
- Diabetes
- Problemas articulares
- Restricciones médicas

### Suplementación

Registrar:

- Creatina
- Proteína
- Cafeína
- Otros

La creatina suele recomendarse.

El uso de pre-entrenos debe analizarse según contexto.

---

## Plan Inicial

Luego del Survey.

No busca maximizar rendimiento.

Busca generar adherencia.

Duración inicial sugerida: **4 semanas.**

---

## Checkpoints

No realizar en la primera semana.

No matar al usuario con pruebas tempranas.

### Cuándo realizarlos

Primer checkpoint: aproximadamente al mes.

Luego: cada 2 o 3 meses.

### Checkpoints adaptativos

Dependen del objetivo.

**Fuerza:**
- Banca
- Sentadilla
- Peso muerto
- Dominadas

**Pérdida de grasa:**
- Peso
- Cintura
- Fotos
- Cardio

**Salud:**
- Caminata
- Resistencia
- Flexiones

### Preparación

Antes del checkpoint:

- Dormir bien.
- Comer adecuadamente.
- Hidratarse.
- Evitar fatiga innecesaria.

---

## FitnessFollowUp

Skill principal de uso diario.

Debe aceptar lenguaje natural.

No formularios.

No JSON.

### Registro de entrenamiento

Ejemplos:

- `Press banca 100kg 3x10`
- `Dominadas 5x5`
- `Bici 20 minutos`
- `Caminata 40 minutos`

### Registro de alimentación

Ejemplos:

- `2 litros de agua`
- `Batido de proteína`
- `Pollo y arroz`
- `Huevos y fruta`
- `Pizza`

### Consultas nutricionales

Usuario: ¿Qué como?

La IA debe considerar:

- Hora actual.
- Objetivos.
- Restricciones.
- Ayuno.
- Preferencias.

Y ofrecer alternativas.

### Clasificación automática

Si el usuario escribe:

> Pollo y arroz

La IA deduce: desayuno / almuerzo / merienda / cena según horario y contexto.

### Cambios temporales

Ejemplos:

- Hoy entreno en hotel.
- Hoy entreno en plaza.
- Estoy de viaje.

### Cambios permanentes

Ejemplos:

- Ya no tengo gimnasio.
- Compré mancuernas.
- Ahora entreno en casa.

La skill actualiza el perfil.

### Estado de salud

Ejemplos:

- Estoy engripado.
- Me duele el hombro.
- Tengo fiebre.

La IA ajusta temporalmente las recomendaciones.

---

## Nutrición

### Filosofía principal

- **NO** contar calorías.
- **NO** perseguir macros.
- **NO** convertir la experiencia en una planilla.

### Objetivo

Detectar:

- hábitos
- adherencia
- calidad general
- patrones

### Registro simple

Ejemplos:

- Desayuné huevos.
- Almorcé pollo.
- Cené pizza.
- Tomé agua.

### Suplementación

Registrar uso.

Ejemplos:

- Tomé creatina.
- Tomé proteína.
- Tomé pre-entreno.

**Creatina:** generalmente recomendada.

**Cafeína:** analizar contexto. No fomentar dependencia innecesaria.

---

## Adherencia

Es la métrica más importante del sistema.

Más importante que calorías.

Más importante que el plan perfecto.

Medir:

- Entrenos realizados.
- Entrenos planificados.
- Peso registrado.
- Alimentación registrada.
- Agua registrada.

Ejemplo:

| Métrica | Valor |
|---|---|
| Planificados | 16 |
| Realizados | 11 |
| Adherencia | 68% |

---

## FitnessAnalysis

Puede ejecutarse:

- Manualmente.
- Semanalmente.
- Mediante cron.

Propuesta actual: **Domingos a las 12.**

### Objetivos

Analizar:

- Entrenamiento.
- Peso.
- Nutrición.
- Salud.
- Adherencia.

### Informes

Generar:

- Resúmenes semanales.
- Resúmenes mensuales.
- Alertas.

### Ejemplos

- Hace 12 días que no registrás entrenamientos.
- Hace 8 días que no registrás peso.
- Tu frecuencia cayó un 40%.
- Mejoraste tu banca un 12%.

---

## Base de Datos

Se concluyó que SQLite es mejor que Markdown como fuente de verdad.

**Archivo:** `fitness.db`

### Tablas sugeridas

- `users`
- `profile`
- `workouts`
- `nutrition_logs`
- `weight_logs`
- `health_events`
- `supplements`
- `checkpoints`
- `analysis_reports`

### Enums

Usar enums para ejercicios.

Ejemplos:

- `BENCH_PRESS`
- `INCLINE_BENCH`
- `SQUAT`
- `DEADLIFT`
- `PULLUP`
- `ROW`

Guardar además el texto original.

### Current State

Mantener una vista resumida del estado actual.

Puede ser una tabla o JSON.

Ejemplo:

| Campo | Descripción |
|---|---|
| `current_weight` | Peso actual |
| `current_phase` | Fase actual |
| `current_health` | Estado de salud |
| `current_equipment` | Equipamiento disponible |
| `adherence_last_30_days` | Adherencia últimos 30 días |
| `last_workout` | Último entrenamiento registrado |

---

## Filosofía General

FitnessOS no intenta ser:

- MyFitnessPal
- Un contador de calorías
- Un contador de macros

Busca ser:

> Un entrenador digital persistente que conoce la historia completa del usuario, adapta recomendaciones a su realidad actual y evalúa el progreso principalmente mediante adherencia, hábitos, rendimiento y consistencia a largo plazo.
