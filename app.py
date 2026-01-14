import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
from sqlalchemy import text

# === CONFIG & SETUP ===
st.set_page_config(
    page_title="PyFinance",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Connection
conn = st.connection("postgresql", type="sql")

# DB Initialization (Cached)
@st.cache_resource
def init_db():
    try:
        with conn.session as session:
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS transacciones (
                    id SERIAL PRIMARY KEY,
                    fecha DATE,
                    tipo VARCHAR(50),
                    categoria VARCHAR(50),
                    monto DECIMAL(10,2),
                    notas TEXT
                );
            """))
            session.commit()
    except Exception as e:
        st.error(f"Error crítico DB: {e}")

init_db()

# === CONSTANTS ===
CATEGORIAS_GASTO = [
    "Comida 🍔", "Transporte 🚌", "Casa 🏠", "Servicios 💡", 
    "Ocio 🍿", "Salud 💊", "Educación 📚", "Shopping 🛍️", "Suscripciones 📅", "Otros"
]
CATEGORIAS_INGRESO = [
    "Salario 💼", "Venta Ocasional 📦", "Regalo 🎁", "Inversión 📈", 
    "Reembolso ↩️", "Otro Ingreso"
]
CATEGORIAS_AHORRO = [
    "Fondo de Emergencia 🚨", "Vacaciones ✈️", "Meta Futura 🏡", "Inversión a Largo Plazo 🏦", "Alcancía 🐖"
]
CATEGORIAS_RETIRO = [
    "Uso de Emergencia 🚑", "Gasto Planificado 🏝️", "Inversión Ejecutada 📉", "Otro Retiro 💸"
]

# === LOGIC FUNCTIONS ===
def save_changes():
    """Callback for data_editor sync."""
    try:
        state = st.session_state["data_editor"]
        with conn.session as session:
            # 1. Edit
            for index, updates in state["edited_rows"].items():
                row_id = int(st.session_state['filtered_df'].iloc[int(index)]['id'])
                for col, value in updates.items():
                    query = text(f"UPDATE transacciones SET {col} = :val WHERE id = :id")
                    session.execute(query, {"val": value, "id": row_id})
            # 2. Delete
            for index in state["deleted_rows"]:
                row_id = int(st.session_state['filtered_df'].iloc[int(index)]['id'])
                session.execute(text("DELETE FROM transacciones WHERE id = :id"), {"id": row_id})
            session.commit()
        st.toast("Cambios guardados", icon="💾")
    except Exception as e:
        st.error(f"Error al guardar: {e}")

def get_smart_insights(df):
    """Generates rule-based insights from the dataframe."""
    insights = []
    
    if df.empty:
        return ["👋 ¡Bienvenido! Empieza registrando tu primera transacción."]

    # Spending Insight
    gastos = df[df['tipo'] == 'Gasto']
    if not gastos.empty:
        top_cat = gastos.groupby('categoria')['monto'].sum().idxmax()
        top_val = gastos.groupby('categoria')['monto'].sum().max()
        insights.append(f"🔥 Tu mayor gasto es en **{top_cat}** (${top_val:,.0f}).")
        
        avg_spend = gastos['monto'].mean()
        insights.append(f"📊 Gastas un promedio de **${avg_spend:,.0f}** por operación.")
    
    # Savings Insight
    total_ahorrado = df[df['tipo'] == 'Ahorro']['monto'].sum()
    total_retirado = df[df['tipo'] == 'RetiroAhorro']['monto'].sum()
    neto_ahorros = total_ahorrado - total_retirado
    
    if neto_ahorros <= 0 and total_ahorrado == 0:
        insights.append("💡 Consejo: ¡Intenta guardar un 5-10% de tus ingresos!")
    elif neto_ahorros > 0:
        insights.append(f"🐖 ¡Sigue así! Tienes **${neto_ahorros:,.0f}** seguros en tu alcancía.")
    
    if total_retirado > 0:
        insights.append(f"📉 Has retirado **${total_retirado:,.0f}** de tus ahorros historicos.")

    return insights

# === SIDEBAR ===
with st.sidebar:
    st.header("➕ Operación Rápida")
    
    # Selection
    tipo_op = st.radio("Tipo", ["Gasto 💸", "Ingreso 💰", "Ahorro 🐖", "Retirar Ahorro 📤"], horizontal=True)
    
    # Category Logic
    if "Gasto" in tipo_op:
        cats = CATEGORIAS_GASTO
        db_type = "Gasto"
    elif "Retirar" in tipo_op:
        cats = CATEGORIAS_RETIRO
        db_type = "RetiroAhorro"
    elif "Ingreso" in tipo_op:
        cats = CATEGORIAS_INGRESO
        db_type = "Ingreso"
    else:
        cats = CATEGORIAS_AHORRO
        db_type = "Ahorro"

    with st.form("main_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
             monto = st.number_input("Monto ($)", min_value=0.0, step=100.0)
        with col2:
             fecha = st.date_input("Fecha", value=date.today())
        
        cat = st.selectbox("Categoría", cats)
        nota = st.text_input("Nota", placeholder="Detalle opcional...")
        
        if st.form_submit_button("Guardar", type="primary"):
            if monto > 0:
                try:
                    with conn.session as session:
                        session.execute(
                            text("INSERT INTO transacciones (fecha, tipo, categoria, monto, notas) VALUES (:f, :t, :c, :m, :n)"),
                            {"f": fecha, "t": db_type, "c": cat, "m": monto, "n": nota}
                        )
                        session.commit()
                    
                    # Check visibility logic (Corrected)
                    visible = True
                    current_filter = st.session_state.get("time_filter", "Este Mes")
                    today = date.today()
                    
                    if current_filter == "Esta Semana":
                        start = today - timedelta(days=today.weekday())
                        end = start + timedelta(days=6)
                        if not (start <= fecha <= end): visible = False
                    elif current_filter == "Este Mes":
                        start = today.replace(day=1)
                        if not (start <= fecha): visible = False # Simple check for past
                    
                    if visible:
                        st.toast("¡Operación registrada con éxito!", icon="✅")
                    else:
                        st.toast(f"Guardado. (No visible en filtro '{current_filter}')", icon="⚠️")
                        
                    st.rerun()
                except Exception as e:
                    st.error(f"Error DB: {e}")
            else:
                st.warning("El monto debe ser > 0")

    
    # === FILTER & DANGER ZONE (Bottom of Sidebar) ===
    st.divider()
    filter_option = st.selectbox("📅 Filtro de Tiempo", ["Todo el Historial", "Este Mes", "Esta Semana"], index=0, key="time_filter")
    
    with st.expander("⚠️ Zona de Peligro"):
        if st.button("🗑️ Borrar TODA la Base de Datos", type="primary"):
            try:
                with conn.session as session:
                    session.execute(text("TRUNCATE TABLE transacciones RESTART IDENTITY CASCADE;"))
                    session.commit()
                st.toast("Base de datos reiniciada", icon="💥")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

# === DATA LOADING ===
try:
    raw_df = conn.query("SELECT * FROM transacciones ORDER BY fecha DESC", ttl=0)
except Exception as e:
    st.error(f"Error conexión: {e}")
    raw_df = pd.DataFrame()

if not raw_df.empty:
    raw_df['fecha'] = pd.to_datetime(raw_df['fecha']).dt.date
    raw_df['monto'] = pd.to_numeric(raw_df['monto'])
    
    # GLOBAL METRICS
    total_ing = raw_df[raw_df['tipo'] == 'Ingreso']['monto'].sum()
    total_gas = raw_df[raw_df['tipo'] == 'Gasto']['monto'].sum()
    total_aho = raw_df[raw_df['tipo'] == 'Ahorro']['monto'].sum()
    total_ret = raw_df[raw_df['tipo'] == 'RetiroAhorro']['monto'].sum()
    
    # Savings Logic: Net Savings = Deposits - Withdrawals
    alcancia_total = total_aho - total_ret
    
    # Cash Flow = Ingresos - Gastos - (Net Savings put into safe)
    # Alternatively: Cash = Ingresos - Gastos - Deposits + Withdrawals
    disponibilidad = total_ing - total_gas - total_aho + total_ret
else:
    disponibilidad, alcancia_total = 0.0, 0.0
    raw_df = pd.DataFrame(columns=["id", "fecha", "tipo", "categoria", "monto", "notas"])

# === APPLY FILTERS ===
today = date.today()
if filter_option == "Esta Semana":
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    mask = (raw_df['fecha'] >= start) & (raw_df['fecha'] <= end)
    filtered_df = raw_df[mask].reset_index(drop=True)
elif filter_option == "Este Mes":
    start = today.replace(day=1)
    next_m = today.replace(day=28) + timedelta(days=4)
    end = next_m - timedelta(days=next_m.day)
    mask = (raw_df['fecha'] >= start) & (raw_df['fecha'] <= end)
    filtered_df = raw_df[mask].reset_index(drop=True)
else:
    filtered_df = raw_df.reset_index(drop=True) # All History

st.session_state['filtered_df'] = filtered_df

# === DASHBOARD V5.2 ===
st.title("💸 PyFinance")

# 1. HERO CARDS
c_hero1, c_hero2, c_hero3 = st.columns(3)
with c_hero1:
    st.metric(label="💰 Disponibilidad (Cash)", value=f"${disponibilidad:,.0f}", help="Dinero líquido = Ingresos - Gastos - Ahorros + Retiros")
with c_hero2:
    st.metric(label="🐖 Mi Alcancía (Neta)", value=f"${alcancia_total:,.0f}", help="Ahorros depositados - Retiros")
with c_hero3:
    if not filtered_df.empty:
        # Visual balance of filter
        f_ing = filtered_df[filtered_df['tipo'] == 'Ingreso']['monto'].sum()
        f_gas = filtered_df[filtered_df['tipo'] == 'Gasto']['monto'].sum()
        f_bal = f_ing - f_gas
    else: f_bal = 0
    st.metric(label=f"Balance Simple ({filter_option})", value=f"${f_bal:,.0f}")

st.divider()

# 2. SMART INSIGHTS
st.subheader("🤖 Análisis Inteligente (AI)")
insights = get_smart_insights(filtered_df)
if insights:
    cols_ins = st.columns(len(insights))
    for i, msg in enumerate(insights):
        with cols_ins[i]:
            st.info(msg)

# 3. VISUALS
if not filtered_df.empty:
    st.markdown("### 📊 Tablero Visual")
    
    col_pie, col_bar = st.columns([1, 2])
    
    gasto_data = filtered_df[filtered_df['tipo'] == 'Gasto'].copy()
    
    with col_pie:
        st.caption("Distribución de Gastos")
        if not gasto_data.empty:
            cat_sum = gasto_data.groupby('categoria')['monto'].sum().reset_index()
            fig_pie = px.pie(
                cat_sum, values='monto', names='categoria', 
                hole=0.5,
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_pie.update_layout(margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Sin gastos registrados.")

    with col_bar:
        st.caption("Evolución en el Tiempo")
        if not gasto_data.empty:
            # Dynamic Aggregation
            if filter_option == "Todo el Historial":
                gasto_data['periodo'] = pd.to_datetime(gasto_data['fecha']).dt.strftime('%Y-%m')
                daily_sum = gasto_data.groupby('periodo')['monto'].sum().reset_index().sort_values('periodo')
                x_ax = 'periodo'
            else:
                daily_sum = gasto_data.groupby('fecha')['monto'].sum().reset_index().sort_values('fecha')
                x_ax = 'fecha'
                
            fig_bar = px.bar(
                daily_sum, x=x_ax, y='monto', 
                text_auto='.2s',
                title="",
                color_discrete_sequence=['#FF4B4B']
            )
            # Update layout to show all ticks if needed, but Plotly is usually smart.
            # We force string axis if needed to avoid skipping dates, but auto is safer for now.
            fig_bar.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Sin gastos registrados.")

# 4. EDITOR
st.markdown("### 📝 Movimientos")
if not filtered_df.empty:
    st.data_editor(
        filtered_df,
        key="data_editor",
        num_rows="dynamic",
        on_change=save_changes,
        column_config={
            "id": None,
            "fecha": st.column_config.DateColumn("Fecha"),
            "tipo": st.column_config.SelectboxColumn("Tipo", options=["Gasto", "Ingreso", "Ahorro", "RetiroAhorro"], required=True),
            "categoria": st.column_config.SelectboxColumn("Categoría", width="medium", options=
                CATEGORIAS_GASTO + CATEGORIAS_INGRESO + CATEGORIAS_AHORRO + CATEGORIAS_RETIRO
            ),
            "monto": st.column_config.NumberColumn("Monto", format="$%.2f"),
        },
        # Fixed deprecation warning
        # use_container_width=True -> replaced with default behavior or width='stretch' if exact match needed
        # Streamlit 1.52 shouldn't error on use_container_width. 
        # But per user error log:
        width='stretch' 
    )
    
    st.download_button("📥 Descargar Reporte Completo", filtered_df.to_csv(index=False).encode('utf-8'), "finanzas.csv")
else:
    st.info("No hay datos en este filtro de tiempo.")
