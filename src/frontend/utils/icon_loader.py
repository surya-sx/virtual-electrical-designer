"""
Icon loader utility for loading SVG icons from assets directory
"""
from pathlib import Path
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import QSize
import logging

logger = logging.getLogger(__name__)

# Get assets directory path
ASSETS_DIR = Path(__file__).parent.parent.parent.parent / "assets"
ICONS_DIR = ASSETS_DIR / "icons"


class IconLoader:
    """Loads and caches SVG icons from the assets directory"""
    
    _cache = {}
    
    @classmethod
    def get_icon(cls, icon_name: str, size: int = 24, color: str = None) -> QIcon:
        """
        Load an SVG icon as QIcon
        
        Args:
            icon_name: Name of the icon file without extension (e.g., 'library')
            size: Size of the icon in pixels
            color: Optional color string (not used for SVG, kept for compatibility)
        
        Returns:
            QIcon object
        """
        cache_key = f"{icon_name}_{size}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]
        
        svg_path = ICONS_DIR / f"{icon_name}.svg"
        
        if not svg_path.exists():
            logger.warning(f"Icon not found: {svg_path}")
            return QIcon()
        
        try:
            # Load SVG and render to pixmap
            renderer = QSvgRenderer(str(svg_path))
            pixmap = QPixmap(size, size)
            pixmap.fill(False)  # Transparent background
            
            from PySide6.QtGui import QPainter
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            
            icon = QIcon(pixmap)
            cls._cache[cache_key] = icon
            return icon
        
        except Exception as e:
            logger.error(f"Error loading icon {icon_name}: {e}")
            return QIcon()
    
    @classmethod
    def get_pixmap(cls, icon_name: str, size: int = 24) -> QPixmap:
        """
        Load an SVG icon as QPixmap
        
        Args:
            icon_name: Name of the icon file without extension
            size: Size of the pixmap in pixels
        
        Returns:
            QPixmap object
        """
        svg_path = ICONS_DIR / f"{icon_name}.svg"
        
        if not svg_path.exists():
            logger.warning(f"Icon not found: {svg_path}")
            return QPixmap()
        
        try:
            renderer = QSvgRenderer(str(svg_path))
            pixmap = QPixmap(size, size)
            pixmap.fill(False)  # Transparent background
            
            from PySide6.QtGui import QPainter
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            
            return pixmap
        
        except Exception as e:
            logger.error(f"Error loading pixmap {icon_name}: {e}")
            return QPixmap()
    
    @classmethod
    def clear_cache(cls):
        """Clear the icon cache"""
        cls._cache.clear()


# Convenience functions
def get_icon(icon_name: str, size: int = 24) -> QIcon:
    """Get an icon by name"""
    return IconLoader.get_icon(icon_name, size)


def get_pixmap(icon_name: str, size: int = 24) -> QPixmap:
    """Get a pixmap by name"""
    return IconLoader.get_pixmap(icon_name, size)
