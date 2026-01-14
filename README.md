# 💸 PyFinance

> **Tu Gestor Financiero Personal Inteligente**

PyFinance es una aplicación web moderna y minimalista diseñada para ayudarte a tomar el control total de tu dinero. Construida con **Python** y **Streamlit**, ofrece una experiencia fluida tanto en escritorio como en móviles, conectada a una base de datos segura en la nube.

---

## ✨ Características Principales

### 🧠 Smart Insights (IA Local)
Olvídate de las hojas de cálculo aburridas. PyFinance analiza tus datos automáticamente y te ofrece:
- **🔥 Top Gastos:** Identifica dónde se va tu dinero.
- **📊 Promedios:** Calcula tu gasto diario habitual.
- **💡 Consejos:** Recomendaciones personalizadas basadas en tu flujo de caja.

### 🐖 Sistema de Ahorro & Alcancía
Gestiona tus objetivos financieros con herramientas dedicadas:
- **Registro de Ahorros:** Separa dinero de tu "Disponibilidad" con un clic.
- **Retiros Flexibles:** ¿Emergencia? Registra retiros de tu alcancía sin romper la contabilidad.
- **Visualización Neta:** Mira cuánto tienes realmente disponible para gastar vs. cuánto tienes ahorrado.

### 📊 Tableros Dinámicos
Visualizaciones que se adaptan a ti:
- **Vista Histórica:** Tendencias mensuales a largo plazo.
- **Vista Detallada:** Evolución diaria cuando filtras por "Este Mes".
- **Distribución:** Gráficos de dona para entender el peso de cada categoría.

### 🛠️ Herramientas de Gestión
- **Filtros Temporales:** Navega entre "Todo el Historial", "Este Mes" o "Esta Semana".
- **Edición en Vivo:** Corrige errores o borra transacciones directamente desde la tabla.
- **Zona de Peligro:** Funcionalidad para reiniciar tu base de datos desde cero si lo necesitas.

---

## � Tecnologías

Este proyecto está construido con un stack robusto y moderno:
- **Frontend/Backend:** [Streamlit](https://streamlit.io/) (Python).
- **Base de Datos:** [PostgreSQL](https://www.postgresql.org/) (recomendado: Neon Tech / Supabase).
- **Visualización:** [Plotly Express](https://plotly.com/python/).
- **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/).

---

## ⚙️ Instalación y Configuración

Sigue estos pasos para desplegar tu propia instancia de PyFinance:

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/PyFinance.git
cd PyFinance
```

### 2. Entorno Virtual (Opcional pero Recomendado)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos
Crea una carpeta llamada `.streamlit` en la raíz del proyecto y dentro un archivo `secrets.toml`:

```toml
# .streamlit/secrets.toml
[connections.postgresql]
dialect = "postgresql"
host = "tu-host-de-neon-o-supabase"
port = "5432"
database = "nombre-db"
username = "tu-usuario"
password = "tu-password"
```

### 5. Iniciar la App
```bash
streamlit run app.py
```

---

## 📱 Uso

1.  **Panel Lateral:** Usa la sección "Operación Rápida" para registrar Ingresos, Gastos o Ahorros.
2.  **Filtros:** Cambia el filtro de tiempo al final de la barra lateral para enfocar tu análisis.
3.  **Análisis:** Revisa las tarjetas superiores para ver tu "Disponibilidad Real" (Cash en mano) y tu "Alcancía".

---

<div align="center">
    <sub>Desarrollado con ❤️ para facilitar tus finanzas.</sub>
</div>