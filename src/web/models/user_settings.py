"""
Defines the UserSettings model for the web interface of the JSON to Excel Conversion Tool.
This class manages user preferences and settings that persist across conversion sessions,
providing a way to customize the application behavior for individual users.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Any, List
import json
import uuid

from ..config.web_interface_config import ui
from .conversion_options import ConversionOptions


@dataclass(init=False)
class UserSettings:
    """
    A data class that represents user settings and preferences for the web interface,
    including theme preferences and default conversion options.
    """
    user_id: str
    theme: str
    show_help_links: bool
    default_conversion_options: ConversionOptions
    ui_preferences: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    def __init__(
        self,
        user_id: Optional[str] = None,
        theme: Optional[str] = None,
        show_help_links: Optional[bool] = None,
        default_conversion_options: Optional[ConversionOptions] = None,
        ui_preferences: Optional[Dict[str, Any]] = None
    ):
        """
        Initializes a new UserSettings instance with the provided settings or defaults.
        
        Args:
            user_id: Unique identifier for the user
            theme: User interface theme preference
            show_help_links: Whether to show help links in the UI
            default_conversion_options: Default conversion options for this user
            ui_preferences: Additional UI preferences
        """
        # Set user_id or generate a new one
        self.user_id = user_id or str(uuid.uuid4())
        
        # Set theme from provided value or default
        self.theme = theme or ui.get("theme", "default")
        
        # Set show_help_links from provided value or default
        self.show_help_links = show_help_links if show_help_links is not None else ui.get("show_help_links", True)
        
        # Set default_conversion_options from provided value or create default
        if default_conversion_options:
            self.default_conversion_options = default_conversion_options
        else:
            # Create default conversion options based on web_interface_config
            default_options = ui.get("default_options", {})
            self.default_conversion_options = ConversionOptions(
                sheet_name=default_options.get("sheet_name", "Sheet1"),
                array_handling=default_options.get("array_handling", "expand")
            )
        
        # Set ui_preferences or use empty dict
        self.ui_preferences = ui_preferences or {}
        
        # Set timestamps
        now = datetime.now()
        self.created_at = now
        self.updated_at = now
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the user settings to a dictionary representation.
        
        Returns:
            Dictionary representation of the user settings
        """
        return {
            "user_id": self.user_id,
            "theme": self.theme,
            "show_help_links": self.show_help_links,
            "default_conversion_options": self.default_conversion_options.to_dict(),
            "ui_preferences": self.ui_preferences,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSettings':
        """
        Creates a UserSettings instance from a dictionary representation.
        
        Args:
            data: Dictionary containing user settings data
            
        Returns:
            A new UserSettings instance
        """
        # Extract basic settings
        user_id = data.get("user_id")
        theme = data.get("theme")
        show_help_links = data.get("show_help_links")
        
        # Create ConversionOptions from the dictionary
        conversion_options_dict = data.get("default_conversion_options", {})
        default_conversion_options = ConversionOptions.from_dict(conversion_options_dict)
        
        # Extract UI preferences
        ui_preferences = data.get("ui_preferences", {})
        
        # Create the UserSettings instance
        user_settings = cls(
            user_id=user_id,
            theme=theme,
            show_help_links=show_help_links,
            default_conversion_options=default_conversion_options,
            ui_preferences=ui_preferences
        )
        
        # Set timestamps if provided
        if "created_at" in data:
            user_settings.created_at = datetime.fromisoformat(data["created_at"])
        
        if "updated_at" in data:
            user_settings.updated_at = datetime.fromisoformat(data["updated_at"])
        
        return user_settings
    
    def to_json(self) -> str:
        """
        Converts the user settings to a JSON string.
        
        Returns:
            JSON string representation of the user settings
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'UserSettings':
        """
        Creates a UserSettings instance from a JSON string.
        
        Args:
            json_str: JSON string representation of user settings
            
        Returns:
            A new UserSettings instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def update_preferences(self, preferences: Dict[str, Any]) -> None:
        """
        Updates specific UI preferences while preserving others.
        
        Args:
            preferences: Dictionary of UI preferences to update
        """
        self.ui_preferences.update(preferences)
        self.updated_at = datetime.now()
    
    def update_conversion_options(self, options: ConversionOptions) -> None:
        """
        Updates the default conversion options.
        
        Args:
            options: New conversion options
        """
        self.default_conversion_options = options
        self.updated_at = datetime.now()
    
    def update_theme(self, theme: str) -> None:
        """
        Updates the user interface theme preference.
        
        Args:
            theme: New theme name
        """
        self.theme = theme
        self.updated_at = datetime.now()
    
    def reset_to_defaults(self) -> None:
        """
        Resets all settings to application defaults.
        """
        # Reset theme and help links to default
        self.theme = ui.get("theme", "default")
        self.show_help_links = ui.get("show_help_links", True)
        
        # Reset conversion options to default
        default_options = ui.get("default_options", {})
        self.default_conversion_options = ConversionOptions(
            sheet_name=default_options.get("sheet_name", "Sheet1"),
            array_handling=default_options.get("array_handling", "expand")
        )
        
        # Clear all UI preferences
        self.ui_preferences = {}
        
        # Update timestamp
        self.updated_at = datetime.now()
    
    def get_preference(self, key: str, default_value: Any = None) -> Any:
        """
        Gets a specific UI preference with an optional default value.
        
        Args:
            key: The preference key to retrieve
            default_value: Value to return if key is not found
            
        Returns:
            The preference value or default if not found
        """
        return self.ui_preferences.get(key, default_value)
    
    def save_to_file(self, file_path: Optional[str] = None) -> bool:
        """
        Saves the user settings to a file.
        
        Args:
            file_path: Path where to save the settings file, or None to use default
            
        Returns:
            True if successful, False otherwise
        """
        # Generate default file path if none provided
        if file_path is None:
            file_path = f"user_settings_{self.user_id}.json"
        
        try:
            # Convert to JSON and write to file
            with open(file_path, 'w') as file:
                file.write(self.to_json())
            return True
        except Exception as e:
            # Log error and return False
            print(f"Error saving settings to file: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'UserSettings':
        """
        Loads user settings from a file.
        
        Args:
            file_path: Path to the settings file
            
        Returns:
            A UserSettings instance loaded from the file
            
        Raises:
            FileNotFoundError: If the settings file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        try:
            with open(file_path, 'r') as file:
                json_str = file.read()
            
            return cls.from_json(json_str)
        except FileNotFoundError:
            raise
        except json.JSONDecodeError:
            raise
        except Exception as e:
            raise Exception(f"Error loading settings from file: {e}")