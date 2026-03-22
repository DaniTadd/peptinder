import os
import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai
from dotenv import load_dotenv
import warnings

# ==============================================================================
# 0. 🔑 INICIALIZACIÓN Y CARGA INTELIGENTE DE API KEY ( Secrets > .env )
# ==============================================================================
# Primero intentamos cargar la API Key de la Bóveda de Secretos de Streamlit Cloud
try:
    # Si la app corre en Streamlit Cloud, st.secrets estará definido
    api_key = st.secrets["GOOGLE_API_KEY"]
except (FileNotFoundError, KeyError, NameError):
    # Si st.secrets no existe (estamos corriendo localmente), cargamos desde .env
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

# Inicialización del cliente de IA (si la llave se cargó)
if api_key and api_key.strip() != "":
    client = genai.Client(api_key=api_key)
else:
    client = None

# Manejo de Estado para persistencia de la IA
if 'ai_report' not in st.session_state:
    st.session_state.ai_report = None
# Persistencia del ID seleccionado para que no se borre la IA al cambiar selección
if 'selected_peptide_id' not in st.session_state:
    st.session_state.selected_peptide_id = None

# Higiene e ID de la app
warnings.filterwarnings("ignore", category=FutureWarning)
st.set_page_config(page_title="Antimicrobial Tinder", layout="wide", page_icon="🧪")

# ==============================================================================
# 🌟 1. BANNER SUPERIOR DE EQUIPO (Branding Incorporado y Centrado Vertical Solucionado)
# ==============================================================================
IMG_FONDO_PLANTACION = "https://images.unsplash.com/photo-1530836369250-ef71a3f5e48c?q=80&w=1600&auto=format&fit=crop"

# Variables de branding (Edita tus URLs de LinkedIn)
BRANDING_NAME = "TEAM PEPTINDER" # <--- ¡Cumplimos tu requisito de branding!
DESARROLLADO_POR_LABEL = "DESARROLLADO POR:"
MIEMBROS_EQUIPO = [
    {"nombre": "Daniel García Taddia", "url": "https://www.linkedin.com/in/danielgarciataddia/"},
    {"nombre": "Bruno Bassi", "url": "https://www.linkedin.com/in/bruno-bassi-65660823b/"},
]

# Construimos los botones en una sola línea continua (sin saltos de línea \n) para evitar fantasmas HTML
botones_links_html = "".join([f'<a href="{m["url"]}" target="_blank" class="linkedin-link">💼 {m["nombre"]}</a>' for m in MIEMBROS_EQUIPO])

# 1. 🎨 CSS EMERALD LIGHT TOTAL (ANTI-MODO OSCURO FORZADO)
# (Matamos los oscuros de la tabla y el gráfico aquí de forma definitiva)
st.markdown("""
<style>
    /* 1. Fondo General de la App y Cabecera (Verde Menta Suave, forzado) */
    /* Aseguramos que la app ignore el tema oscuro predeterminado */
    html, body, .stApp {
        background-color: #F0FDF4 !important; /* Fondo claro menta */
    }

    /* 2. Forzar color de TODA la fuente a Verde Bosque Muy Oscuro (Legibilidad Máxima) */
    html, body, [class*="st-"] {
        color: #052E16 !important;
        font-family: 'Inter', -apple-system, sans-serif;
    }

    /* 3. Títulos destacados en Esmeralda */
    h1, h2, h3 {
        color: #166534 !important;
        font-weight: 700 !important;
        letter-spacing: -1px;
    }

    /* 4. Labels de inputs (Selectbox, TextInput) */
    label p {
        color: #0F5132 !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }

    /* Estilo para los inputs limpios con borde */
    div[data-baseweb="select"] div[role="button"] {
        background-color: white !important;
        border-radius: 8px !important;
        border: 1px solid #A7F3D0 !important;
    }

    /* 5. Estilo de la Tabla (DataFrame) - (Mata el negro definitivamente) */
    div[data-testid="stDataFrame"] {
        background-color: white;
        border-radius: 12px;
        padding: 10px;
        border: 1px solid #A7F3D0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    /* 6. Botones (General y de la IA) */
    .stButton>button {
        background-color: #22C55E !important; /* Verde Esmeralda Brillante */
        color: white !important;
        border-radius: 8px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        border: none !important;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #16A34A !important;
        box-shadow: 0 10px 15px -3px rgba(34, 197, 94, 0.3);
    }

    /* 7. Caja de Informe de IA */
    .stInfo {
        background-color: #FFFFFF !important;
        color: #052E16 !important;
        border-left: 5px solid #22C55E !important;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    .stInfo p { color: #052E16 !important; }

    /* 8. Cajas de Código y Números Raw (Corregido image_3.png y Agrandado) */
    .stCodeBlock, [data-testid="stCodeBlock"] pre, [data-testid="stCodeBlock"] code {
        background-color: #D1FAE5 !important; /* Fondo verde esmeralda translúcido */
        color: #052E16 !important;
        border: 1px solid #A7F3D0 !important;
        border-radius: 8px;
    }

    /* Agrandamos la fuente de los valores raw a la derecha */
    p code {
        background-color: #D1FAE5 !important;
        color: #166534 !important;
        padding: 4px 12px !important;
        border-radius: 6px !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important; /* Letra bien grande y legible */
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# 2. 🧠 FUNCIONES CORE Y LÓGICA DE DATOS
# ==============================================================================
@st.cache_data
def load_data(file) -> pd.DataFrame:
    df = pd.read_csv(file)
    df['Sequence_Normalized'] = df['sequence'] if 'sequence' in df.columns else df.get('Sequence_Normalized', "")
    if 'length' not in df.columns:
        df['length'] = df['Sequence_Normalized'].str.len()
    
    cols_num = ['length', 'FunctionScore', 'SafetyScore', 'FinalScore', 'net_charge', 'hydrophobicity_eisenberg', 'hydrophobic_moment']
    for col in cols_num:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    if 'id' not in df.columns:
        df['id'] = [f"PEP-{i+1}" for i in range(len(df))]
    return df

def generar_briefing_peptido(pep_row, hongo_nombre, modelo_seleccionado):
    if not client: return "⚠️ Error: API Key no configurada."
    
    pep_id = pep_row['id']
    seq = pep_row['Sequence_Normalized']
    carga = pep_row['net_charge']
    hidro = pep_row['hydrophobicity_eisenberg']
    anfip = pep_row['hydrophobic_moment']
    
    prompt = f"""
    Como experto en fitopatología, analiza este candidato específico ({pep_id}) diseñado para combatir a: {hongo_nombre}.
    
    Datos exactos del {pep_id}:
    - Secuencia: {seq}
    - Carga Neta: {carga:.2f}
    - Hidrofobicidad: {hidro:.2f}
    - Anfipatía: {anfip:.2f}
    
    Genera un dictamen técnico breve indicando: 
    1. Mecanismo de acción probable para los valores exactos de este péptido. 
    2. Por qué es letal vs {hongo_nombre}. 
    3. Recomendación de uso.
    """
    
    try:
        response = client.models.generate_content(model=modelo_seleccionado, contents=prompt)
        return response.text
    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e): return "🚨 QUOTA_EXCEEDED"
        return f"Error en la consulta: {e}"


# ==============================================================================
# 3. 📂 CARGA DE DATOS Y FILTROS PRINCIPALES
# ==============================================================================
data_source = "Peptides_Ranked_Final.csv"
if os.path.exists(data_source):
    df = load_data(data_source)
else:
    st.error("Archivo 'Peptides_Ranked_Final.csv' no encontrado.")
    st.stop()

st.title("🔬 Bienvenido a Peptinder")
st.markdown("### Plataforma Inteligente de Selección de Péptidos Fúngicos")

if not api_key:
    st.error("⚠️ No se encontró la GOOGLE_API_KEY en el archivo .env.")

col_filt1, col_filt2 = st.columns([2, 1])
with col_filt1:
    pathogen = st.text_input("🎯 Patógeno Objetivo", placeholder="ej. Fusarium, Candida...")
with col_filt2:
    num_results = st.selectbox("📊 Cantidad a mostrar en tabla", options=[5, 10, 50, 100, "Todos"], index=1)

mask = df['id'].notnull()
if pathogen:
    search_term = pathogen.lower().strip()
    mask &= df.apply(lambda row: search_term in str(row.get('Target Species', '')).lower() or 
                                 search_term in str(row.get('Target_Organism', '')).lower(), axis=1)

filtered_df = df[mask].sort_values(by='FinalScore', ascending=False)
limit = len(filtered_df) if num_results == "Todos" else num_results


# ==============================================================================
# 4. 📊 TABLA DE RESULTADOS (Nombres Limpios y Barras Emerald Lab)
# ==============================================================================
st.subheader("📊 Ranking de Candidatos")
st.write(f"Se encontraron **{len(filtered_df)}** péptidos que cumplen los criterios.")

cols_cientificas = [
    'id', 'Sequence_Normalized', 'FinalScore', 
    'ChargeScore', 'net_charge', 
    'HydrophobicityScore', 'hydrophobicity_eisenberg',
    'AmphipathicityScore', 'hydrophobic_moment',
    'LengthScore', 'length', 'Category'
]

# Tabla Científica Interactiva (Clara, texto oscuro)
st.dataframe(
    filtered_df[cols_cientificas].head(limit),
    use_container_width=True,
    hide_index=True,
    column_config={
        "id": "ID",
        "Sequence_Normalized": "Secuencia",
        "net_charge": st.column_config.NumberColumn("Carga Neta Raw", format="%.2f"),
        "hydrophobicity_eisenberg": st.column_config.NumberColumn("Hidrofobicidad Raw", format="%.2f"),
        "hydrophobic_moment": st.column_config.NumberColumn("Anfipatía Raw (μH)", format="%.2f"),
        "length": "Longitud (aa)",
        "Category": "Categoría ✨",
        "FinalScore": st.column_config.ProgressColumn("Puntaje Total ✨🎯", min_value=0, max_value=100, format="%.1f"),
        "ChargeScore": st.column_config.ProgressColumn("Score Carga", min_value=0, max_value=100, format="%d"),
        "HydrophobicityScore": st.column_config.ProgressColumn("Score Hidrofobicidad", min_value=0, max_value=100, format="%d"),
        "AmphipathicityScore": st.column_config.ProgressColumn("Score Anfipatía", min_value=0, max_value=100, format="%d"),
        "LengthScore": st.column_config.NumberColumn("Score Largo", format="%d")
    }
)


# ==============================================================================
# 5. 🧬 DETALLE Y RADAR (Transparente y Homogéneo)
# ==============================================================================
if not filtered_df.empty:
    st.divider()
    st.subheader("🧬 Inspección Detallada del Candidato")
    
    col_sel, col_empty = st.columns([1, 2.5])
    with col_sel:
        peptide_list = filtered_df['id'].head(limit).tolist()
        if not st.session_state.selected_peptide_id or st.session_state.selected_peptide_id not in peptide_list:
            st.session_state.selected_peptide_id = peptide_list[0]
            
        st.session_state.selected_peptide_id = st.selectbox("Selecciona un ID de la tabla para detalle:", peptide_list)

    if st.session_state.selected_peptide_id:
        pep = filtered_df[filtered_df['id'] == st.session_state.selected_peptide_id].iloc[0]
        c_radar, c_raw = st.columns([1.5, 1])
        
        with c_radar:
            radar_df = pd.DataFrame(dict(
                r=[pep['ChargeScore'], pep['HydrophobicityScore'], pep['AmphipathicityScore'], pep['LengthScore'], pep['SafetyScore']],
                theta=['Score Carga', 'Score Hidro.', 'Score Anfipatía', 'Score Largo', 'Bioseguridad']
            ))
            fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True)
            # Trazado Emerald Lab
            fig.update_traces(fill='toself', line_color='#22C55E', fillcolor='rgba(34, 197, 94, 0.25)')
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', # Fondo 100% transparente para mezclarse con la app
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#052E16', size=14),
                polar=dict(
                    bgcolor='rgba(255,255,255,0.4)', # Fondo del radar blanco suave translúcido
                    radialaxis=dict(visible=True, range=[0, 100])
                ),
                margin=dict(l=30, r=30, t=30, b=30)
            )
            st.plotly_chart(fig, use_container_width=True)

        with c_raw:
            # Datos Raw Científicos (Letras grandes)
            st.markdown(f"**Categoría:** `{pep['Category']}` ✨")
            st.code(pep['Sequence_Normalized'], language="text")
            st.markdown(f"""
            - **Carga Neta Raw:** `{pep['net_charge']:.2f}`
            - **Hidrofobicidad (Eisenberg) Raw:** `{pep['hydrophobicity_eisenberg']:.2f}`
            - **Anfipatía Raw (μH):** `{pep['hydrophobic_moment']:.2f}`
            - **Longitud Raw:** `{pep['length']} aa`
            - **Puntaje Total ✨🎯 Raw:** `{pep['FinalScore']:.1f}`
            """)


# ==============================================================================
# 6. 🚀 BRIEFING ESTRATÉGICO DE LA IA (Centrado y Apilado)
# ==============================================================================
st.divider()

st.markdown("<h2 style='text-align: center; color: #166534;'>🛡️ Informe de Inteligencia Fúngica</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.15rem; margin-bottom: 5px;'>Selecciona el modelo y presiona el botón para comenzar el análisis del candidato seleccionado en el panel de inspección de arriba.</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1rem; color: #475569; margin-top: 0;'>Gemini analizará la vulnerabilidad del patógeno específico contra este péptido.</p>", unsafe_allow_html=True)
st.write("")

col_izq, col_centro, col_der = st.columns([1, 2, 1])
target_pathogen = pathogen if (pathogen and pathogen.strip() != "") else "Hongos Fitopatógenos"

with col_centro:
    # Selector de modelo de respaldo integrado aquí
    modelo_ai = st.selectbox("🤖 Selecciona el Motor de IA (Respaldo)", options=[
        "gemini-3.1-flash-lite-preview",
        "gemini-3-flash-preview",
        "gemini-2.5-flash-lite-preview-09-2025"
    ], help="Si un modelo falla por cuota o tokens, prueba con otro.")
    
    # Botón ocupando el ancho central
    if st.button("🔬 Generar Dictamen Estratégico", use_container_width=True):
        if st.session_state.selected_peptide_id:
            pep_seleccionado = filtered_df[filtered_df['id'] == st.session_state.selected_peptide_id].iloc[0]
            
            with st.spinner(f"Gemini analizando el perfil de {pep_seleccionado['id']} contra membrane de {target_pathogen}..."):
                resultado = generar_briefing_peptido(pep_seleccionado, target_pathogen, modelo_ai)
                
                if resultado == "🚨 QUOTA_EXCEEDED":
                    st.error("❌ Cuota agotada para este modelo.")
                    st.warning("⚠️ Selecciona otro 'Motor de IA' en la lista desplegable de arriba para continuar.")
                    st.session_state.ai_report = None 
                else:
                    # Título clarísimo en el reporte persistente
                    st.session_state.ai_report = f"### 🎯 Análisis Técnico para el candidato: {pep_seleccionado['id']}\n\n" + resultado
        else:
            st.warning("Primero debes seleccionar un ID de péptido válido en el panel de Inspección Detallada de arriba.")

# Muestra el reporte ocupando todo el ancho inferior, centrado visualmente
if st.session_state.ai_report:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info(st.session_state.ai_report)
