from flask_restx import Api

api = Api(
    title="Industria API",
    version="1.0",
    description="Documentation de l'API Industria (parcelles, zones, RDV...)",
    doc="/docs",
    prefix="/api",
    default="swagger",
    default_label="Doc Swagger"
)
