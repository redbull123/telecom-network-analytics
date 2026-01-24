# 📡 Telecom Network Analytics Pipeline

> Pipeline de análisis end-to-end para eventos de señalización en redes móviles (SGSN-MME)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: In Development](https://img.shields.io/badge/status-in%20development-orange.svg)]()

## 📋 Descripción

Este proyecto implementa un pipeline completo de ingeniería de datos para analizar eventos de señalización en redes de telecomunicaciones móviles. Procesa y analiza eventos como attach, handover, paging y otros procedimientos de señalización SGSN-MME.

**Caso de uso:** Monitoreo y análisis de rendimiento de red móvil en tiempo casi-real, permitiendo detectar anomalías, calcular KPIs de red y optimizar la experiencia del usuario.

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────┐
│  Data Generator     │  Simulador de eventos de señalización
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   ETL Pipeline      │  Extracción, transformación y carga
│   (Apache Airflow)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   PostgreSQL DB     │  Almacenamiento persistente
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Analytics/Viz      │  Power BI / Streamlit
└─────────────────────┘
```

## 🛠️ Stack Tecnológico

- **Lenguaje:** Python 3.10+
- **Orchestration:** Apache Airflow 2.7+ *(próximamente)*
- **Base de Datos:** PostgreSQL 14+
- **Visualización:** Power BI / Streamlit
- **Containerización:** Docker & Docker Compose *(próximamente)*
- **Cloud:** AWS (RDS, ECS, S3) *(próximamente)*

## 📊 Métricas y KPIs Analizados

### KPIs Principales
- **Attach Success Rate (ASR):** % de attach procedures exitosos
- **Handover Success Rate (HOSR):** % de handovers sin fallo
- **Paging Success Rate:** Tiempo de respuesta promedio de paging
- **Service Request Success Rate:** % de service requests exitosos
- **Detach Success Rate:** % de detach procedures correctos

### Análisis Dimensionales
- Distribución temporal (horaria, diaria, semanal)
- Performance por celda/eNodeB
- Análisis de causas de fallo
- Detección de anomalías
- Comparativa horas pico vs normales

## 🚀 Quick Start

### Prerequisitos

```bash
Python 3.10 o superior
PostgreSQL 14+ (opcional para desarrollo inicial)
Git
```

### Instalación

1. **Clonar el repositorio:**
```bash
git clone https://github.com/TU_USUARIO/telecom-network-analytics.git
cd telecom-network-analytics
```

2. **Crear entorno virtual:**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Crear estructura de directorios:**
```bash
mkdir -p data/raw data/processed data/staging
```

### Uso del Generador de Datos

#### Generar dataset una sola vez

```bash
# Generar 10,000 eventos en JSON
python data_generator/generator.py --mode once --events 10000 --format json

# Generar 50,000 eventos en CSV
python data_generator/generator.py --mode once --events 50000 --format csv
```

#### Ejecutar en modo continuo (stream simulation)

```bash
# Generar 1,000 eventos cada 60 segundos
python data_generator/generator.py --mode continuous --batch-size 1000 --interval 60

# Detener con Ctrl+C
```

#### Opciones adicionales

```bash
# Con seed para reproducibilidad
python data_generator/generator.py --mode once --events 10000 --seed 42

# Especificar directorio de salida
python data_generator/generator.py --mode once --events 10000 --output-dir data/custom_output
```

### Ejemplos de Uso

```python
# Usar el generador en código Python
from data_generator.generator import TelecomEventGenerator

# Crear generador
generator = TelecomEventGenerator(seed=42)

# Generar eventos
events = generator.generate_batch(num_events=1000)

# Guardar a archivo
from pathlib import Path
generator.save_to_json(events, Path("data/raw/my_events.json"))
```

## 📂 Estructura del Proyecto

```
telecom-network-analytics/
├── .gitignore                  # Archivos ignorados por Git
├── README.md                   # Este archivo
├── requirements.txt            # Dependencias de Python
├── config/                     # Configuraciones
│   └── config.yaml            # (próximamente)
├── data/                       # Datos (gitignored)
│   ├── raw/                   # Datos crudos generados
│   ├── processed/             # Datos procesados
│   └── staging/               # Datos intermedios
├── data_generator/            # Generador de datos sintéticos
│   ├── __init__.py
│   └── generator.py           # Script principal del generador
├── sql/                       # Scripts SQL
│   └── schema.sql             # (próximamente)
├── etl/                       # Scripts ETL
│   └── (próximamente)
├── airflow/                   # DAGs de Airflow
│   └── dags/
│       └── (próximamente)
├── dashboards/                # Visualizaciones
│   ├── powerbi/               # Archivos Power BI
│   └── streamlit/             # App Streamlit (próximamente)
├── tests/                     # Tests unitarios
│   └── (próximamente)
└── docs/                      # Documentación adicional
    └── architecture.md        # (próximamente)
```

## 🔧 Configuración

### Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=telecom_analytics
DB_USER=your_user
DB_PASSWORD=your_password

# Airflow (próximamente)
AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/airflow
```

## 📈 Roadmap

### ✅ Sprint 0 - Setup Inicial (Completado)
- [x] Configuración de GitHub
- [x] Generador de datos sintéticos
- [x] Estructura del proyecto
- [x] Documentación inicial

### 🔄 Sprint 1 - ETL & Airflow (En Progreso)
- [ ] Integración con Apache Airflow
- [ ] DAG de ETL completo
- [ ] Conexión a PostgreSQL
- [ ] Data quality checks
- [ ] KPI calculations

### ⏳ Sprint 2 - Containerización (Próximamente)
- [ ] Dockerfiles para cada componente
- [ ] docker-compose.yml
- [ ] CI/CD básico

### ⏳ Sprint 3 - Cloud Deployment (Próximamente)
- [ ] Deploy en AWS
- [ ] Dashboard público
- [ ] Monitoring y alertas

## 🧪 Testing

```bash
# Ejecutar tests (próximamente)
pytest tests/

# Con coverage
pytest --cov=data_generator tests/
```

## 📝 Datos Sintéticos

Los eventos generados incluyen los siguientes campos:

```json
{
  "event_id": "20250119143045_00000001",
  "timestamp": "2025-01-19T14:30:45.123456",
  "event_type": "attach",
  "result": "success",
  "failure_cause": null,
  "imsi_hash": "IMSI_123456789",
  "imei_hash": "IMEI_987654321",
  "cell_id": "CELL_042",
  "enodeb_id": "ENB_005",
  "mme_id": "MME_01",
  "tracking_area": "TA_3",
  "duration_ms": 245,
  "rat_type": "LTE",
  "frequency_band": "B7"
}
```

### Tipos de Eventos Soportados

- **attach** (35%): Initial attach, handover attach, periodic TAU
- **handover** (25%): X2 handover, S1 handover
- **paging** (20%): MT call, MT SMS
- **service_request** (15%): Data, voice, SMS
- **detach** (5%): UE initiated, network initiated

## 🤝 Contribuciones

Este es un proyecto de portafolio personal. Si tienes sugerencias o encuentras bugs, feel free to:

1. Fork el proyecto
2. Crear una rama con tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 👤 Autor

**Raul Santana**
- Packet Core Specialist | Aspiring Data Engineer
- LinkedIn: [ingraulsantana](https://linkedin.com/in/ingraulsantana)
- GitHub: [@redbull123](https://github.com/redbull123)
- Email: rjsantana95@gmail.com

## 🙏 Agradecimientos

- Dataset sintético inspirado en 3GPP TS 23.401 (GPRS enhancements for E-UTRAN access)
- Arquitectura basada en mejores prácticas de Data Engineering

---

⚠️ **Nota:** Este proyecto utiliza datos sintéticos simulados. No contiene información real o confidencial de ninguna red de telecomunicaciones.

**Status:** 🚧 Proyecto en desarrollo activo - Sprint 0 completado, Sprint 1 en progreso