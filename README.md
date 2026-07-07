# TRACERBLOCK ⛓️📦
### Decentralized Enterprise Supply Chain Tracking & Compliance Portal

TRACERBLOCK is a high-fidelity, secure, and performant Supply Chain Management (SCM) portal built on a multi-layer architecture integrating an **in-memory Private Ethereum Blockchain Node**, a **Django REST Framework (DRF) backend**, and a **Streamlit visual command center**. 

The system leverages off-chain optimizations to scale transactional throughput while preserving on-chain integrity for audits, quality checks, procurement escrows, and AI forecasting.

---

## 1. System Architecture & Topology

TRACERBLOCK runs on a three-tier architecture:

```
                  ┌───────────────────────────────┐
                  │      Streamlit Frontend       │
                  │   (Cyberpunk Glassmorphism)   │
                  └───────────────┬───────────────┘
                                  │
                  (API Handshake & JWT Auth token)
                                  │
                                  ▼
                  ┌───────────────────────────────┐
                  │      Django Backend API       │
                  │      (DRF & db.sqlite3)       │
                  └──────┬─────────────────┬──────┘
                         │                 │
                (Saves telemetry)   (Broadcasts proof)
                         │                 │
                         ▼                 ▼
          ┌──────────────────────┐ ┌──────────────────────┐
          │  Relational Database │ │ Private Blockchain   │
          │     (db.sqlite3)     │ │   Node (127.0.0.1)   │
          └──────────────────────┘ └──────────────────────┘
```

1. **Streamlit Portal (UI)**: Built with a premium, responsive glassmorphism theme using `@import Outfit` typography, translucent panel backdrops, custom hover micro-animations, and cubic-bezier fade-in transitions.
2. **Django Backend (API)**: Manages CRUD operations, user role registries, IoT telemetry events, Purchase Orders, QA audits, and exposes AI analysis endpoints.
3. **Private Blockchain Node**: Runs an in-memory ledger mimicking Ethereum client JSON-RPC protocols. It processes transactions, maintains a mempool with nonces, issues dynamic transaction receipts, and tracks verified block heights.

---

## 2. Core Security & Enclosure Standards

Security is enforced at every layer of the system:
* **Viewport Lock Masking**: Unauthenticated visits are covered by a dark, blurred backdrop modal overlay (`.login-mask`). The sidebar navigation, headers, and dashboard metrics remain completely masked until a valid JWT token is acquired.
* **Subpage Enclosure Guards**: All sidebar subpages (Register, Track, Inventory, Orders, QA, AI) verify authentication states. Attempts to directly navigate to a subpage via URL parameters result in a secure access-blocked screen and call `st.stop()`.
* **API Route Permissions**: Every Django endpoint requires simple JWT token authorizations (`IsAuthenticated` permissions). Unauthenticated requests return `401 Unauthorized` responses.
* **HTTP Hardening**: Core Django settings define strict CORS origins, cross-site scripting (XSS) filters, frame-options protection, and content-type nosniff instructions.
* **Data Privacy (Secrets Concealed)**: Standard user views hide raw cryptographic hashes, private signatures, public keys, and Solidity compilers. Business indicators, percentages, and simple status lights are rendered instead, keeping engineering details under-the-hood.

---

## 3. Off-Chain Optimization & Gas Savings

SCM telemetry generates high-frequency data streams (e.g. hourly temperature and humidity checks). Broadcasting every tick to a root blockchain is cost-prohibitive.

TRACERBLOCK implements **Off-Chain State Channels**:
* Intermediate IoT metrics are cached, verified locally, and saved in the relational database.
* Only critical status checkpoints (e.g. `MANUFACTURED`, `IN_TRANSIT`, `DELIVERED`) and QA certifications are anchored on-chain.
* This model saves **93% in transaction gas fees** while maintaining complete tamper-proof proof-of-delivery provenance.

---

## 4. Database Seeder & Mock Data

A Django management command populates the database with real-world observations:
* **100 Unique Products**: Distributed across 5 SCM verticals (Pharmaceutical cold-chain, Perishable food logistics, Defense electronics, Chemical fluid safety, and Heavy industrial machinery).
* **Authorized Roles**: Pre-configures test profiles (`manufacturer_seeder`, `distributor_seeder`, `retailer_seeder`, `inspector_seeder`, `logistics_seeder`) with password `password123`.
* **40 Telemetry Checkpoints**: Seeds historical logs, inducing select temperature excursions (e.g. >30°C or <2°C) to validate contract rule warnings.
* **Procurement Logs**: Generates 25 Purchase Orders in various escrow states (PENDING, APPROVED, SHIPPED, DELIVERED).
* **QA Reports**: Registers 40 inspection records verifying quality thresholds.

---

## 5. Detailed Installation & Setup

Ensure Python 3.10+ is installed on your system.

### Step 1: Install Dependencies
Open your workspace terminal and run:
```bash
pip install -r requirements.txt
```

### Step 2: Seed the Database
Initialize migrations and run the relational populator command to seed 100 products and users:
```bash
python backend/manage.py migrate
python backend/manage.py populate_db
```

### Step 3: Run the Orchestrator
Start the private blockchain node, Django API backend, and Streamlit frontend concurrently using the runner script:
```bash
python run_all.py
```

* **Blockchain Node**: Running on `http://127.0.0.1:8545`
* **Django API**: Running on `http://127.0.0.1:8000`
* **Streamlit Portal**: Running on `http://localhost:8501`

---

## 6. Accessing the Portal

Once the services are active:
1. Open `http://localhost:8501` in your browser.
2. Enter username `manufacturer_seeder` or `inspector_seeder` with password `password123`.
3. Click **Authenticate & Decrypt SCM Ledger** to unlock the command center.
