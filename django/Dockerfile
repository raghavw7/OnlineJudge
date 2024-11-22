# Use Python 3.10 base image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Install Node.js and npm
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g npm@latest

# Set npm registry and enable caching
RUN npm config set registry=http://registry.npmjs.org/
RUN npm config set cache=/app/.npm-cache --global

# Pre-install lodash.sortby to avoid dependency resolution issues
RUN npm install lodash.sortby@4.7.0 --verbose

# Copy frontend code and handle React dependencies
COPY ./frontend /app/frontend
ENV CI=true
RUN cd /app/frontend && npm cache clean --force && \
    NODE_OPTIONS=--max_old_space_size=4096 npm install --legacy-peer-deps --verbose && npm run build

# Copy the rest of the application code
COPY . .

# Collect static files for Django
RUN python manage.py collectstatic --noinput

# Add and set permissions for the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]
