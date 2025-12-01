"""
Library Service

Loads, manages, and provides access to component library data.
Handles library caching, validation, search operations, and file watching.
Automatically reloads libraries when JSON files change on disk.
"""

import json
import os
import threading
import time
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from .value_parser import ValueParser


class LibraryService:
    """
    Manages component library data files.
    
    Responsibilities:
    - Load library files from disk
    - Cache library data in memory
    - Search and filter components
    - Validate library structure
    - Provide library statistics
    - Watch for file changes and auto-reload
    - Notify observers when libraries change
    """

    def __init__(self, library_path: str = 'data/libraries'):
        self.library_path = library_path
        self.libraries: Dict[str, Dict[str, Any]] = {}
        self.cache_enabled = True
        
        # File watching
        self.file_watch_enabled = True
        self.watch_thread: Optional[threading.Thread] = None
        self._stop_watching = False
        self.last_file_mtimes: Dict[str, float] = {}
        
        # Change callbacks
        self.on_library_changed: List[Callable[[str], None]] = []
        self.on_libraries_reloaded: List[Callable[[], None]] = []
        
        self._load_all_libraries()
        self._start_file_watcher()

    def register_change_callback(self, callback: Callable[[str], None]) -> None:
        """
        Register callback for library changes.
        Callback receives library name as parameter.
        """
        if callback not in self.on_library_changed:
            self.on_library_changed.append(callback)

    def register_reload_callback(self, callback: Callable[[], None]) -> None:
        """Register callback for when all libraries are reloaded."""
        if callback not in self.on_libraries_reloaded:
            self.on_libraries_reloaded.append(callback)

    def unregister_change_callback(self, callback: Callable[[str], None]) -> None:
        """Unregister library change callback."""
        if callback in self.on_library_changed:
            self.on_library_changed.remove(callback)

    def unregister_reload_callback(self, callback: Callable[[], None]) -> None:
        """Unregister reload callback."""
        if callback in self.on_libraries_reloaded:
            self.on_libraries_reloaded.remove(callback)

    def _notify_library_changed(self, library_name: str) -> None:
        """Notify all observers that a library changed."""
        for callback in self.on_library_changed:
            try:
                callback(library_name)
            except Exception as e:
                print(f"Error in library change callback: {e}")

    def _notify_libraries_reloaded(self) -> None:
        """Notify all observers that libraries were reloaded."""
        for callback in self.on_libraries_reloaded:
            try:
                callback()
            except Exception as e:
                print(f"Error in reload callback: {e}")

    def _start_file_watcher(self) -> None:
        """Start background thread to watch for file changes."""
        if not self.file_watch_enabled:
            return
        
        self.watch_thread = threading.Thread(target=self._watch_library_files, daemon=True)
        self.watch_thread.start()
        print("[OK] Library file watcher started")

    def stop_file_watcher(self) -> None:
        """Stop the file watcher thread."""
        self._stop_watching = True
        if self.watch_thread:
            self.watch_thread.join(timeout=2.0)
        print("[OK] Library file watcher stopped")

    def _watch_library_files(self) -> None:
        """Watch library directory for file changes (runs in background thread)."""
        while not self._stop_watching:
            try:
                if not os.path.exists(self.library_path):
                    time.sleep(1.0)
                    continue
                
                # Check each JSON file
                json_files = [f for f in os.listdir(self.library_path) 
                             if f.endswith('.json') and f != 'library_index.json']
                
                for json_file in json_files:
                    filepath = os.path.join(self.library_path, json_file)
                    
                    try:
                        current_mtime = os.path.getmtime(filepath)
                        previous_mtime = self.last_file_mtimes.get(filepath)
                        
                        if previous_mtime is None:
                            self.last_file_mtimes[filepath] = current_mtime
                        elif current_mtime > previous_mtime:
                            # File has been modified
                            self.last_file_mtimes[filepath] = current_mtime
                            library_name = json_file.replace('.json', '')
                            
                            print(f"↻ Library file changed: {json_file}")
                            if self._load_library_file(library_name, filepath):
                                self._notify_library_changed(library_name)
                    except OSError:
                        # File might have been deleted
                        if filepath in self.last_file_mtimes:
                            del self.last_file_mtimes[filepath]
                
                # Clean up tracking for deleted files
                deleted_files = [f for f in self.last_file_mtimes.keys() 
                                if not os.path.exists(f)]
                for f in deleted_files:
                    del self.last_file_mtimes[f]
                
                # Check every 500ms
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error in file watcher: {e}")
                time.sleep(1.0)

    def _load_all_libraries(self) -> None:
        """Load all library files from directory"""
        if not os.path.exists(self.library_path):
            print(f"Warning: Library path not found: {self.library_path}")
            return
        
        json_files = [f for f in os.listdir(self.library_path) if f.endswith('.json') and f != 'library_index.json']
        for json_file in json_files:
            library_name = json_file.replace('.json', '')
            filepath = os.path.join(self.library_path, json_file)
            self._load_library_file(library_name, filepath)

    def _load_library_file(self, library_name: str, filepath: str) -> bool:
        """Load a single library file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                
            # Validate library structure
            if 'components' not in data:
                print(f"Warning: Invalid library format in {filepath}")
                return False
            
            self.libraries[library_name] = data
            return True
        except Exception as e:
            print(f"Error loading library {filepath}: {e}")
            return False

    def get_library(self, library_name: str) -> Optional[Dict[str, Any]]:
        """Get library data by name"""
        return self.libraries.get(library_name)

    def get_component(self, library_name: str, component_id: str) -> Optional[Dict[str, Any]]:
        """
        Get component from library.
        
        Args:
            library_name: Library name (e.g., 'resistors', 'capacitors')
            component_id: Component ID (e.g., 'r_1k')
            
        Returns:
            Component dictionary or None
        """
        library = self.get_library(library_name)
        if not library:
            return None
        
        for component in library.get('components', []):
            if component.get('id') == component_id:
                return component
        
        return None

    def get_components_by_library(self, library_name: str) -> List[Dict[str, Any]]:
        """Get all components from a library"""
        library = self.get_library(library_name)
        if not library:
            return []
        
        return library.get('components', [])

    def search_components(self, query: str,
                         library_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for components by name or description.
        
        Args:
            query: Search string
            library_name: Optional library to restrict search
            
        Returns:
            List of matching components
        """
        results = []
        query_lower = query.lower()
        
        # Search in specific library or all libraries
        libraries_to_search = {library_name: self.libraries[library_name]} if library_name \
            else self.libraries
        
        for lib_name, library in libraries_to_search.items():
            if library is None:
                continue
            
            for component in library.get('components', []):
                name = component.get('name', '').lower()
                desc = component.get('description', '').lower()
                value = str(component.get('value', '')).lower()
                
                if (query_lower in name or query_lower in desc or
                    query_lower in value):
                    results.append(component)
        
        return results

    def get_component_value(self, library_name: str, component_id: str) -> Optional[str]:
        """Get the default value for a component"""
        component = self.get_component(library_name, component_id)
        if component:
            return component.get('value')
        return None

    def get_component_properties(self, library_name: str,
                                 component_id: str) -> Dict[str, Any]:
        """Get all properties for a component"""
        component = self.get_component(library_name, component_id)
        if component:
            return component.get('properties', {})
        return {}

    def get_component_description(self, library_name: str,
                                 component_id: str) -> str:
        """Get component description"""
        component = self.get_component(library_name, component_id)
        if component:
            return component.get('description', '')
        return ''

    def get_component_instructions(self, library_name: str,
                                  component_id: str) -> str:
        """Get component usage instructions"""
        component = self.get_component(library_name, component_id)
        if component:
            return component.get('instructions', '')
        return ''

    def get_all_libraries(self) -> Dict[str, Dict[str, Any]]:
        """Get all loaded libraries"""
        return dict(self.libraries)

    def get_library_names(self) -> List[str]:
        """Get list of available library names"""
        return list(self.libraries.keys())

    def get_library_stats(self) -> Dict[str, Any]:
        """Get statistics about all libraries"""
        stats = {
            'total_libraries': len(self.libraries),
            'total_components': 0,
            'by_library': {}
        }
        
        for lib_name, library in self.libraries.items():
            if library:
                components = library.get('components', [])
                count = len(components)
                stats['total_components'] += count
                stats['by_library'][lib_name] = count
        
        return stats

    def reload_library(self, library_name: str) -> bool:
        """Reload a library from disk"""
        filepath = os.path.join(self.library_path, f"{library_name}.json")
        return self._load_library_file(library_name, filepath)

    def reload_all_libraries(self) -> None:
        """Reload all libraries"""
        self.libraries.clear()
        self._load_all_libraries()

    def validate_library_structure(self, library_name: str) -> Dict[str, Any]:
        """
        Validate library structure and content.
        
        Returns:
            Dictionary with validation results
        """
        library = self.get_library(library_name)
        if not library:
            return {'valid': False, 'error': 'Library not found'}
        
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'component_count': 0
        }
        
        # Check required fields
        required_fields = ['library', 'version', 'components']
        for field in required_fields:
            if field not in library:
                results['valid'] = False
                results['errors'].append(f"Missing required field: {field}")
        
        # Validate components
        components = library.get('components', [])
        results['component_count'] = len(components)
        
        for i, component in enumerate(components):
            if 'id' not in component:
                results['errors'].append(f"Component {i} missing 'id'")
            if 'name' not in component:
                results['errors'].append(f"Component {i} missing 'name'")
            if 'properties' not in component:
                results['warnings'].append(f"Component {i} missing 'properties'")
        
        return results

    def get_component_by_value_pattern(self, library_name: str,
                                       pattern: str) -> List[Dict[str, Any]]:
        """
        Get components matching a value pattern (e.g., "1k" for resistor "1kΩ").
        
        Args:
            library_name: Library to search
            pattern: Value pattern (e.g., "1k", "100n")
            
        Returns:
            List of matching components
        """
        components = self.get_components_by_library(library_name)
        results = []
        
        try:
            target_value = ValueParser.parse(pattern)
        except:
            return results
        
        for component in components:
            try:
                component_value = ValueParser.parse(str(component.get('value', '')))
                if abs(component_value - target_value) < 1e-9:  # Allow small floating point errors
                    results.append(component)
            except:
                continue
        
        return results

    def export_library(self, library_name: str, filepath: str) -> bool:
        """
        Export library to file.
        
        Args:
            library_name: Library to export
            filepath: Destination file path
            
        Returns:
            True if successful
        """
        library = self.get_library(library_name)
        if not library:
            return False
        
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(library, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting library: {e}")
            return False

    def import_library(self, library_name: str, filepath: str) -> bool:
        """
        Import library from file.
        
        Args:
            library_name: Name for imported library
            filepath: Source file path
            
        Returns:
            True if successful
        """
        return self._load_library_file(library_name, filepath)
