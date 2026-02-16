import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Análisis Electoral Ecuador",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🗳️ Análisis Electoral - Ecuador")
st.markdown("### Sistema de Análisis por Parroquia - CNE")

# Función para crear datos de ejemplo
@st.cache_data
def crear_datos_ejemplo():
    """Genera datos de ejemplo con estructura del CNE"""
    import random
    
    provincias_data = {
        'Pichincha': ['Quito', 'Cayambe', 'Rumiñahui'],
        'Guayas': ['Guayaquil', 'Durán', 'Samborondón'],
        'Azuay': ['Cuenca', 'Gualaceo', 'Paute'],
        'Manabí': ['Portoviejo', 'Manta', 'Chone'],
        'El Oro': ['Machala', 'Pasaje', 'Santa Rosa']
    }
    
    parroquias_data = {
        'Quito': ['Centro Histórico', 'La Mariscal', 'Iñaquito', 'Kennedy'],
        'Guayaquil': ['Rocafuerte', 'Urdesa', 'Centro', 'Alborada'],
        'Cuenca': ['El Vecino', 'Centro', 'El Batán', 'Totoracocha'],
        'Cayambe': ['Cayambe Centro', 'Juan Montalvo', 'Ayora'],
        'Durán': ['Durán Centro', 'El Recreo', 'Eloy Alfaro']
    }
    
    candidatos = ['Candidato A', 'Candidato B', 'Candidato C', 'Candidato D', 'Candidato E']
    tipos_eleccion = ['Presidencial', 'Alcalde', 'Prefecto', 'Concejal']
    años = [2023, 2024, 2025]
    
    datos = []
    
    for provincia, cantones in provincias_data.items():
        for canton in cantones:
            parroquias = parroquias_data.get(canton, [f'{canton} Centro', f'{canton} Norte'])
            
            for parroquia in parroquias:
                for candidato in candidatos:
                    for año in años[:2]:  # Solo 2023 y 2024
                        votos = random.randint(500, 5000)
                        total_mesa = random.randint(3000, 8000)
                        porcentaje = round((votos / total_mesa) * 100, 2)
                        
                        datos.append({
                            'provincia': provincia,
                            'canton': canton,
                            'parroquia': parroquia,
                            'candidato': candidato,
                            'votos': votos,
                            'porcentaje': porcentaje,
                            'tipo_eleccion': random.choice(tipos_eleccion),
                            'año': año,
                            'circunscripcion': provincia if random.random() > 0.5 else 'Nacional'
                        })
    
    return pd.DataFrame(datos)

# Sidebar
st.sidebar.header("📊 Panel de Control")

# Opción de datos
st.sidebar.subheader("1️⃣ Fuente de Datos")
opcion_datos = st.sidebar.radio(
    "Selecciona:",
    ["📝 Datos de Ejemplo", "📤 Cargar Datos del CNE"],
    help="Usa datos de ejemplo o carga archivos CSV/Excel del CNE"
)

df = None

if opcion_datos == "📝 Datos de Ejemplo":
    with st.spinner('Cargando datos de ejemplo...'):
        df = crear_datos_ejemplo()
    st.sidebar.success(f"✅ {len(df)} registros cargados")
    
    st.info("""
    📝 **Usando datos de ejemplo**
    
    Para usar datos reales:
    1. Descarga datos desde: [CNE Ecuador](https://www.cne.gob.ec/estadisticas/bases-de-datos/)
    2. Selecciona "Cargar Datos del CNE" arriba
    3. Sube el archivo CSV o Excel
    """)

else:
    uploaded_file = st.sidebar.file_uploader(
        "Sube archivo CSV o Excel del CNE",
        type=['csv', 'xlsx', 'xls'],
        help="Formatos aceptados: .csv, .xlsx, .xls"
    )
    
    if uploaded_file:
        try:
            with st.spinner('Procesando archivo...'):
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
            
            st.sidebar.success(f"✅ Archivo cargado: {len(df)} registros")
        except Exception as e:
            st.sidebar.error(f"❌ Error: {str(e)}")
            st.error("No se pudo cargar el archivo. Verifica que sea un archivo válido del CNE.")

# Si hay datos, mostrar análisis
if df is not None and len(df) > 0:
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("2️⃣ Filtros")
    
    # Filtros
    col_filtro1, col_filtro2 = st.sidebar.columns(2)
    
    with col_filtro1:
        if 'provincia' in df.columns:
            provincia_sel = st.selectbox(
                "Provincia:",
                ['Todas'] + sorted(df['provincia'].unique().tolist())
            )
    
    with col_filtro2:
        if 'año' in df.columns:
            año_sel = st.selectbox(
                "Año:",
                ['Todos'] + sorted(df['año'].unique().tolist(), reverse=True)
            )
    
    if 'tipo_eleccion' in df.columns:
        tipo_sel = st.sidebar.selectbox(
            "Tipo de Elección:",
            ['Todos'] + sorted(df['tipo_eleccion'].unique().tolist())
        )
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if provincia_sel != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['provincia'] == provincia_sel]
    
    if año_sel != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['año'] == año_sel]
    
    if tipo_sel != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['tipo_eleccion'] == tipo_sel]
    
    # Filtro de cantón
    if provincia_sel != 'Todas' and 'canton' in df_filtrado.columns:
        canton_sel = st.sidebar.selectbox(
            "Cantón:",
            ['Todos'] + sorted(df_filtrado['canton'].unique().tolist())
        )
        if canton_sel != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['canton'] == canton_sel]
    
    # Métricas principales
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📍 Parroquias", df_filtrado['parroquia'].nunique() if 'parroquia' in df_filtrado.columns else 0)
    with col2:
        st.metric("🗳️ Total Votos", f"{df_filtrado['votos'].sum():,.0f}" if 'votos' in df_filtrado.columns else 0)
    with col3:
        st.metric("👥 Candidatos", df_filtrado['candidato'].nunique() if 'candidato' in df_filtrado.columns else 0)
    with col4:
        st.metric("📊 Registros", f"{len(df_filtrado):,}")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📍 Por Parroquia",
        "📊 Resultados Generales",
        "📈 Comparativas",
        "📋 Datos"
    ])
    
    with tab1:
        st.header("Análisis por Parroquia")
        
        if 'parroquia' in df_filtrado.columns and len(df_filtrado) > 0:
            parroquia_sel = st.selectbox(
                "Selecciona una parroquia:",
                sorted(df_filtrado['parroquia'].unique()),
                key='parroquia_selector'
            )
            
            df_parroquia = df_filtrado[df_filtrado['parroquia'] == parroquia_sel]
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader(f"📍 {parroquia_sel}")
                
                if 'provincia' in df_parroquia.columns:
                    st.write(f"**Provincia:** {df_parroquia['provincia'].iloc[0]}")
                if 'canton' in df_parroquia.columns:
                    st.write(f"**Cantón:** {df_parroquia['canton'].iloc[0]}")
                
                st.write(f"**Total Votos:** {df_parroquia['votos'].sum():,}")
                
                if 'candidato' in df_parroquia.columns and 'votos' in df_parroquia.columns:
                    st.write("**Resultados:**")
                    resultados = df_parroquia.groupby('candidato')['votos'].sum().sort_values(ascending=False)
                    for i, (cand, votos) in enumerate(resultados.items(), 1):
                        pct = (votos / resultados.sum()) * 100
                        st.write(f"{i}. {cand}: {votos:,} ({pct:.1f}%)")
            
            with col2:
                if 'candidato' in df_parroquia.columns and 'votos' in df_parroquia.columns:
                    votos_cand = df_parroquia.groupby('candidato')['votos'].sum()
                    fig = px.pie(
                        values=votos_cand.values,
                        names=votos_cand.index,
                        title=f'Votos en {parroquia_sel}'
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay datos de parroquias disponibles con los filtros seleccionados.")
    
    with tab2:
        st.header("Resultados Generales")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'candidato' in df_filtrado.columns and 'votos' in df_filtrado.columns:
                st.subheader("Votos por Candidato")
                votos_candidato = df_filtrado.groupby('candidato')['votos'].sum().sort_values(ascending=False)
                
                fig = px.bar(
                    x=votos_candidato.index,
                    y=votos_candidato.values,
                    labels={'x': 'Candidato', 'y': 'Votos'},
                    title='Total Votos por Candidato'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'provincia' in df_filtrado.columns and 'votos' in df_filtrado.columns:
                st.subheader("Distribución por Provincia")
                votos_prov = df_filtrado.groupby('provincia')['votos'].sum().sort_values(ascending=False)
                
                fig = px.pie(
                    values=votos_prov.values,
                    names=votos_prov.index,
                    title='Votos por Provincia'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        if 'parroquia' in df_filtrado.columns and 'votos' in df_filtrado.columns:
            st.subheader("🏆 Top 10 Parroquias")
            top10 = df_filtrado.groupby('parroquia')['votos'].sum().sort_values(ascending=False).head(10)
            
            fig = px.bar(
                x=top10.values,
                y=top10.index,
                orientation='h',
                labels={'x': 'Votos', 'y': 'Parroquia'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.header("Análisis Comparativo")
        
        if 'candidato' in df_filtrado.columns and 'provincia' in df_filtrado.columns:
            st.subheader("Candidatos por Provincia")
            
            pivot = df_filtrado.pivot_table(
                values='votos',
                index='provincia',
                columns='candidato',
                aggfunc='sum',
                fill_value=0
            )
            
            fig = px.bar(
                pivot,
                barmode='group',
                title='Comparación por Provincia'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.header("Datos Detallados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            buscar = st.text_input("🔍 Buscar en parroquia:", "")
        
        df_busqueda = df_filtrado.copy()
        if buscar:
            df_busqueda = df_busqueda[
                df_busqueda['parroquia'].str.contains(buscar, case=False, na=False)
            ]
        
        st.dataframe(df_busqueda, use_container_width=True, height=400)
        
        st.download_button(
            label="📥 Descargar CSV",
            data=df_busqueda.to_csv(index=False).encode('utf-8'),
            file_name=f'datos_electorales_{datetime.now().strftime("%Y%m%d")}.csv',
            mime='text/csv'
        )
        
        if 'votos' in df_busqueda.columns:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Media", f"{df_busqueda['votos'].mean():,.0f}")
            with col2:
                st.metric("Mediana", f"{df_busqueda['votos'].median():,.0f}")
            with col3:
                st.metric("Máximo", f"{df_busqueda['votos'].max():,.0f}")
            with col4:
                st.metric("Mínimo", f"{df_busqueda['votos'].min():,.0f}")

else:
    st.info("👈 Selecciona una fuente de datos en el panel lateral para comenzar el análisis.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Sistema de Análisis Electoral Ecuador | Datos: <a href='https://www.cne.gob.ec' target='_blank'>CNE</a></p>
</div>
""", unsafe_allow_html=True)
