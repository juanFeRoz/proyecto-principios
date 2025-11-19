# Proyecto Final: Análisis del Comportamiento de Aplicaciones en Kubernetes

Este proyecto tuvo como objetivo principal analizar y cuantificar el impacto del entorno de despliegue y la escalabilidad de la infraestructura en el rendimiento de una aplicación web (API REST con PostgreSQL).

Se compararon tres escenarios principales: **Docker Compose** (línea base), **Kubernetes en un Solo Nodo** (simulación de recursos limitados), y **Kubernetes Multi-Nodo** (escalado horizontal de infraestructura).

### Conclusión Principal

Se demostró que la **escalabilidad horizontal de la infraestructura** (número de nodos de Kubernetes) fue el factor determinante para el rendimiento y la reducción de la latencia, superando las limitaciones impuestas por el escalado de réplicas en un entorno de nodo único. El punto de rendimiento óptimo se alcanzó con **2 réplicas** distribuidas en el clúster Multi-Nodo.

## 2. Metodología de Despliegue y Pruebas

El clúster se configuró utilizando **MicroK8s** en tres Máquinas Virtuales (VMs): `gp21` (Líder), `gp22` y `gp4`. Para generar la carga, se utilizó **Locust** (simulando JMeter) con una configuración consistente de **50 usuarios** durante 60 segundos en cada prueba.
Este resumen describe la metodología rigurosa utilizada para generar la carga de trabajo, la cual es fundamental para asegurar la validez y comparabilidad de las métricas recolectadas.

---

### Descripción de la Metodología para Generar Carga con Locust

Aunque el proyecto sugería el uso de JMeter, se utilizó la herramienta de prueba de carga **Locust** para generar las peticiones HTTP concurrentes. Locust permitió simular el tráfico de múltiples usuarios de manera escalable, recolectando las métricas de rendimiento necesarias para el análisis.

#### A. Objetivo de la Prueba

El objetivo de la metodología fue saturar la aplicación en cada escenario de despliegue para observar y cuantificar dos métricas clave:

1.  **Tiempo Medio de Respuesta (Latencia):** El tiempo promedio que tarda la aplicación en responder a la petición, medido en milisegundos (ms).
2.  **Throughput (Tasa de Peticiones):** El número de peticiones procesadas exitosamente por la aplicación por segundo (`Requests/s`).

#### B. Configuración de Carga (Parámetros Fijos)

Para garantizar que los resultados entre Docker Compose, K8s 1 Nodo y K8s Multi-Nodo fueran directamente comparables, se utilizaron parámetros de carga idénticos en cada ronda de prueba:

| Parámetro | Valor | Descripción |
| :--- | :--- | :--- |
| **Usuarios Concurrentes** | 50 | Número total de usuarios simulados. |
| **Tasa de Generación (*Spawn Rate*)** | 5/segundo | Tasa a la que los usuarios virtuales se añadieron a la prueba. |
| **Duración de la Prueba** | 60 segundos | Tiempo total de ejecución de la prueba para cada escenario. |
| **Endpoint Principal** | `GET /Listar Productos` | Operación crítica de lectura que interactúa con la base de datos poblada. |
| **IP de Destino** | IP Pública de la VM Líder | El *host* de Locust se configuró con `http://100.115.74.53:30001` (el NodePort de Kubernetes). |

#### C. Procedimiento de Recolección de Datos

El proceso de recolección se repitió para las siete configuraciones de despliegue (Fase 1 + 6 variaciones de K8s):

1.  **Inicialización de la DB:** Antes de cada fase, se verificó la persistencia y la cantidad significativa de datos. Si la DB se había reseteado, se ejecutó la operación de *seed* (`/seed/5000`).
2.  **Ejecución de Locust:** Se inició Locust contra el NodePort expuesto (30001) para generar la carga.
3.  **Recolección del Reporte:** Al finalizar cada prueba, se descargó el reporte CSV generado por Locust (nombrados como `reporteX-Y.csv`).
4.  **Extracción de Métricas:** Para el análisis en el Jupyter Notebook, se extrajeron las métricas de la fila **`Aggregated`** del CSV, la cual resume el rendimiento total de la prueba, asegurando que los datos fueran consistentes.

Esta metodología garantizó una base de datos de rendimiento empírica y rigurosa para extraer conclusiones sobre la escalabilidad.

### Fases de Despliegue (Paso a Paso)

| Fase | Entorno | Configuración | Comandos Clave |
| :--- | :--- | :--- | :--- |
| **Fase 1** | Docker Compose | Línea base: App + DB en 1 VM. | `docker compose up -d` |
| **Fase 2** | K8s 1 Nodo | Simulación: **`gp21`** activo. Nodos `gp22`/`gp4` bloqueados. | `microk8s kubectl cordon gp22 gp4` |
| **Fase 3** | K8s Multi-Nodo | Despliegue completo: 3 Nodos Activos (`gp21`, `gp22`, `gp4`). | `microk8s kubectl uncordon gp22 gp4` |

---

### Comandos Comunes en Kubernetes (Fase 2 y 3)

| Tarea | Comando de Ejemplo |
| :--- | :--- |
| **Despliegue** | `microk8s kubectl apply -f postgres.yaml -f app.yaml` |
| **Poblamiento DB** | `curl -X POST http://100.115.74.53:30001/seed/5000` |
| **Escalado de Réplicas** | `microk8s kubectl scale deployment tienda-app --replicas=3` |
| **Verificación** | `microk8s kubectl get pods -o wide` |

---

## 3. Resultados Cuantitativos

Los datos recolectados (Archivos CSV: `reporte1.csv` a `reporte3-3replicas.csv`) fueron procesados en un Jupyter Notebook para obtener las métricas finales.

### DataFrame de Métricas Finales

| Escenario | Tipo Despliegue | Réplicas | Throughput (RPS) | Latencia (ms) |
| :--- | :--- | :---: | :---: | :---: |
| **Fase 1: Docker Compose** | Docker | 1 | 23.65 | 74.26 |
| Fase 2: K8s 1 Nodo, 1 Réplica | K8s 1 Nodo | 1 | 18.92 | 527.23 |
| Fase 2: K8s 1 Nodo, 2 Réplicas | K8s 1 Nodo | 2 | 20.24 | 297.87 |
| Fase 2: K8s 1 Nodo, 3 Réplicas | K8s 1 Nodo | 3 | 21.10 | 210.75 |
| Fase 3: K8s Multi-Nodo, 1 Réplica | K8s Multi-Nodo | 1 | 22.96 | 45.64 |
| **Fase 3: K8s Multi-Nodo, 2 Réplicas** | K8s Multi-Nodo | 2 | **23.01** | **43.38** |
| Fase 3: K8s Multi-Nodo, 3 Réplicas | K8s Multi-Nodo | 3 | 21.88 | 170.22 |

---

## 4. Análisis y Conclusiones

### Análisis de Tendencias

1.  **Penalización de K8s:** Se observó un **gran *overhead*** inicial al pasar de Docker Compose a K8s 1 Nodo, reflejado en el aumento drástico de la latencia (74 ms a 527 ms).
2.  **Límite de Recursos Físicos:** El escalado de 1 a 3 réplicas en la Fase 2 (Nodo Único) solo produjo una mejora marginal en el Throughput (de 18.92 a 21.10 RPS). Esto confirma que el **nodo físico (`gp21`)** se convirtió en el cuello de botella, y el escalado de Pods internos fue ineficaz.
3.  **El Poder del Multi-Nodo:** Al liberar los nodos (Fase 3), el rendimiento se disparó. El escenario **Multi-Nodo con 2 réplicas** alcanzó la latencia más baja (43.38 ms) y el Throughput más eficiente, demostrando que la **distribución de la carga** en diferentes máquinas (escalado horizontal de la infraestructura) fue el factor clave para mitigar las limitaciones del *hardware*.
4.  **Nuevo Cuello de Botella:** La caída del rendimiento en el escenario de 3 réplicas Multi-Nodo (21.88 RPS / 170.22 ms) sugiere que la **Base de Datos PostgreSQL** (que no fue escalada horizontalmente) se saturó, convirtiéndose en el nuevo límite del sistema.

### Conclusiones del Proyecto

* **Escalabilidad:** La aplicación es escalable horizontalmente, pero el rendimiento máximo se logra únicamente cuando se **escala la infraestructura (nodos)** junto con la aplicación.
* **Eficiencia:** El despliegue de Kubernetes Multi-Nodo (2 Réplicas) ofreció la configuración más eficiente, superando la línea base de Docker Compose.
* **Recomendación:** Para mejorar aún más el rendimiento, es esencial **escalar la capa de persistencia** (PostgreSQL) y utilizar herramientas de monitorización (como Prometheus/Grafana) para diagnosticar la utilización de recursos de la DB.
