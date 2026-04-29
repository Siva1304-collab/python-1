"""
Greeting Platform - A complete application for sending and managing greetings
Author: Generated
Version: 1.0.0
"""

import datetime
import json
import os
import sys
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import re

# ==================== ENUMS AND CONSTANTS ====================

class GreetingType(Enum):
    """Enum for greeting types"""
    BIRTHDAY = "birthday"
    ANNIVERSARY = "anniversary"
    HOLIDAY = "holiday"
    CONGRATULATIONS = "congratulations"
    SYMPATHY = "sympathy"
    GENERAL = "general"
    
    @classmethod
    def get_display_name(cls, greeting_type):
        """Get display name for greeting type"""
        names = {
            cls.BIRTHDAY: "🎂 Birthday",
            cls.ANNIVERSARY: "💑 Anniversary",
            cls.HOLIDAY: "🎄 Holiday",
            cls.CONGRATULATIONS: "🏆 Congratulations",
            cls.SYMPATHY: "🕊️ Sympathy",
            cls.GENERAL: "💬 General"
        }
        return names.get(greeting_type, "💬 General")
    
    @classmethod
    def get_all(cls):
        """Get all greeting types"""
        return list(cls)

class UserRole(Enum):
    """User roles for permissions"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

# ==================== DATA MODELS ====================

@dataclass
class User:
    """User model"""
    username: str
    email: str
    role: str = "user"
    created_at: str = None
    total_sent: int = 0
    total_received: int = 0
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.datetime.now().isoformat()
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

@dataclass
class Greeting:
    """Greeting model"""
    id: int
    sender: str
    receiver: str
    message: str
    greeting_type: str
    timestamp: str = None
    is_read: bool = False
    is_favorite: bool = False
    tags: List[str] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.datetime.now().isoformat()
        if self.tags is None:
            self.tags = []
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    
    def get_formatted_date(self):
        """Get formatted date string"""
        dt = datetime.datetime.fromisoformat(self.timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    def __str__(self):
        return f"[{self.get_formatted_date()}] {GreetingType.get_display_name(GreetingType(self.greeting_type))} from {self.sender} to {self.receiver}: {self.message[:50]}..."

# ==================== DATABASE MANAGER ====================

class DatabaseManager:
    """Handles all data persistence operations"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, "users.json")
        self.greetings_file = os.path.join(data_dir, "greetings.json")
        self.metadata_file = os.path.join(data_dir, "metadata.json")
        self._ensure_data_directory()
        self._initialize_data_files()
    
    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _initialize_data_files(self):
        """Initialize data files with default structure"""
        if not os.path.exists(self.users_file):
            self._save_json(self.users_file, {})
        
        if not os.path.exists(self.greetings_file):
            self._save_json(self.greetings_file, {})
        
        if not os.path.exists(self.metadata_file):
            self._save_json(self.metadata_file, {
                "next_greeting_id": 1,
                "total_greetings": 0,
                "total_users": 0,
                "created_at": datetime.datetime.now().isoformat()
            })
    
    def _save_json(self, filepath: str, data: dict):
        """Save data to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error saving to {filepath}: {e}")
    
    def _load_json(self, filepath: str) -> dict:
        """Load data from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading from {filepath}: {e}")
            return {}
    
    # User operations
    def save_user(self, user: User) -> bool:
        """Save a user to database"""
        users = self._load_json(self.users_file)
        users[user.username] = user.to_dict()
        self._save_json(self.users_file, users)
        
        # Update metadata
        metadata = self._load_json(self.metadata_file)
        metadata["total_users"] = len(users)
        self._save_json(self.metadata_file, metadata)
        return True
    
    def get_user(self, username: str) -> Optional[User]:
        """Get a user by username"""
        users = self._load_json(self.users_file)
        if username in users:
            return User.from_dict(users[username])
        return None
    
    def get_all_users(self) -> List[User]:
        """Get all users"""
        users = self._load_json(self.users_file)
        return [User.from_dict(data) for data in users.values()]
    
    def user_exists(self, username: str) -> bool:
        """Check if user exists"""
        users = self._load_json(self.users_file)
        return username in users
    
    # Greeting operations
    def save_greeting(self, greeting: Greeting) -> bool:
        """Save a greeting to database"""
        greetings = self._load_json(self.greetings_file)
        greetings[str(greeting.id)] = greeting.to_dict()
        self._save_json(self.greetings_file, greetings)
        
        # Update metadata
        metadata = self._load_json(self.metadata_file)
        metadata["total_greetings"] = len(greetings)
        metadata["next_greeting_id"] = max(metadata.get("next_greeting_id", 1), greeting.id + 1)
        self._save_json(self.metadata_file, metadata)
        return True
    
    def get_greeting(self, greeting_id: int) -> Optional[Greeting]:
        """Get a greeting by ID"""
        greetings = self._load_json(self.greetings_file)
        if str(greeting_id) in greetings:
            return Greeting.from_dict(greetings[str(greeting_id)])
        return None
    
    def get_all_greetings(self) -> List[Greeting]:
        """Get all greetings"""
        greetings = self._load_json(self.greetings_file)
        return [Greeting.from_dict(data) for data in greetings.values()]
    
    def delete_greeting(self, greeting_id: int) -> bool:
        """Delete a greeting by ID"""
        greetings = self._load_json(self.greetings_file)
        if str(greeting_id) in greetings:
            del greetings[str(greeting_id)]
            self._save_json(self.greetings_file, greetings)
            
            # Update metadata
            metadata = self._load_json(self.metadata_file)
            metadata["total_greetings"] = len(greetings)
            self._save_json(self.metadata_file, metadata)
            return True
        return False
    
    def update_greeting(self, greeting: Greeting) -> bool:
        """Update an existing greeting"""
        return self.save_greeting(greeting)
    
    def get_next_id(self) -> int:
        """Get next available greeting ID"""
        metadata = self._load_json(self.metadata_file)
        return metadata.get("next_greeting_id", 1)

# ==================== GREETING PLATFORM ====================

class GreetingPlatform:
    """Main platform class handling all business logic"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.current_user: Optional[User] = None
    
    def register_user(self, username: str, email: str, role: str = "user") -> Tuple[bool, str]:
        """Register a new user"""
        # Validation
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            return False, "Username can only contain letters, numbers, and underscores"
        
        if not email or "@" not in email:
            return False, "Invalid email address"
        
        if self.db.user_exists(username):
            return False, f"Username '{username}' already exists"
        
        # Create user
        user = User(username=username, email=email, role=role)
        if self.db.save_user(user):
            return True, f"User '{username}' registered successfully!"
        return False, "Failed to register user"
    
    def login(self, username: str) -> Tuple[bool, str]:
        """Login user"""
        user = self.db.get_user(username)
        if user:
            self.current_user = user
            return True, f"Welcome back, {username}! 👋"
        return False, f"User '{username}' not found. Please register first."
    
    def logout(self):
        """Logout current user"""
        self.current_user = None
        print("✅ Logged out successfully!")
    
    def send_greeting(self, receiver: str, message: str, greeting_type: str) -> Tuple[bool, str, Optional[int]]:
        """Send a greeting to another user"""
        if not self.current_user:
            return False, "Please login first", None
        
        # Validate receiver
        if not self.db.user_exists(receiver):
            return False, f"User '{receiver}' not found", None
        
        if receiver == self.current_user.username:
            return False, "You cannot send a greeting to yourself", None
        
        # Validate message
        if not message or len(message) < 5:
            return False, "Message must be at least 5 characters", None
        
        if len(message) > 500:
            return False, "Message is too long (max 500 characters)", None
        
        # Create and save greeting
        greeting_id = self.db.get_next_id()
        greeting = Greeting(
            id=greeting_id,
            sender=self.current_user.username,
            receiver=receiver,
            message=message,
            greeting_type=greeting_type
        )
        
        if self.db.save_greeting(greeting):
            # Update user statistics
            sender_user = self.db.get_user(self.current_user.username)
            sender_user.total_sent += 1
            self.db.save_user(sender_user)
            
            receiver_user = self.db.get_user(receiver)
            receiver_user.total_received += 1
            self.db.save_user(receiver_user)
            
            return True, f"✅ Greeting sent successfully! (ID: {greeting_id})", greeting_id
        
        return False, "Failed to send greeting", None
    
    def get_my_greetings(self, as_sender: bool = True) -> List[Greeting]:
        """Get greetings for current user"""
        if not self.current_user:
            return []
        
        all_greetings = self.db.get_all_greetings()
        if as_sender:
            return [g for g in all_greetings if g.sender == self.current_user.username]
        else:
            return [g for g in all_greetings if g.receiver == self.current_user.username]
    
    def search_greetings(self, keyword: str) -> List[Greeting]:
        """Search greetings by keyword"""
        if not self.current_user:
            return []
        
        all_greetings = self.db.get_all_greetings()
        keyword_lower = keyword.lower()
        
        return [
            g for g in all_greetings 
            if (g.sender == self.current_user.username or g.receiver == self.current_user.username)
            and (keyword_lower in g.message.lower() or 
                 keyword_lower in g.sender.lower() or 
                 keyword_lower in g.receiver.lower())
        ]
    
    def mark_as_read(self, greeting_id: int) -> bool:
        """Mark a greeting as read"""
        greeting = self.db.get_greeting(greeting_id)
        if greeting and greeting.receiver == self.current_user.username:
            greeting.is_read = True
            return self.db.update_greeting(greeting)
        return False
    
    def toggle_favorite(self, greeting_id: int) -> bool:
        """Toggle favorite status of a greeting"""
        greeting = self.db.get_greeting(greeting_id)
        if greeting and (greeting.sender == self.current_user.username or 
                        greeting.receiver == self.current_user.username):
            greeting.is_favorite = not greeting.is_favorite
            return self.db.update_greeting(greeting)
        return False
    
    def delete_my_greeting(self, greeting_id: int) -> bool:
        """Delete a greeting (only if user is sender)"""
        greeting = self.db.get_greeting(greeting_id)
        if greeting and greeting.sender == self.current_user.username:
            return self.db.delete_greeting(greeting_id)
        return False
    
    def get_statistics(self) -> dict:
        """Get platform statistics"""
        all_greetings = self.db.get_all_greetings()
        all_users = self.db.get_all_users()
        
        # Count by type
        type_counts = {}
        for greeting in all_greetings:
            type_counts[greeting.greeting_type] = type_counts.get(greeting.greeting_type, 0) + 1
        
        # Count by user
        user_stats = {}
        for user in all_users:
            sent = len([g for g in all_greetings if g.sender == user.username])
            received = len([g for g in all_greetings if g.receiver == user.username])
            user_stats[user.username] = {"sent": sent, "received": received}
        
        return {
            "total_greetings": len(all_greetings),
            "total_users": len(all_users),
            "greetings_by_type": type_counts,
            "user_statistics": user_stats
        }
    
    def get_unread_count(self) -> int:
        """Get count of unread greetings for current user"""
        if not self.current_user:
            return 0
        
        received = self.get_my_greetings(as_sender=False)
        return len([g for g in received if not g.is_read])

# ==================== UI HELPER FUNCTIONS ====================

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_success(message: str):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message: str):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message: str):
    """Print info message"""
    print(f"ℹ️ {message}")

def print_warning(message: str):
    """Print warning message"""
    print(f"⚠️ {message}")

def get_input(prompt: str, required: bool = True) -> str:
    """Get user input with validation"""
    while True:
        value = input(prompt).strip()
        if not required and not value:
            return value
        if value:
            return value
        print_error("Input cannot be empty. Please try again.")

def get_choice(options: Dict[str, str], prompt: str = "Select option: ") -> str:
    """Get validated choice from options"""
    while True:
        choice = input(prompt).strip()
        if choice in options:
            return choice
        print_error(f"Invalid choice. Please select from: {', '.join(options.keys())}")

# ==================== MAIN APPLICATION ====================

class GreetingApp:
    """Main application class"""
    
    def __init__(self):
        self.platform = GreetingPlatform()
    
    def run(self):
        """Run the main application loop"""
        while True:
            if not self.platform.current_user:
                self.show_auth_menu()
            else:
                self.show_main_menu()
    
    def show_auth_menu(self):
        """Show authentication menu"""
        clear_screen()
        print_header("🎉 GREETING PLATFORM 🎉")
        print("\n1. 🔐 Login")
        print("2. 📝 Register")
        print("3. 🚪 Exit")
        
        choice = get_choice({"1": "login", "2": "register", "3": "exit"}, "\nYour choice: ")
        
        if choice == "1":
            self.login()
        elif choice == "2":
            self.register()
        elif choice == "3":
            print_success("Thank you for using Greeting Platform! Goodbye! 👋")
            sys.exit(0)
    
    def login(self):
        """Handle user login"""
        clear_screen()
        print_header("🔐 LOGIN")
        
        username = get_input("Username: ")
        success, message = self.platform.login(username)
        
        if success:
            print_success(message)
            input("\nPress Enter to continue...")
        else:
            print_error(message)
            input("\nPress Enter to try again...")
    
    def register(self):
        """Handle user registration"""
        clear_screen()
        print_header("📝 REGISTER NEW USER")
        
        username = get_input("Username (min 3 chars, letters/numbers/_): ")
        email = get_input("Email address: ")
        
        success, message = self.platform.register_user(username, email)
        
        if success:
            print_success(message)
            input("\nPress Enter to login...")
            self.platform.login(username)
        else:
            print_error(message)
            input("\nPress Enter to try again...")
    
    def show_main_menu(self):
        """Show main menu for logged-in users"""
        clear_screen()
        
        # Show unread count
        unread = self.platform.get_unread_count()
        unread_msg = f" ({unread} unread)" if unread > 0 else ""
        
        print_header(f"🎉 WELCOME, {self.platform.current_user.username.upper()}!{unread_msg} 🎉")
        print("\n1. 📝 Send Greeting")
        print("2. 📬 My Greetings")
        print("3. ⭐ Favorites")
        print("4. 🔍 Search Greetings")
        print("5. 📊 Statistics")
        print("6. 👤 My Profile")
        print("7. 🚪 Logout")
        
        choice = get_choice(
            {"1": "send", "2": "view", "3": "favorites", "4": "search", "5": "stats", "6": "profile", "7": "logout"},
            "\nYour choice: "
        )
        
        if choice == "1":
            self.send_greeting()
        elif choice == "2":
            self.view_greetings()
        elif choice == "3":
            self.view_favorites()
        elif choice == "4":
            self.search_greetings()
        elif choice == "5":
            self.show_statistics()
        elif choice == "6":
            self.show_profile()
        elif choice == "7":
            self.platform.logout()
            input("\nPress Enter to continue...")
    
    def send_greeting(self):
        """Handle sending a greeting"""
        clear_screen()
        print_header("📝 SEND A GREETING")
        
        # Show greeting types
        print("\n✨ GREETING TYPES:")
        greeting_types = list(GreetingType)
        for i, gtype in enumerate(greeting_types, 1):
            print(f"  {i}. {GreetingType.get_display_name(gtype)}")
        
        type_choice = get_input("\nSelect type (1-6): ")
        try:
            gtype = greeting_types[int(type_choice) - 1]
            greeting_type = gtype.value
        except:
            greeting_type = "general"
        
        receiver = get_input("\nReceiver's username: ")
        print(f"\n💬 Write your {GreetingType.get_display_name(GreetingType(greeting_type))} message:")
        message = get_input("Message (min 5 chars): ")
        
        success, message_result, greeting_id = self.platform.send_greeting(receiver, message, greeting_type)
        
        if success:
            print_success(message_result)
        else:
            print_error(message_result)
        
        input("\nPress Enter to continue...")
    
    def view_greetings(self):
        """View user's greetings"""
        clear_screen()
        print_header("📬 MY GREETINGS")
        
        print("\n1. 📤 Sent Greetings")
        print("2. 📥 Received Greetings")
        
        choice = get_choice({"1": "sent", "2": "received"}, "\nView: ")
        
        if choice == "1":
            greetings = self.platform.get_my_greetings(as_sender=True)
            title = "SENT GREETINGS"
        else:
            greetings = self.platform.get_my_greetings(as_sender=False)
            title = "RECEIVED GREETINGS"
        
        if not greetings:
            print_info(f"\nNo {title.lower()} found.")
        else:
            print(f"\n📌 {title} ({len(greetings)}):")
            print("-" * 60)
            for g in greetings:
                status = "⭐ " if g.is_favorite else "   "
                read_status = "✓" if g.is_read else "●"
                print(f"{status}[{g.get_formatted_date()}] [{read_status}] ID:{g.id}")
                print(f"   {'To' if choice=='1' else 'From'}: {g.receiver if choice=='1' else g.sender}")
                print(f"   Type: {GreetingType.get_display_name(GreetingType(g.greeting_type))}")
                print(f"   Message: {g.message}")
                print("-" * 60)
            
            # Actions for received greetings
            if choice == "2":
                action = get_input("\nEnter greeting ID to mark as read/favorite (or press Enter to continue): ", required=False)
                if action and action.isdigit():
                    gid = int(action)
                    self.platform.mark_as_read(gid)
                    fav = get_input("Mark as favorite? (y/n): ", required=False).lower()
                    if fav == 'y':
                        self.platform.toggle_favorite(gid)
                    print_success("Updated!")
        
        input("\nPress Enter to continue...")
    
    def view_favorites(self):
        """View favorite greetings"""
        clear_screen()
        print_header("⭐ FAVORITE GREETINGS")
        
        all_greetings = self.platform.db.get_all_greetings()
        favorites = [
            g for g in all_greetings 
            if g.is_favorite and (g.sender == self.platform.current_user.username or 
                                  g.receiver == self.platform.current_user.username)
        ]
        
        if not favorites:
            print_info("\nNo favorite greetings yet. Star some greetings to see them here!")
        else:
            print(f"\n📌 FAVORITES ({len(favorites)}):")
            print("-" * 60)
            for g in favorites:
                role = "To" if g.sender == self.platform.current_user.username else "From"
                other = g.receiver if g.sender == self.platform.current_user.username else g.sender
                print(f"[{g.get_formatted_date()}] ID:{g.id}")
                print(f"   {role}: {other}")
                print(f"   Type: {GreetingType.get_display_name(GreetingType(g.greeting_type))}")
                print(f"   Message: {g.message}")
                print("-" * 60)
        
        input("\nPress Enter to continue...")
    
    def search_greetings(self):
        """Search through greetings"""
        clear_screen()
        print_header("🔍 SEARCH GREETINGS")
        
        keyword = get_input("Enter search keyword: ")
        results = self.platform.search_greetings(keyword)
        
        if not results:
            print_info(f"\nNo greetings found matching '{keyword}'")
        else:
            print(f"\n📌 SEARCH RESULTS ({len(results)}):")
            print("-" * 60)
            for g in results:
                role = "To" if g.sender == self.platform.current_user.username else "From"
                other = g.receiver if g.sender == self.platform.current_user.username else g.sender
                print(f"[{g.get_formatted_date()}] {role}: {other}")
                print(f"   {g.message[:100]}")
                print("-" * 60)
        
        input("\nPress Enter to continue...")
    
    def show_statistics(self):
        """Show platform statistics"""
        clear_screen()
        print_header("📊 PLATFORM STATISTICS")
        
        stats = self.platform.get_statistics()
        
        print(f"\n📈 OVERVIEW:")
        print(f"   Total Greetings: {stats['total_greetings']}")
        print(f"   Total Users: {stats['total_users']}")
        
        if stats['greetings_by_type']:
            print(f"\n📊 BY TYPE:")
            for gtype, count in stats['greetings_by_type'].items():
                display_name = GreetingType.get_display_name(GreetingType(gtype))
                print(f"   {display_name}: {count}")
        
        if stats['user_statistics']:
            print(f"\n👥 USER ACTIVITY:")
            for user, data in stats['user_statistics'].items():
                print(f"   {user}: Sent {data['sent']} | Received {data['received']}")
        
        input("\nPress Enter to continue...")
    
    def show_profile(self):
        """Show user profile"""
        clear_screen()
        print_header("👤 MY PROFILE")
        
        user = self.platform.current_user
        
        print(f"\n📋 USER INFORMATION:")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Role: {user.role}")
        print(f"   Joined: {user.created_at[:10]}")
        print(f"   Greetings Sent: {user.total_sent}")
        print(f"   Greetings Received: {user.total_received}")
        
        input("\nPress Enter to continue...")

# ==================== ENTRY POINT ====================

if __name__ == "__main__":
    try:
        app = GreetingApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print_error(f"An unexpected error occurred: {e}")
        sys.exit(1)
