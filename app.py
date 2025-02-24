from app_instance import app

# Import routes
from routes.auth_routes import auth_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')

from routes.ocr_routes import ocr_bp

# Register OCR blueprint
app.register_blueprint(ocr_bp, url_prefix='/ocr')

if __name__ == '__main__':
    app.run(debug=True)
