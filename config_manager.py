# config_manager.py
import json
import os
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

CONFIG_FILE = "config.json"


class ConfigManager:
    """Manages the master password hash and verification"""

    def __init__(self):
        self.ph = PasswordHasher()  # Argon2id by default
        self.config_file = CONFIG_FILE

    def is_first_run(self):
        """Check if this is the first time the app runs"""
        return not os.path.exists(self.config_file)

    def create_master_password(self, master_password):
        """Hash and store the master password (first-time setup)"""
        # Hash the password with Argon2id
        password_hash = self.ph.hash(master_password)

        # Save the hash to config.json
        config = {
            "password_hash": password_hash
        }

        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

        return True

    def verify_master_password(self, master_password):
        """Verify the entered password against the stored hash"""
        if not os.path.exists(self.config_file):
            return False

        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)

            # Argon2 verifies the password against the hash
            self.ph.verify(config["password_hash"], master_password)
            return True

        except (VerifyMismatchError, KeyError, json.JSONDecodeError):
            return False

    def rehash_if_needed(self, master_password):
        """Rehash if the Argon2 parameters have changed (optional)"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)

            if self.ph.check_needs_rehash(config["password_hash"]):
                new_hash = self.ph.hash(master_password)
                config["password_hash"] = new_hash
                with open(self.config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                return True
        except Exception:
            pass
        return False

    def change_master_password(self, new_master_password):
        new_hash = self.ph.hash(new_master_password)
        config = {"password_hash": new_hash}

        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

        return True
