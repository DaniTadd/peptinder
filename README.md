# 🧬 TEAM PEPTINDER
**Plataforma Inteligente de Selección de Péptidos Fúngicos**

🏆 **[¡Prueba la aplicación en vivo aquí!](https://peptinder.streamlit.app/)**

Peptinder es una herramienta bioinformática y estratégica diseñada para acelerar el descubrimiento de péptidos antimicrobianos (AMPs) contra hongos fitopatógenos. Combina el análisis de propiedades fisicoquímicas con Inteligencia Artificial generativa para ayudar a investigadores a seleccionar los mejores candidatos a fungicidas.

### 💡 Funcionalidades Principales
* 🔍 **Búsqueda Dinámica:** Filtra la base de datos de péptidos especificando el patógeno objetivo.
* 📊 **Ranking Multicriterio (Scoring):** Evalúa a los candidatos mediante un "Score Total" normalizado basado en carga neta, hidrofobicidad, anfipatía y longitud.
* 🕸️ **Inspección de Candidatos:** Visualización interactiva (Radar Plot) del perfil biofísico exacto del péptido seleccionado.
* 🤖 **Dictamen Estratégico IA:** Integración con Google Gemini para generar un informe técnico instantáneo sobre el mecanismo de acción y la viabilidad del péptido seleccionado.

---

### 🏗️ Arquitectura y Procesamiento de Datos
Para garantizar una experiencia de usuario fluida y sin latencia durante la demostración, esta aplicación web (Frontend) se alimenta de una base de datos ya curada (`Peptides_Ranked_Final.csv`). 

**El pipeline de datos (Backend) que generó este archivo consistió en:**
1. Extracción y limpieza de secuencias de bases de datos públicas de AMPs.
2. Cálculo de propiedades fisicoquímicas utilizando librerías bioinformáticas especialics (`modlamp`, `biopython`).
3. Aplicación de un algoritmo de *Scoring* ponderado para penalizar secuencias tóxicas o inestables y premiar características fungicidas (alta carga catiónica, anfipatía óptima).

*(Nota: Los scripts de curación y generación de la base de datos se encuentran en este mismo repositorio para su auditoría técnica).*

---

### 💻 Ejecución Local (Para Desarrolladores)
Si deseas auditar el código y correr la app en tu entorno local:

1. Clona este repositorio.
2. Instala las dependencias: `pip install -r requirements.txt`
3. Crea un archivo `.env` en la raíz y añade tu API Key de Gemini: `GOOGLE_API_KEY="tu_clave_aqui"`
4. Ejecuta la app: `streamlit run app.py`
