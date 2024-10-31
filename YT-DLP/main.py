from pathlib import Path
from src.downloader import VideoDownloader
import logging



def setup_logging():
    """Configura el sistema de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def get_user_preferences():
    """Obtiene las preferencias del usuario para la descarga"""
    print("\n=== Configuración de Descarga ===")

    # Obtener URL
    url = input("Ingrese la URL del canal o video: ").strip()

    # Obtener ruta de destino
    while True:
        output_path = input("Ingrese la ruta de descarga (Enter para usar ./downloads): ").strip()

        # Asignar un valor por defecto si el usuario no ingresa nada
        if not output_path:
            output_path = "./downloads"

        # Inicializar path aquí para evitar el error
        path = Path(output_path)

        if path.exists() or path.parent.exists():
            break
        print("La ruta no existe. Por favor, ingrese una ruta válida.")

    # Seleccionar secciones a descargar (solo si es URL de canal)
    sections = None
    if '/channel/' in url or '/c/' in url or '/user/' in url or '@' in url:
        print("\nSecciones disponibles:")
        print("1. Videos")
        print("2. Playlists")
        print("3. Releases")
        print("4. Todo")
        while True:
            try:
                section_choice = int(input("Seleccione qué descargar (1-4): "))
                if 1 <= section_choice <= 4:
                    break
            except ValueError:
                pass
            print("Por favor, seleccione una opción válida (1-4)")

        sections = {
            1: ['videos'],
            2: ['playlists'],
            3: ['releases'],
            4: ['videos', 'playlists', 'releases']
        }[section_choice]

    # Seleccionar tipo de formato
    print("\nFormato de descarga:")
    print("1. Audio MP3 (320kbps)")
    print("2. Audio WAV")
    print("3. Video MP4")

    audio_format = None  # Inicializar audio_format como None para evitar el error
    while True:
        try:
            format_choice = int(input("Seleccione el formato (1-3): "))
            if 1 <= format_choice <= 3:
                break
        except ValueError:
            pass
        print("Por favor, seleccione una opción válida (1-3)")

    # Determinar formato_type y audio_format basado en la selección
    if format_choice in [1, 2]:  # Opciones de audio
        format_type = 'audio'
        if format_choice == 1:
            audio_format = 'mp3'
        elif format_choice == 2:
            audio_format = 'wav'
    else:  # Opción de video
        format_type = 'video'

    return {
        'url': url,
        'output_path': output_path,
        'sections': sections,
        'format_type': format_type,
        'audio_format': audio_format,
    }


def main():
    setup_logging()

    try:
        downloader = VideoDownloader()
        preferences = get_user_preferences()

        print("\nIniciando descarga...")
        success = downloader.download_channel(
            url=preferences['url'],
            output_path=preferences['output_path'],
            sections=preferences['sections'],
            format_type=preferences['format_type'],
            audio_format=preferences['audio_format']
        )

        if success:
            print("\n¡Descarga completada exitosamente!")
        else:
            print("\nLa descarga finalizó con algunos errores. Revisa los logs para más detalles.")

    except KeyboardInterrupt:
        print("\nDescarga cancelada por el usuario.")
    except Exception as e:
        print(f"\nError inesperado: {str(e)}")
        logging.error(f"Error inesperado: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()
