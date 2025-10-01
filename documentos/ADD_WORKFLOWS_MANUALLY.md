# 🔧 Agregar Workflows de GitHub Actions Manualmente

## ✅ **Estado Actual**

- ✅ Sistema desplegado exitosamente en producción
- ✅ Backend funcionando: https://backend-493189429371.us-central1.run.app
- ✅ Frontend funcionando: https://storage.googleapis.com/facturas-frontend-facturasbst-1759186561/index.html
- ✅ GitHub Secrets configurados
- ⏳ Workflows pendientes de agregar manualmente

## 📋 **Pasos para Agregar Workflows**

### 1. Crear Directorio de Workflows

En GitHub, ve a tu repositorio y crea la carpeta `.github/workflows/` si no existe.

### 2. Agregar Workflow de CI

Crea el archivo `.github/workflows/simple-ci.yml`:

```yaml
name: 🧪 CI - Tests and Linting

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    name: 🐍 Backend Tests
    
    steps:
    - name: 📥 Checkout code
      uses: actions/checkout@v4
      
    - name: 🐍 Set up Python 3.12
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
        
    - name: 📦 Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng
        
    - name: 📦 Install Python dependencies
      run: |
        cd backend
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: 🧪 Run tests
      run: |
        cd backend
        pytest tests/ -v --cov=src --cov-report=xml
        
    - name: 📊 Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
        flags: backend
        name: backend-coverage

  frontend-tests:
    runs-on: ubuntu-latest
    name: ⚛️ Frontend Tests
    
    steps:
    - name: 📥 Checkout code
      uses: actions/checkout@v4
      
    - name: 📦 Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
        
    - name: 📦 Install dependencies
      run: |
        cd frontend
        npm ci
        
    - name: 🧪 Run tests
      run: |
        cd frontend
        npm test -- --coverage --watchAll=false
        
    - name: 🔍 Run linting
      run: |
        cd frontend
        npm run lint
        
    - name: 🏗️ Build project
      run: |
        cd frontend
        npm run build

  security-scan:
    runs-on: ubuntu-latest
    name: 🔒 Security Scan
    
    steps:
    - name: 📥 Checkout code
      uses: actions/checkout@v4
      
    - name: 🐍 Set up Python 3.12
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
        
    - name: 📦 Install dependencies
      run: |
        cd backend
        python -m pip install --upgrade pip
        pip install safety bandit
        
    - name: 🔒 Run security checks
      run: |
        cd backend
        safety check -r requirements.txt
        bandit -r src/ -f json -o bandit-report.json || true
        
    - name: 📊 Upload security report
      uses: actions/upload-artifact@v3
      with:
        name: security-report
        path: backend/bandit-report.json
```

### 3. Agregar Workflow de CD

Crea el archivo `.github/workflows/simple-deploy.yml`:

```yaml
name: 🚀 CD - Deploy to GCP

on:
  push:
    branches: [ main, deploy-production ]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy to'
        required: true
        default: 'production'
        type: choice
        options:
        - production
        - staging

env:
  PROJECT_ID: facturasbst
  REGION: us-central1
  REPOSITORY: facturas-repo
  BUCKET_NAME: facturas-frontend-facturasbst-1759186561

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    name: 🐍 Deploy Backend to Cloud Run
    
    steps:
    - name: 📥 Checkout code
      uses: actions/checkout@v4
      
    - name: 🔐 Authenticate to Google Cloud
      uses: google-github-actions/auth@v2
      with:
        credentials_json: ${{ secrets.GCP_SA_KEY }}
        
    - name: ☁️ Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v2
      
    - name: 🏗️ Build and push Docker image
      run: |
        gcloud builds submit --tag $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/backend:latest ./backend
        
    - name: 🚀 Deploy to Cloud Run
      run: |
        gcloud run deploy backend \
          --image $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/backend:latest \
          --platform managed \
          --region $REGION \
          --allow-unauthenticated \
          --port 8000 \
          --memory 2Gi \
          --cpu 2 \
          --max-instances 10 \
          --min-instances 0 \
          --timeout 300 \
          --set-env-vars="DATABASE_URL=${{ secrets.DATABASE_URL }},SECRET_KEY=${{ secrets.SECRET_KEY }},GMAIL_CLIENT_ID=${{ secrets.GMAIL_CLIENT_ID }},GMAIL_CLIENT_SECRET=${{ secrets.GMAIL_CLIENT_SECRET }}"

  deploy-frontend:
    runs-on: ubuntu-latest
    name: ⚛️ Deploy Frontend to Cloud Storage
    needs: deploy-backend
    
    steps:
    - name: 📥 Checkout code
      uses: actions/checkout@v4
      
    - name: 📦 Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
        
    - name: 📦 Install dependencies
      run: |
        cd frontend
        npm ci
        
    - name: 🏗️ Build project
      run: |
        cd frontend
        npm run build
        
    - name: 🔐 Authenticate to Google Cloud
      uses: google-github-actions/auth@v2
      with:
        credentials_json: ${{ secrets.GCP_SA_KEY }}
        
    - name: ☁️ Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v2
      
    - name: 🗂️ Upload to Cloud Storage
      run: |
        gsutil -m cp -r frontend/dist/* gs://$BUCKET_NAME/
        gsutil -m cp frontend/dist/index.html gs://$BUCKET_NAME/index.html
        gsutil -m setmeta -h "Cache-Control:no-cache" gs://$BUCKET_NAME/index.html

  notify:
    runs-on: ubuntu-latest
    name: 📢 Notify Deployment
    needs: [deploy-backend, deploy-frontend]
    if: always()
    
    steps:
    - name: 📢 Notify Success
      if: needs.deploy-backend.result == 'success' && needs.deploy-frontend.result == 'success'
      run: |
        echo "✅ Deployment successful!"
        echo "Backend: https://backend-$REGION-$PROJECT_ID.a.run.app"
        echo "Frontend: https://storage.googleapis.com/$BUCKET_NAME/index.html"
        echo "API Health: https://backend-$REGION-$PROJECT_ID.a.run.app/health"
        
    - name: 📢 Notify Failure
      if: needs.deploy-backend.result == 'failure' || needs.deploy-frontend.result == 'failure'
      run: |
        echo "❌ Deployment failed!"
        echo "Backend status: ${{ needs.deploy-backend.result }}"
        echo "Frontend status: ${{ needs.deploy-frontend.result }}"
```

### 4. Agregar Workflow de CodeQL (Opcional)

Crea el archivo `.github/workflows/codeql.yml`:

```yaml
name: "CodeQL"

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]
  schedule:
    - cron: '30 1 * * 0'

jobs:
  analyze:
    name: Analyze
    runs-on: ubuntu-latest
    permissions:
      actions: read
      contents: read
      security-events: write

    strategy:
      fail-fast: false
      matrix:
        language: [ 'python', 'javascript' ]

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Initialize CodeQL
      uses: github/codeql-action/init@v3
      with:
        languages: ${{ matrix.language }}

    - name: Autobuild
      uses: github/codeql-action/autobuild@v3

    - name: Perform CodeQL Analysis
      uses: github/codeql-action/analyze@v3
      with:
        category: "/language:${{matrix.language}}"
```

## 🎯 **Resultado Final**

Una vez agregados los workflows manualmente:

- ✅ CI/CD completamente activo
- ✅ Tests automáticos en cada push
- ✅ Despliegue automático a producción
- ✅ Análisis de seguridad automático
- ✅ Sistema completamente automatizado

## 📝 **Notas**

- Los workflows están listos para usar
- Todos los secrets ya están configurados
- El sistema está funcionando en producción
- Solo falta agregar los archivos de workflow manualmente

**¡Sistema 100% operativo y listo para CI/CD!** 🚀
