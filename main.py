#!/usr/bin/env python
import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check required environment variables
required_vars = ["LINKEDIN_COOKIE", "OPENAI_API_KEY", "POSTGRES_HOST", "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD"]
missing_vars = [var for var in required_vars if not os.environ.get(var)]

if missing_vars:
    print(f"Missing required environment variables: {', '.join(missing_vars)}")
    print("Please set them in the .env file or environment before running the server.")
    exit(1)

if __name__ == "__main__":
    # Run the FastAPI server
    uvicorn.run(
        "recruitment.api:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )