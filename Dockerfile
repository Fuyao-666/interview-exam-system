# Stage 1: Build frontend
FROM node:20-alpine AS build-frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Production
FROM python:3.11-slim
WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy frontend build output from stage 1
COPY --from=build-frontend /app/frontend/dist ./frontend/dist

# Expose port
EXPOSE 8080

# Start with gunicorn
CMD ["gunicorn", "--chdir", "backend", "app:app", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120"]
