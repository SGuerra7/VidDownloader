from pathlib import Path
import logging
from typing import Dict, List
from yt_dlp import YoutubeDL
import re

class VideoDownloader:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _progress_hook(self, d):
        """Hook de progreso para la descarga"""
        if d['status'] == 'downloading':
            self.logger.info(f"Progreso: {d['_percent_str']} - Velocidad: {d['_speed_str']} - ETA: {d['_eta_str']}")
        elif d['status'] == 'finished':
            self.logger.info("Descarga completada, procesando...")

    def _sanitize_filename(self, name: str) -> str:
        """Limpia el nombre del archivo eliminando caracteres no permitidos"""
        return re.sub(r'[/:*?"<>|]', "", name)

    def _get_channel_sections(self, url: str) -> Dict:
        """Obtiene información de las secciones del canal. Aquí se usa un ejemplo básico."""
        return {
            'channel_name': 'Nombre del Canal',
            'sections': ['playlists', 'videos', 'releases']
        }

    def _get_base_options(self, output_path: str, format_type: str = 'audio', audio_format: str = 'mp3') -> Dict:
        """
        Configura las opciones base para yt-dlp, permitiendo la descarga en diferentes formatos de audio.
        """
        base_opts = {
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': True,
            'extract_flat': False,
            'progress_hooks': [self._progress_hook],
            'outtmpl': str(Path(output_path) / '%(title)s.%(ext)s'),
        }

        if format_type == 'audio':
            base_opts.update({
                'format': 'bestaudio/best',
                'writethumbnail': True,
                'embedthumbnail': True,
                'addmetadata': True,
                'prefer_ffmpeg': True,
                'postprocessors': [
                    # Primero extraemos el audio y definimos el formato
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': audio_format,
                        'preferredquality': '320' if audio_format == 'mp3' else None,
                    },
                    # Luego los metadatos
                    {
                        'key': 'FFmpegMetadata',
                    },
                    # Finalmente la miniatura
                    {
                        'key': 'EmbedThumbnail',
                    },
                ],
                'postprocessor_args': {
                    'FFmpegMetadata': ['-id3v2_version', '3'],
                    'EmbedThumbnail': ['-id3v2_version', '3'],
                },
                'convert_thumbnails': 'jpg',
            })

            # Configuración adicional si se selecciona el formato AIFF
            if audio_format == 'aiff':
                base_opts['postprocessors'][0] = {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'aiff',
                }

        elif format_type == 'video':
            base_opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'merge_output_format': 'mp4',
            })

        return base_opts

    def download_channel(self, url: str, output_path: str, sections: List[str] = None,
                         format_type: str = 'audio', audio_format: str = 'mp3') -> bool:
        """
        Descarga el contenido del canal según las secciones especificadas
        """
        try:
            if not sections:
                return self._download_single_video(url, output_path, format_type, audio_format)

            channel_info = self._get_channel_sections(url)
            channel_name = channel_info['channel_name']
            base_path = Path(output_path) / self._sanitize_filename(channel_name)
            base_path.mkdir(parents=True, exist_ok=True)

            success = True
            for section in sections:
                section_path = base_path / section
                section_path.mkdir(parents=True, exist_ok=True)

                if section == 'playlists':
                    success &= self._download_section(f"{url}/playlists", section_path,
                                                      format_type, audio_format)
                elif section == 'videos':
                    success &= self._download_section(f"{url}/videos", section_path,
                                                      format_type, audio_format)
                elif section == 'releases':
                    success &= self._download_section(f"{url}/releases", section_path,
                                                      format_type, audio_format)

            return success

        except Exception as e:
            self.logger.error(f"Error al descargar el canal: {str(e)}")
            return False

    def _download_single_video(self, url: str, output_path: str,
                               format_type: str, audio_format: str) -> bool:
        """Descarga un solo video o audio"""
        try:
            ydl_opts = self._get_base_options(output_path, format_type, audio_format)

            with YoutubeDL(ydl_opts) as ydl:
                self.logger.info(f"Descargando desde: {url}")
                ydl.download([url])
            return True
        except Exception as e:
            self.logger.error(f"Error al descargar: {str(e)}")
            return False

    def _download_section(self, url: str, output_path: Path,
                          format_type: str, audio_format: str) -> bool:
        """Descarga una sección específica del canal"""