# Sentinel
A multiplatform distributed telemetry system designed to collect, process, and store metrics from remote server infrastructure.
<center>

![Sentinel Arquitecture](docs/Arquitecture.svg)
</center>

## Overview

Sentinel is a multi-agent telemetry system designed to collect infrastructure metrics from distributed servers. \
Agents gather metrics such as CPU, RAM, and GPU usage, as well as failed SSH login attempts. The collected data is sent to an EC2 virtual machine and routed through a reverse proxy to a FastAPI service, where it is processed and stored in a Cassandra cluster.

## Architecture

The project implements a client-server architecture geared towards efficient telemetry collection and server monitoring. The entire backend environment is centralized in the cloud using an AWS EC2 instance, provisioned as Infrastructure as Code (IaC). The design prioritizes perimeter security through a reverse proxy and the isolation of internal services via containerization, ensuring that critical components are not directly exposed to the internet.
<center>

![Sentinel Arquitecture](docs/Arquitecture.svg)
</center>

### System Components

The system is divided into the following main blocks:

- **Agent (Client):** A lightweight collector script running on target machines to extract hardware metrics and security logs.

- **Reverse Proxy (NGINX):** Acts as the single entry point to the server. It receives external traffic and routes it internally, hiding the network topology and container ports for security purposes.

- **Backend API (FastAPI):** The core of the business logic. It receives payloads from the agent, validates authentication, and processes the information.

- **Database (Apache Cassandra):** A NoSQL wide-column store cluster, ideal for massive write operations and time-series data.

- **Infrastructure (AWS & Terraform):** The virtualized environment where the containers reside, managed in an automated and reproducible way.

### Data Flow

The information lifecycle follows a strict process:

1. **Collection:** The agent extracts local metrics (CPU, RAM, GPU usage) and logs failed SSH connection attempts.

2. **Transmission:** The data is sent to the public IP of the EC2 instance.

3. **Interception:** NGINX receives the web request and securely forwards it to the internal API container.

4. **Validation:** FastAPI verifies the headers. The API Key is securely validated here (avoiding a hardcoded key on the client side), mitigating the risk of unauthorized access.

5. **Persistence:** If the validation is successful, FastAPI executes the write operation to the Cassandra cluster, where the data is sorted and stored for subsequent analysis.

### Technology Stack

- **Language:** Python

- **Web Framework:** FastAPI

- **Reverse Proxy:** NGINX

- **Database:** Apache Cassandra

- **Containers:** Docker & Docker Compose

- **Infrastructure as Code (IaC):** Terraform

- **Cloud Provider:** Amazon Web Services (EC2)

### Produccion Recomendations

Although the current architecture is optimized for portability and leveraging the AWS Free Tier, to scale this system to a massive production environment (thousands of concurrent agents), the following architectural evolutions are proposed:

1. **Decoupling with Message Brokers (RabbitMQ / Kafka):** Interposing a message queue broker between FastAPI and the database. This acts as a buffer to handle extreme traffic spikes, enabling asynchronous processing, reducing API latency to near zero, and preventing the saturation of direct database connections.

2. **Migration to a Managed Database (Amazon DynamoDB):** Replacing the local Cassandra cluster with a fully managed, serverless service like DynamoDB. This eliminates the operational overhead of maintaining database containers, ensuring automatic horizontal scalability and native high availability within the AWS ecosystem.

## Project Structure

```
proyecto-sentinel/
├── docker-compose.yml          # Orchestrates the API and Cassandra services
├── docs/                       # Documentation
├── terraform/
│   └── main.tf                 # AWS infrastructure provisioning (EC2, security group, key pair)
└── sentinel-api/
    ├── Dockerfile              # Container image for the FastAPI service
    ├── requirements.txt        # Pinned Python dependencies
    ├── main.py                 # FastAPI app entry point; registers routers and DB lifecycle hooks
    ├── models.py               # Pydantic schema for incoming telemetry payloads
    ├── database.py             # Cassandra connection management (init, session, teardown)
    ├── agent/
    │   └── agent.py            # Standalone client script: collects and ships metrics to the API
    └── routers/
        └── telemetry.py        # POST /telemetry/ endpoint with API key authentication
```

## Example Telemetry Data

A payload sent by an agent to `POST /telemetry/` looks like this:

```json
{
  "server_name": "arch-workstation",
  "cpu_usage": 34.7,
  "ram_usage": 61.2,
  "gpu_usage": 12.5,
  "failed_ssh_attempts": 3
}
```

The request must include the API key in the header:

```
X-API-Key: <your-sentinel-api-key>
```

On success, the API responds with:

```json
{
  "status": "success",
  "message": "Telemetría guardada en Cassandra"
}
```

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- Python 3.11+ (for running the agent locally)
- An `.env` file inside `sentinel-api/` with the following variable:

```env
SENTINEL_API_KEY=your_secret_key_here
```

### 1. Start the Backend Stack

```bash
docker compose up --build -d
```

This launches two containers:
- `sentinel-api-v3` — the FastAPI service on port `8000`
- `sentinel-cassandra` — the Cassandra database on port `9042`

### 2. Verify the API is Running

```bash
curl http://localhost:8000/health
```

### 3. Run the Agent

On any machine you want to monitor, install the agent dependencies and execute it:

```bash
pip install psutil requests python-dotenv
python sentinel-api/agent/agent.py
```

The agent will collect local CPU, RAM, GPU, and failed SSH metrics and POST them to the API endpoint.


## Roadmap

This project is in continuous evolution. While the current version provides a solid and functional foundation, the following enhancements are planned for future iterations:

- [ ] **Message Broker Integration:** Implement Apache Kafka as a messaging queue between the FastAPI backend and the database. This will allow the system to handle high concurrency, manage traffic spikes, and enable asynchronous data processing.

- [ ] **CI/CD Pipelines:** Establish Continuous Integration and Continuous Deployment (CI/CD) workflows (e.g., using GitHub Actions) to automate testing, container image builds, and the Terraform infrastructure provisioning.

- [ ] **Data Visualization:** Deploy Grafana to create interactive, real-time dashboards. This will transform the raw telemetry data and security logs into beautiful, easy-to-monitor visual metrics.

Continuous Improvement: The architecture is designed to be extensible, leaving room for future additions such as real-time alerting systems or migrating to managed cloud services as new requirements arise.

## Motivation

Sentinel was developed as a hands-on project to deepen my practical understanding of Infrastructure as Code (IaC) using Terraform within a real-world cloud environment.

By leveraging the AWS Free Tier, my goal was to build a fully functional data pipeline from scratch. This project has been instrumental in solidifying my knowledge of how containerized applications (Docker) operate in production, how to design scalable backend architectures, and how to implement essential security practices in a cloud ecosystem.
