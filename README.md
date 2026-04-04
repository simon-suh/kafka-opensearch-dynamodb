# Kafka + OpenSearch + DynamoDB

A hybrid data pipeline using Apache Kafka for message streaming, OpenSearch for indexing and visualization, and DynamoDB on AWS for cloud persistence. Local services run in Docker Compose. DynamoDB is provisioned on AWS with Terraform.

## Architecture

```
Local (Docker Compose)
│
├── Producer App (Python)
│   ├── validates schema --> Schema Registry
│   └── publishes messages --> Apache Kafka
│
├── Kafka Cluster
│   ├── Schema Registry   :8081
│   ├── Apache Kafka      :9092 (internal) / :29092 (external)
│   └── Zookeeper         :2181
│
├── Consumer App (Python)
│   ├── validates schema --> Schema Registry
│   ├── writes to ------->  OpenSearch
│   └── writes to ------->  DynamoDB (AWS)
│
├── OpenSearch            :9200
├── OpenSearch Dashboards :5601
└── Grafana               :3000

AWS (Terraform)
└── DynamoDB
```

## Tech Stack

| Category | Technology |
|---|---|
| Messaging | Apache Kafka, Schema Registry, Zookeeper |
| Search & Storage | OpenSearch, OpenSearch Dashboards |
| Cloud | DynamoDB (AWS) |
| Monitoring | Grafana |
| Languages | Python (confluent-kafka, opensearch-py, boto3) |
| Infrastructure | Docker Compose, Terraform |

## Getting Started

### Prerequisites

- Docker Desktop
- Python 3.x
- AWS CLI configured with a profile
- Terraform

### Start local services

```bash
docker compose up -d
```

### Provision DynamoDB on AWS

```bash
cd terraform
terraform init
terraform apply
```

### Run the producer

```bash
python producer.py
```

### Run the consumer

```bash
python consumer.py
```

## Service Endpoints

| Service               | URL                          |
|-----------------------|------------------------------|
| Kafka (external)      | localhost:29092               |
| Schema Registry       | http://localhost:8081         |
| OpenSearch            | http://localhost:9200         |
| OpenSearch Dashboards | http://localhost:5601         |
| Grafana               | http://localhost:3000         |

## Verify

Check messages are landing in Kafka:

```bash
docker exec -it kafka kafka-console-consumer.sh \
  --bootstrap-server kafka:9092 \
  --topic events \
  --from-beginning
```

Check OpenSearch has indexed documents:

```bash
curl http://localhost:9200/events/_count
```

Check DynamoDB has received records:

```bash
aws dynamodb scan --table-name events
```

Open OpenSearch Dashboards at http://localhost:5601 and confirm the `events` index appears under **Index Management**.

Open Grafana at http://localhost:3000 and confirm the OpenSearch data source is connected under **Connections > Data Sources**.

## Teardown

Stop and remove local containers and volumes:

```bash
docker compose down -v
```

The `-v` flag removes volumes, including all stored data. Docker will confirm with a "Total reclaimed space" message.

Destroy AWS infrastructure:

```bash
cd terraform
terraform destroy
```
