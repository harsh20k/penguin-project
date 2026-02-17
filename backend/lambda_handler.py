"""AWS Lambda entrypoint: wrap FastAPI app with Mangum (ASGI)."""
from mangum import Mangum
from app.main import app

handler = Mangum(app)
