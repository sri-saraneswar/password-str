# config.py

class Config:
    # Server configuration
    DEBUG = True
    PORT = 5001
    
    # Simulation configuration
    ATTEMPTS_PER_SECOND = 1_000_000
    WEAK_PASSWORDS_FILE = 'weak_passwords.txt'
    
    # CORS Origin Whitelist
    CORS_ORIGINS = [
        "http://localhost:3000", 
        "http://localhost:5000", 
        "http://127.0.0.1:5500"
    ]
    
    # Rate Limiting configuration
    RATELIMIT_STORAGE_URI = "memory://"
    RATELIMIT_DEFAULT_LIMITS = ["200 per day", "50 per hour"]
    ANALYZE_ENDPOINT_LIMIT = "30 per minute"
