# Example .env.tpl template
# To generate .env: op inject -i .env.tpl -o .env

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=admin
DB_PASSWORD="op://Dev/MyProject/db_password"

# API Keys
API_KEY="op://Dev/MyProject/api_key"
STRIPE_SECRET_KEY="op://Dev/MyProject/stripe_secret"

# Feature Flags (non-secrets)
ENABLE_ANALYTICS=true
DEBUG_MODE=false
