# 🔐 Password Creator & Manager

A secure, desktop-based password manager built with Python, CustomTkinter, and modern cryptography. It generates strong passwords and passphrases, encrypts them with industry-standard algorithms, and stores them in a local vault — all behind a single Argon2id-hashed master password.

# 📸 Screenshots

![img.png](img.png)
![img_1.png](img_1.png)
![img_2.png](img_2.png)

# ✨ Features

### 🔑 Password & Passphrase Generation
- Generate random passwords with configurable:
  - Length (5–24 characters)
  - Uppercase letters
  - Digits
  - Symbols
- Generate memorable passphrases using `wordfreq` (3–6 words)
- Cryptographically secure randomness via Python's `secrets` module

### 🛡️ Secure Vault Storage
- Every password is encrypted individually with **Fernet** (AES-128-CBC + HMAC)
- Each entry has its own **salt** and key derivation via **PBKDF2HMAC** (100,000 iterations)
- Encrypted vault stored in a local `vault.json` file
- No plaintext passwords ever touch the disk

### 🔐 Master Password Protection
- Master password hashed with **Argon2id** — the winner of the Password Hashing Competition
- Memory-hard and GPU-resistant
- First-time setup flow for new users, login flow for returning users
- Master password is **never stored** — only its Argon2id hash

### 📋 Full Vault Management
- View all saved services in a scrollable list
- Search and filter by service name
- View entry details in a modal popup
- Copy passwords to clipboard with one click
- Edit usernames, URLs, and notes
- Delete entries with confirmation
- Optional notes and URL fields per entry

### 🎨 Modern UI
- Dark theme with custom color palette
- Rounded overlay cards for readability
- Consistent emoji iconography
- Responsive layout across 1600×800 window

---

## 🔒 Security Architecture

This project takes a defense-in-depth approach by having different layers of security.

### Layer 1 — Master Password Hashing (Argon2id)
- Why this is safe: Uses Argon2id to hash the password. Cannot be reversed, memory-hard to slow down GPU brute force.
- The hash for the Master password stored in config.json. 
- Verifies the user.


### Layer 2 - Vault Encryption (Fernet + PBKDF2)
- Why this is safe: to get a decrypted password, the master password as well as its unique salt is required even if the vault.json is stolen.
- (hashed master password + salt) is passed through PBKDF2 to derive the Fernet encryption key.
- PBKDF2 has 100,000 iterations
- encrypted passwords are stored in the vault.json

### What is encrypted?
- Master password | ❌ Not stored | Only its argon2id hash is stored
- Stored password | ✅ Encrypted with Fernet | sensitive and expected to be retrieved 
- Notes | ✅ Encrypted with Fernet | May contain sensitive info
- Usernames | ❌ plain text | Needed for the search function without decryption
- Service names | ❌ plain text | Used for JSON keys
- URLs | ❌ plain | public knowledge

# 🧠 Threat Model

### ✅ Protects Against
- **Server-side data breaches** — nothing sensitive is stored in plaintext
- **Rainbow table attacks** — every hash is salted
- **GPU brute-force** — Argon2id is memory-hard
- **Credential reuse** — each service has a unique password
- **Theft of `vault.json`** — encrypted with the master password
- **Theft of `config.json`** — contains only a one-way Argon2id hash

### ⚠️ Does Not Protect Against
- **Keyloggers** — if the OS is compromised, nothing helps
- **Screen capture / shoulder surfing** — physical security is the user's responsibility
- **Weak master passwords** — cryptography can't fix a user choosing `"password123"`
- **Malware with memory access** — a running process can be inspected
- **Lost master password** — there is no recovery by design

---

# 🛡️ Reliability
- Atomic file writes prevent vault corruption if the app crashes mid-save
- Writes to a temporary file, then atomically renames it into place

---

# 🏗️ Project Structure

1. main.py = Entry point + all UI elements (frontend)
2. generator.py = Password and passphrase generation
3. encrypter.py = Fernet encryption/decryption
4. vault_manager.py = logic for CRUD UI (saving, loading, editing, deleting)
5. config_manager.py = master password hashing and verification