from app_instance import app
import os

# Import routes
from routes.auth_routes import auth_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')

from routes.ocr_routes import ocr_bp

# Register OCR blueprint
app.register_blueprint(ocr_bp, url_prefix='/ocr')

from routes.document_routes import document_bp

# Register document blueprint
app.register_blueprint(document_bp, url_prefix='/docs')

from routes.chat_routes import chat_bp

# Register chat blueprint
app.register_blueprint(chat_bp)


PORT= int(os.getenv("PORT"))
if __name__ == '__main__':
    app.run(port=PORT)
