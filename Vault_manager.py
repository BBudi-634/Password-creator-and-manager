import json
import os
import base64
from datetime import datetime
from encrypter import PasswordEncryptor


class VaultManager:
    def __init__(self, master_password, filename="vault.json"):
        self.master_password = master_password
        self.filename = filename
        self.vault = self.load_vault()

    def load_vault(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("⚠️ Vault file corrupted. Starting fresh.")
                return {}
        return {}

    def save_vault(self):
        with open(self.filename, 'w') as f:
            json.dump(self.vault, f, indent=2)

    def add_password(self, service, username, password, url=None, notes=None):
        # 1. Encrypt the password
        encryptor = PasswordEncryptor(self.master_password)
        encrypted_password = encryptor.encrypt(password)
        salt = encryptor.get_salt()

        # 2. Structure for JSON
        entry = {
            'username': username,
            'password': encrypted_password,  # ← Encrypted!
            'salt': base64.b64encode(salt).decode(),  # ← Base64 encoded!
            'created': datetime.now().isoformat(),
        }

        if url:
            entry['url'] = url
        if notes:
            # Optional: encrypt notes too
            entry['notes'] = encryptor.encrypt(notes)

        # 3. Save to vault
        self.vault[service] = entry
        self.save_vault()
        print(f"✅ Password for '{service}' saved securely!")
        return True

    def get_password(self, service):
        if service not in self.vault:
            print(f"❌ No password found for '{service}'")
            return None

        entry = self.vault[service]

        # Get encrypted data
        encrypted_password = entry['password']
        salt = base64.b64decode(entry['salt'])

        # Decrypt
        encryptor = PasswordEncryptor(self.master_password, salt)
        decrypted_password = encryptor.decrypt(encrypted_password)

        return decrypted_password

    def get_entry(self, service):
        if service not in self.vault:
            return None

        entry = self.vault[service].copy()
        entry['password'] = self.get_password(service)
        return entry

    def list_services(self):
        if not self.vault:
            print("📭 No passwords stored yet.")
            return []

        print(f"📋 {len(self.vault)} services stored:")
        for service in sorted(self.vault.keys()):
            created = self.vault[service].get('created', 'Unknown')
            print(f"  - {service} (created: {created})")
        return list(self.vault.keys())

    def delete_service(self, service):
        """Delete a service from the vault"""
        if service not in self.vault:
            print(f"❌ No service found for '{service}'")
            return False

        del self.vault[service]
        self.save_vault()
        print(f"🗑️ Deleted '{service}' from vault")
        return True

    def re_encrypt_all(self, old_password, new_password):
        """
        Re-encrypt every entry in the vault with a new master password.
        Reads with old, encrypts with new, saves.
        """
        # 1. Create encryptors for old and new passwords
        from encrypter import PasswordEncryptor
        import base64

        # 2. Decrypt every entry with the OLD password
        decrypted_entries = {}
        for service, entry in self.vault.items():
            # Decrypt password
            old_salt = base64.b64decode(entry['salt'])
            old_encryptor = PasswordEncryptor(old_password, old_salt)
            plain_password = old_encryptor.decrypt(entry['password'])

            # Decrypt notes if present
            plain_notes = None
            if entry.get('notes'):
                plain_notes = old_encryptor.decrypt(entry['notes'])

            decrypted_entries[service] = {
                'username': entry['username'],
                'password': plain_password,
                'notes': plain_notes,
                'url': entry.get('url'),
                'created': entry.get('created')
            }

        # 3. Re-encrypt with the NEW password
        new_vault = {}
        for service, data in decrypted_entries.items():
            new_encryptor = PasswordEncryptor(new_password)

            new_entry = {
                'username': data['username'],
                'password': new_encryptor.encrypt(data['password']),
                'salt': base64.b64encode(new_encryptor.get_salt()).decode(),
                'created': data['created']
            }

            if data['url']:
                new_entry['url'] = data['url']
            if data['notes']:
                new_entry['notes'] = new_encryptor.encrypt(data['notes'])

            new_vault[service] = new_entry

        # 4. Replace the vault
        self.vault = new_vault
        self.master_password = new_password
        self.save_vault()

        # 5. Clear plaintext from memory
        del decrypted_entries

