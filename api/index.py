# api/index.py
from app import app

# Vercel entry point
def handler(request):
    return app(request.environ, lambda status, headers: None)

# For direct imports
if __name__ == "__main__":
    app.run()
