<div align="center">
  <a href="#pt-br">🇧🇷</a> | <a href="#en">🇬🇧</a>
</div>

---

<a id="pt-br"></a>
# Lacrei Saúde - API Rest (Desafio Técnico) 🇧🇷

API RESTful desenvolvida para o desafio técnico da vaga de **voluntariado** da Lacrei Saúde. O sistema gerencia o cadastro de profissionais de saúde e seus respectivos agendamentos de consultas, com foco em segurança, integridade de dados e boas práticas de engenharia de software.

## Tecnologias Utilizadas

A stack utilizada segue os [requisitos](https://lacrei-saude.notion.site/Desafio-Back-end-32a28e22d088463ab4bee78ff394c5f9) do exercício, evidenciando o foco em produtividade, segurança e facilidade de deploy:

* **Backend:** Python 3.14 + Django 5 + Django REST Framework (DRF)
* **Banco de Dados:** PostgreSQL 15
* **Infraestrutura:** Docker & Docker Compose
* **Gerenciamento de Pacotes:** Poetry
* **CI/CD:** GitHub Actions (Pipeline de testes automatizados com integração CI/CD)
* **Autenticação:** JWT (JSON Web Tokens) via djangorestframework-simplejwt

## Como Executar o Projeto Localmente

O projeto foi totalmente containerizado para garantir que funcione em qualquer ambiente.

### 1. Preparando as Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto baseado no arquivo de exemplo:
```bash
cp .env.example .env

```

### 2. Subindo a Infraestrutura (Docker)

Construa e inicie os containers do banco de dados e da aplicação:

```bash
docker compose up --build

```

### 3. Criando as Tabelas e o Usuário Admin

Em outro terminal, execute as migrações e crie o seu usuário mestre:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser

```

A API estará disponível em `http://localhost:8000/api/v1/`.

## Documentação Interativa da API (OpenAPI 3)

A API possui documentação viva e interativa gerada automaticamente via `drf-spectacular`. Com a aplicação rodando localmente, acesse:

* **Swagger UI (Playground interativo):** [http://localhost:8000/api/docs/swagger/](https://www.google.com/search?q=http://localhost:8000/api/docs/swagger/)
* **Redoc (Leitura estruturada):** [http://localhost:8000/api/docs/redoc/](https://www.google.com/search?q=http://localhost:8000/api/docs/redoc/)

## Segurança e Validações

* **Autenticação JWT:** Todas as rotas (exceto a obtenção de token) estão protegidas. É necessário enviar o token no Header `Authorization: Bearer <token>`.
* **CORS:** Configurado para permitir integrações seguras com o front-end.
* **Tratamento de Credenciais:** Usuários e senhas são trafegados como strings puras na camada da aplicação. Esta decisão assume que a criptografia e o hashing (PBKDF2 por padrão no Django) ocorrem antes da persistência, e que o tráfego é protegido por camadas externas de transporte (TLS/SSL/HTTPS).
* **Sanitização de Dados:** Serializers configurados para remover espaços em branco invisíveis (`trim_whitespace`), bloquear nomes com números e forçar a formatação de telefones (apenas dígitos, 10 ou 11 caracteres).
* **Proteção contra SQL Injection:** Garantida by-design. O framework não concatena strings para consultas ao banco; o ORM do Django utiliza exclusivamente *Parameterized Queries* (consultas parametrizadas) por baixo dos panos, neutralizando tentativas de injeção de código SQL.
* **Logs de Acesso e Erro:** O sistema foi configurado seguindo o padrão 12-Factor App. Todos os logs de requisições (`django`) e exceções/erros (`django.request`) são direcionados para a saída padrão (stdout/console), permitindo que orquestradores modernos (como o ECS da AWS) capturem e indexem a saúde da aplicação em tempo real.

## Decisões Arquiteturais e Dívida Técnica (V2)

Durante o desenvolvimento deste MVP, algumas decisões estratégicas foram tomadas visando o equilíbrio entre o tempo de entrega e a integridade do sistema:

* **Soft Delete para Profissionais (Implementado):** A exclusão física (Hard Delete) foi substituída por exclusão lógica (campo `is_active=False`) sobrescrevendo o método `destroy` da View. O model também possui proteção (`models.PROTECT`) nas chaves estrangeiras para impedir exclusão acidental no banco.
* **Integração de Saúde (Implementado):** O projeto já contempla a lógica de negócio para integração com serviços de saúde, garantindo a separação de papéis entre o profissional e os agendamentos.
* **Integração Financeira (Mock Asaas):** Para demonstrar o domínio sobre o ciclo de vida de uma requisição e a comunicação com APIs de terceiros, a rota de criação de agendamentos foi customizada. Ao nascer uma consulta, a View orquestra uma chamada a um serviço simulado do gateway Asaas, gerando um ID de transação e injetando um `payment_link` na resposta de sucesso (201 Created) devolvida ao paciente.
* **Máquina de Estados vs Booleano (Roadmap V2):** Atualmente o status do profissional é gerenciado por um booleano. Para a V2, a arquitetura ideal prevê a substituição por uma State Machine (`StatusChoices: PENDING, ACTIVE, SUSPENDED, INACTIVE`) para dar maior visibilidade analítica sobre a jornada de onboarding.
* **Auditoria de Consultas (Roadmap V2):** No escopo atual, a exclusão de consultas ocorre via Hard Delete. Visando melhorar a rastreabilidade dos eventos, o mapeamento futuro exige a aplicação de um campo de status (`SCHEDULED, COMPLETED, CANCELED`) também nas consultas.

## Testes Automatizados

O projeto conta com uma suíte de testes cobrindo regras de negócio, bloqueios de segurança e o CRUD completo (utilizando `APITestCase`). A pipeline de CI roda automaticamente a cada push via GitHub Actions.

Para rodar os testes localmente:

```bash
docker compose exec web python manage.py test api

```

## Fluxo de Deploy (CI/CD) e Infraestrutura AWS

A arquitetura foi desenhada para operar em nuvem (proposta para AWS ECS/Fargate), com separação estrita de contextos.

### 1. Separação de Ambientes (Staging vs Produção)

Embora consumam a mesma base de código do repositório, os ambientes são isolados fisicamente e por contexto:

* **Isolamento de Dados:** Staging e Produção apontam para bancos de dados PostgreSQL (RDS) completamente distintos, garantindo que testes de QA não afetem clientes reais.
* **Isolamento de Configuração:** O comportamento da aplicação é ditado por variáveis de ambiente (`.env`). No Staging, o `DEBUG` pode ser ativado e as integrações apontam para Sandboxes. Na Produção, o `DEBUG` é rigorosamente `False` e as credenciais são injetadas via AWS Secrets Manager.

### 2. A Esteira de CI/CD (GitHub Actions)

O pipeline automatizado (`.github/workflows/ci.yml`) garante a qualidade antes de qualquer código chegar à nuvem:

1. **Integração (CI):** A cada push, a esteira sobe um banco PostgreSQL efêmero, executa o Linter (Ruff) e roda toda a suíte de testes.
2. **Entrega (CD):** Se (e somente se) a branch for a `master/main` e os testes passarem, a esteira realiza o build da imagem Docker e a publica automaticamente no GitHub Container Registry (GHCR), gerando um artefato imutável pronto para deploy.

### 3. Servidor de Produção

Para a produção, o servidor embutido de desenvolvimento do Django é descartado. O projeto conta com um `docker-compose.prod.yml` que sobe a aplicação utilizando o **Gunicorn** (servidor WSGI padrão da indústria) configurado com múltiplos workers para suportar alta concorrência.

### 4. Estratégia de Rollback

Como a entrega é baseada em artefatos Docker imutáveis gerados pelo CI, o rollback é **determinístico e instantâneo**. Caso a versão recém-implantada apresente falha crítica em Produção, o fluxo de reversão consiste em atualizar a Task Definition do AWS ECS para apontar novamente para a tag da imagem Docker imediatamente anterior (ex: `v1.1.0`), substituindo os containers defeituosos em segundos, evitando que o sistema fique indisponível por muito tempo.

---

<a id="en"></a>

# Lacrei Saúde - REST API (Technical Challenge) 🇬🇧

RESTful API developed for the technical challenge of the **volunteer** position at Lacrei Saúde. The system manages the registration of healthcare professionals and their respective appointment schedules, focusing on security, data integrity, and software engineering best practices.

## Technologies Used

The stack follows the [requirements](https://lacrei-saude.notion.site/Desafio-Back-end-32a28e22d088463ab4bee78ff394c5f9) of the exercise, highlighting the focus on productivity, security, and ease of deployment:

* **Backend:** Python 3.14 + Django 5 + Django REST Framework (DRF)
* **Database:** PostgreSQL 15
* **Infrastructure:** Docker & Docker Compose
* **Package Management:** Poetry
* **CI/CD:** GitHub Actions (Automated testing pipeline with CI/CD integration)
* **Authentication:** JWT (JSON Web Tokens) via djangorestframework-simplejwt

## How to Run the Project Locally

The project is fully containerized to ensure it works in any environment.

### 1. Preparing Environment Variables

Create a `.env` file in the project root based on the example file:

```bash
cp .env.example .env

```

### 2. Starting the Infrastructure (Docker)

Build and start the database and application containers:

```bash
docker compose up --build

```

### 3. Creating Tables and Admin User

In another terminal, run migrations and create your master user:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser

```

The API will be available at `http://localhost:8000/api/v1/`.

## Interactive API Documentation (OpenAPI 3)

The API features live, interactive documentation automatically generated via `drf-spectacular`. With the application running locally, access:

* **Swagger UI (Interactive Playground):** [http://localhost:8000/api/docs/swagger/](https://www.google.com/search?q=http://localhost:8000/api/docs/swagger/)
* **Redoc (Structured Reading):** [http://localhost:8000/api/docs/redoc/](https://www.google.com/search?q=http://localhost:8000/api/docs/redoc/)

## Security and Validations

* **JWT Authentication:** All routes (except token retrieval) are protected. It is necessary to send the token in the Header `Authorization: Bearer <token>`.
* **CORS:** Configured to allow secure integrations with the front-end.
* **Credential Handling:** Usernames and passwords are treated as raw strings at the application layer. This decision assumes that encryption and hashing (PBKDF2 by default in Django) occur before persistence, and that traffic is protected by external transport layers (TLS/SSL/HTTPS).
* **Data Sanitization:** Serializers configured to remove invisible whitespaces (`trim_whitespace`), block names with numbers, and force phone formatting (digits only, 10 or 11 characters).
* **SQL Injection Protection:** Guaranteed by-design. The framework does not concatenate strings for database queries; the Django ORM exclusively uses *Parameterized Queries* under the hood, neutralizing any SQL injection attempts.
* **Access and Error Logs:** The system is configured following the 12-Factor App methodology. All request logs (`django`) and exceptions/errors (`django.request`) are routed to standard output (stdout/console), allowing modern orchestrators (like AWS ECS) to capture and index the application's health in real-time.

## Architectural Decisions and Technical Debt (V2)

During the development of this MVP, some strategic decisions were made to balance delivery time and system integrity:

* **Soft Delete for Professionals (Implemented):** Physical deletion (Hard Delete) was replaced by logical deletion (`is_active=False` field) by overriding the View's `destroy` method. The model also has protection (`models.PROTECT`) on foreign keys to prevent accidental database deletion.
* **Health Integration (Implemented):** The project already includes the business logic for integration with health services, ensuring the separation of roles between the professional and appointments.
* **Financial Integration (Mock Asaas):** To demonstrate mastery over a request's lifecycle and communication with Third-Party APIs, the appointment creation route was customized. When an appointment is created, the View orchestrates a call to a simulated Asaas gateway service, generating a transaction ID and injecting a `payment_link` into the success response (201 Created) returned to the patient.
* **State Machine vs. Boolean (Roadmap V2):** Currently, the professional's status is managed by a boolean. For V2, the ideal architecture foresees replacement with a State Machine (`StatusChoices: PENDING, ACTIVE, SUSPENDED, INACTIVE`) to provide greater analytical visibility into the onboarding journey.
* **Appointment Auditing (Roadmap V2):** In the current scope, appointment deletion occurs via Hard Delete. Aiming to improve event traceability, future mapping requires applying a status field (`SCHEDULED, COMPLETED, CANCELED`) to appointments as well.

## Automated Tests

The project includes a test suite covering business rules, security blocks, and the full CRUD (using `APITestCase`). The CI pipeline runs automatically on every push via GitHub Actions.

To run tests locally:

```bash
docker compose exec web python manage.py test api

```

## Deploy Flow (CI/CD) and AWS Infrastructure

The architecture is designed to operate in the cloud (proposed for AWS ECS/Fargate), with strict context separation.

### 1. Environment Separation (Staging vs Production)

Although they consume the same code base from the repository, the environments are isolated physically and by context:

* **Data Isolation:** Staging and Production point to completely distinct PostgreSQL (RDS) databases, ensuring that QA tests do not affect real clients.
* **Configuration Isolation:** Application behavior is dictated by environment variables (`.env`). In Staging, `DEBUG` can be activated, and integrations point to Sandboxes. In Production, `DEBUG` is strictly `False`, and credentials are injected via AWS Secrets Manager.

### 2. The CI/CD Pipeline (GitHub Actions)

The automated pipeline (`.github/workflows/ci.yml`) guarantees quality before any code reaches the cloud:

1. **Integration (CI):** On every push, the pipeline spins up an ephemeral PostgreSQL database, executes the Linter (Ruff), and runs the entire test suite.
2. **Delivery (CD):** If (and only if) the branch is `master/main` and the tests pass, the pipeline builds the Docker image and automatically publishes it to the GitHub Container Registry (GHCR), generating an immutable artifact ready for deployment.

### 3. Production Server

For production, Django's built-in development server is discarded. The project features a `docker-compose.prod.yml` that runs the application using **Gunicorn** (the industry-standard WSGI server) configured with multiple workers to support high concurrency.

### 4. Rollback Strategy

Since delivery is based on immutable Docker artifacts generated by CI, rollback is **deterministic and instantaneous**. In case the newly deployed version encounters a critical failure in Production, the reversion flow consists of updating the AWS ECS Task Definition to point back to the immediately previous Docker image tag (e.g., `v1.1.0`), replacing the faulty containers in seconds and preventing prolonged system downtime.
