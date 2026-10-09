# RansomGuard AI - Frontend

Frontend interface for **RansomGuard AI** (AI-Powered Intelligent Storage Protection & Recovery System), built with React, TypeScript, Vite, React Router, Framer Motion, Recharts, and Lucide Icons.

## 📁 Project Architecture

```
frontend/
├── public/
│   ├── assets/
│   │   ├── images/
│   │   └── icons/
│   └── favicon.svg
│
├── src/
│   ├── assets/
│   ├── components/
│   │   ├── layout/       # AppLayout, Header, Sidebar, PageContainer
│   │   ├── dashboard/    # StatCard, StorageHealth, ThreatOverview, etc.
│   │   ├── common/       # GlassCard, Button, Badge, Modal, LoadingSpinner
│   │   └── charts/       # ActivityChart, StorageChart, ThreatChart
│   │
│   ├── pages/            # 9 Route pages (Dashboard, Storage, LiveMonitor, etc.)
│   ├── layouts/          # DashboardLayout (React Router Outlet layout)
│   ├── routes/           # AppRoutes configuration
│   ├── hooks/            # Custom React hooks (useStorage, useThreats, useFileMonitor)
│   ├── services/         # API services layer
│   ├── data/             # Mock telemetry & incident data layer
│   ├── types/            # TypeScript interfaces & types
│   ├── utils/            # Formatters, constants, helpers
│   ├── styles/           # globals.css, liquid-ui.css, animations.css
│   ├── App.tsx
│   └── main.tsx
│
├── .env
├── .env.example
├── package.json
└── vite.config.ts
```

## 🚀 Getting Started

### Install Dependencies
```bash
npm install
```

### Run Local Development Server
```bash
npm run dev
```

### Production Build
```bash
npm run build
```
