from pydantic_settings import BaseSettings, SettingsConfigDict

# Clase que hereda de BaseSettings para cargar automáticamente
# la configuración desde variables de entorno (.env)
class Settings(BaseSettings):
    
    # URL de conexión a la base de datos
    database_url: str
    # Variable para el nombre de la app
    app_name: str
    # Variable para poder ver las consultas SQL
    debug: bool
    # Variable que permite acceder al frontend
    allowed_origins: list[str]
    
    # Guarda la instancia de SettingsConfigDict(sirve en este caso para señalar que archivo leer '.env' y en que formato 'utf-8')
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

# Instancia única de la configuración para reutilizarla
# en toda la aplicación
settings = Settings()
