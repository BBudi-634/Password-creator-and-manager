import ttkbootstrap as ttk
import customtkinter as ctk
from generator import generate_password
from generator import generate_passphrase
from Vault_manager import VaultManager
from config_manager import ConfigManager
from PIL import Image
import os
import json


# ============================================
# GLOBAL VARIABLES
# ============================================
vault = None  # Initialized after master password verification
window = None
config = ConfigManager()  # Argon2 hashing/verification

def clear_window(self): # destroys page.
    for widget in self.winfo_children():
        widget.destroy()

# ============================================
# WINDOW SETUP
# ============================================
def setup_window():
    """Create and configure the main application window"""
    global window
    window = ctk.CTk()
    window.title("Password Creator & Manager")
    window.geometry("1600x800")
    window.configure(fg_color="#0D1424")
    ctk.set_default_color_theme("blue")


# ============================================
# ATOMIC SAVE
# ============================================
def atomic_save(self, filename, data):
    """Write to a temp file, then atomically rename it."""
    temp_file = filename + ".tmp"
    with open(temp_file, 'w') as f:
        json.dump(data, f, indent=2)
    os.replace(temp_file, filename)  # Atomic on POSIX and Windows

# ============================================
# FIRST-TIME SETUP SCREEN
# ============================================
def show_setup_screen():
    """Show setup screen for first-time users"""
    global vault

    def create_password():
        global vault
        password = entry_string.get()
        confirm = confirm_string.get()

        # Validation
        if not password:
            output_string.set("❌ Please enter a password!")
            return

        if len(password) < 8:
            output_string.set("❌ Password must be at least 8 characters!")
            return

        if password != confirm:
            output_string.set("❌ Passwords do not match!")
            return

        # Save the Argon2 hash
        config.create_master_password(password)

        # Initialize vault with the password
        vault = VaultManager(password, "vault.json")

        # Go to main menu
        clear_window(window)
        show_main_menu()

    # Center frame
    main_frame = ctk.CTkFrame(window, fg_color="transparent")
    main_frame.place(relx=0.5, rely=0.5, anchor="center")

    # Title
    ctk.CTkLabel(
        main_frame,
        text="🔐 Welcome!",
        font=ctk.CTkFont(size=40, weight="bold")
    ).pack(pady=(0, 10))

    ctk.CTkLabel(
        main_frame,
        text="Create a master password to secure your vault",
        font=ctk.CTkFont(size=16),
        text_color="gray"
    ).pack(pady=(0, 30))

    # Password entry
    ctk.CTkLabel(main_frame, text="Master Password:").pack()
    entry_string = ctk.StringVar()
    entry = ctk.CTkEntry(
        main_frame,
        textvariable=entry_string,
        placeholder_text="Enter master password...",
        show="*",
        width=350,
        height=45,
        font=ctk.CTkFont(size=16)
    )
    entry.pack(pady=10)

    # Confirm password
    ctk.CTkLabel(main_frame, text="Confirm Password:").pack()
    confirm_string = ctk.StringVar()
    confirm_entry = ctk.CTkEntry(
        main_frame,
        textvariable=confirm_string,
        placeholder_text="Confirm master password...",
        show="*",
        width=350,
        height=45,
        font=ctk.CTkFont(size=16)
    )
    confirm_entry.pack(pady=10)

    # Create button
    ctk.CTkButton(
        main_frame,
        text="Create Vault",
        command=create_password,
        width=200,
        height=45,
        font=ctk.CTkFont(size=16, weight="bold"),
        fg_color="#1E88E5",
        hover_color="#1565C0"
    ).pack(pady=20)

    # Output
    output_string = ctk.StringVar()
    ctk.CTkLabel(
        main_frame,
        textvariable=output_string,
        font=ctk.CTkFont(size=14),
        text_color="red"
    ).pack(pady=10)

    # Enter key
    confirm_entry.bind("<Return>", lambda e: create_password())
    entry.focus()


# ============================================
# MASTER PASSWORD
# ============================================
def show_master_password():
    """Master password entry page for returning users"""
    global vault

    def check():
        global vault
        password_input = entry_string.get()

        # ✅ Verify against the stored Argon2 hash
        if config.verify_master_password(password_input):
            # Correct password — initialize the vault
            vault = VaultManager(password_input, "vault.json")
            clear_window(window)
            show_main_menu()
        else:
            # Wrong password
            output_string.set("❌ Incorrect password. Please try again.")
            entry.delete(0, "end")
            entry.focus()

    # semi-transparent box
    overlay_box = ctk.CTkFrame(
        window,
        fg_color="#0D1424",  # Solid black
        corner_radius=25,  # Rounded corners
        border_width=1,
        border_color="#3A4A6B"
    )
    overlay_box.place(
        relx=0.5,
        rely=0.5,
        anchor="center",
        relwidth=0.35,  # 35% of window width
        relheight=0.5  # 50% of window height
    )


    # Center everything with place()
    main_frame = ctk.CTkFrame(window, fg_color="transparent")
    main_frame.place(relx=0.5, rely=0.5, anchor="center")

    # Title
    title_label = ctk.CTkLabel(
        main_frame,
        text="🔐 Master Password 🔐",
        font=ctk.CTkFont(size=40, weight="bold")
    )

    # Subtitle
    subtitle_label = ctk.CTkLabel(
        main_frame,
        text="Enter your master password to unlock your vault",
        font=ctk.CTkFont(size=16),
        text_color="gray"
    )

    # Input frame (holds entry + button side by side)
    input_frame = ctk.CTkFrame(main_frame, fg_color="transparent")

    # Entry
    entry_string = ctk.StringVar()
    entry = ctk.CTkEntry(
        input_frame,
        textvariable=entry_string,
        placeholder_text="Enter master password...",
        show="*",
        width=350,
        height=45,
        font=ctk.CTkFont(size=16)
    )

    # Unlock button
    button = ctk.CTkButton(
        main_frame,
        text="Unlock Vault",
        command=check,
        width=150,
        height=45,
        font=ctk.CTkFont(size=16, weight="bold"),
        fg_color="#1E88E5",
        hover_color="#1565C0"
    )

    # Error output
    output_string = ctk.StringVar()
    output_label = ctk.CTkLabel(
        main_frame,
        textvariable=output_string,
        font=ctk.CTkFont(size=16),
        text_color="red"
    )

    # ============================================
    # LAYOUT
    # ============================================

    title_label.pack(pady=(0, 10))
    subtitle_label.pack(pady=(0, 30))

    input_frame.pack(pady=10)
    entry.pack(side="left", padx=10)
    button.pack()

    output_label.pack(pady=20)

    # Bind Enter key to check
    entry.bind("<Return>", lambda e: check())

    # Focus on entry
    entry.focus()

# ============================================
# MAIN MENU
# ============================================
def show_main_menu():
    def main_menu_generate():
        clear_window(self=window)
        show_generate()

    def view_vault():
        clear_window(self=window)
        show_view_vault()

    def back_page():
        clear_window(self=window)
        show_master_password()

    overlay_box = ctk.CTkFrame(
        window,
        fg_color="#0D1424",  # Solid black
        corner_radius=25,  # Rounded corners
        border_width=1,
        border_color="#3A4A6B"
    )
    overlay_box.place(
        relx=0.5,
        rely=0.5,
        anchor="center",
        relwidth=0.35,  # 35% of window width
        relheight=0.5  # 50% of window height
    )

    main_frame = ctk.CTkFrame(window, fg_color="transparent")
    main_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Log Out button
    back_button = ctk.CTkButton(window, text="Log Out", command=back_page)
    back_button.pack(anchor="nw", padx=10, pady=10)

    # Title
    title_label = ctk.CTkLabel(
        window,
        text="🏠 Main Menu",
        font=ctk.CTkFont(size=48, weight="bold")
    )
    title_label.pack(pady=40)

    button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    button_frame.pack(expand=True)  # Centers the frame

    change_pw_button = ctk.CTkButton(
        button_frame,
        text="🔑 Change Master Password",
        command=lambda: (clear_window(window), show_change_master_password()),
        width=400,
        height=60,
        font=ctk.CTkFont(size=16, weight="bold"),
        fg_color="#FF9800",
        hover_color="#F57C00"
    )
    change_pw_button.pack(pady=10)

    generate_button = ctk.CTkButton(
        button_frame,
        text="🔑 Generate Password/Passphrase",
        command=main_menu_generate,
        width=400,  # ← Wider
        height=80,  # ← Taller
        font=ctk.CTkFont(size=20, weight="bold"),
        corner_radius=15
    )
    generate_button.pack(pady=20)

    view_vault_button = ctk.CTkButton( # Add view vault function
        button_frame,
        text="📋 View Vault",
        command = view_vault,
        width=400,
        height=80,
        font=ctk.CTkFont(size=20, weight="bold"),
        corner_radius=15
    )
    view_vault_button.pack(pady=20)

# ============================================
# VIEW VAULT
# ============================================
def show_view_vault():

    selected_service = None # currently selected service to edit/delete/view

    def back_page():
        clear_window(window)
        show_main_menu()

    def refresh_vault_list(search_term=""):
        # Clear the list frame
        for widget in list_frame.winfo_children():
            widget.destroy()

        # Get all services from vault
        services = vault.list_services()

        # Filter by search term
        if search_term:
            services = [s for s in services if search_term.lower() in s.lower()]

        if not services:
            ctk.CTkLabel(
                list_frame,
                text="📭 No passwords stored yet.",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            ).pack(pady=20)
            return

        # Create a header row
        header_frame = ctk.CTkFrame(list_frame, fg_color="#1A1A2E", height=30)
        header_frame.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(
            header_frame,
            text="Service",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=150
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            header_frame,
            text="Username",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=200
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            header_frame,
            text="Created",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=150
        ).pack(side="left", padx=10)

        # Display each service
        for service in services:
            entry = vault.vault.get(service, {})
            username = entry.get('username', 'Unknown')
            created = entry.get('created', 'Unknown')[:10]  # Show only date

            # Create a clickable row
            row_frame = ctk.CTkFrame(list_frame)
            row_frame.pack(fill="x", pady=2)

            # Store the service name in the frame
            row_frame.service_name = service

            # Service name
            ctk.CTkLabel(
                row_frame,
                text=f"🔑 {service}",
                font=ctk.CTkFont(size=14),
                width=150
            ).pack(side="left", padx=10)

            # Username
            ctk.CTkLabel(
                row_frame,
                text=username,
                font=ctk.CTkFont(size=14),
                width=200
            ).pack(side="left", padx=10)

            # Created date
            ctk.CTkLabel(
                row_frame,
                text=created,
                font=ctk.CTkFont(size=12),
                text_color="gray",
                width=150
            ).pack(side="left", padx=10)

            # Make row clickable
            def on_row_click(event, service_name=service):
                select_service(service_name)

            row_frame.bind("<Button-1>", on_row_click)
            for child in row_frame.winfo_children():
                child.bind("<Button-1>", on_row_click)

    def select_service(service):
        """Select a service and enable action buttons"""
        nonlocal selected_service
        selected_service = service

        # Update status
        status_label.configure(
            text=f"✅ Selected: {service}",
            text_color="#4CAF50"
        )

        # Enable action buttons
        view_button.configure(state="normal")
        edit_button.configure(state="normal")
        delete_button.configure(state="normal")

    def view_password():
        """View the selected password in a popup"""
        nonlocal selected_service

        if not selected_service:
            status_label.configure(text="❌ Please select a service first!", text_color="red")
            return

        # Get the password
        password = vault.get_password(selected_service)
        entry = vault.vault.get(selected_service, {})
        username = entry.get('username', 'Unknown')
        url = entry.get('url', '')
        notes = entry.get('notes', '')

        # Create a popup window
        popup = ctk.CTkToplevel(window)
        popup.title(f"🔑 {selected_service}")
        popup.geometry("500x400")
        popup.configure(fg_color="#1A1A2E")

        # Make it modal
        popup.transient(window)
        popup.grab_set()

        # Content
        ctk.CTkLabel(
            popup,
            text=f"🔑 {selected_service}",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(20, 10))

        # Username
        username_frame = ctk.CTkFrame(popup, fg_color="transparent")
        username_frame.pack(pady=5)

        ctk.CTkLabel(
            username_frame,
            text=f"Username: {username}",
            font=ctk.CTkFont(size=16)
        ).pack(side="left", padx=5)

        def copy_username():
            window.clipboard_clear()
            window.clipboard_append(username)
            status_label.configure(text="📋 Username copied to clipboard!", text_color="#4CAF50")

        ctk.CTkButton(
            username_frame,
            text="📋 Copy",
            command=copy_username,
            width=40,
            height=25,
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=5)

        # Password (with copy button)
        password_frame = ctk.CTkFrame(popup, fg_color="transparent")
        password_frame.pack(pady=5)

        ctk.CTkLabel(password_frame, text=f"Password: ", font=ctk.CTkFont(size=16)).pack(side="left")

        password_label = ctk.CTkLabel(
            password_frame,
            text=password,
            font=ctk.CTkFont(size=16),
            text_color="#4CAF50"
        )
        password_label.pack(side="left", padx=5)

        def copy_password(): # copies password to clipboard
            window.clipboard_clear()
            window.clipboard_append(password)
            status_label.configure(text="📋 Password copied to clipboard!", text_color="#4CAF50")

        ctk.CTkButton(
            password_frame,
            text="📋 Copy",
            command=copy_password,
            width=60,
            height=25,
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=5)

        # URL
        if url:
            url_frame = ctk.CTkFrame(popup, fg_color="transparent")
            url_frame.pack(pady=5)

            ctk.CTkLabel(
                url_frame,
                text=f"URL: {url}",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            ).pack(side="left", padx=5)

            def copy_url():
                window.clipboard_clear()
                window.clipboard_append(url)
                status_label.configure(text="📋 URL copied to clipboard!", text_color="#4CAF50")

            ctk.CTkButton(
                url_frame,
                text="📋 Copy",
                command=copy_url,
                width=40,
                height=25,
                font=ctk.CTkFont(size=12)
            ).pack(side="left", padx=5)

        # Notes
        if notes:
            ctk.CTkLabel(
                popup,
                text=f"Notes: {notes}",
                font=ctk.CTkFont(size=14),
                text_color="gray",
                wraplength=450
            ).pack(pady=5)

        # Close button
        ctk.CTkButton(
            popup,
            text="Close",
            command=popup.destroy,
            width=100,
            height=35
        ).pack(pady=20)

    def edit_password():
        nonlocal selected_service

        if not selected_service:
            status_label.configure(text="❌ Please select a service first!", text_color="red")
            return

        # Get current data
        entry = vault.vault.get(selected_service, {})
        current_username = entry.get('username', '')
        current_url = entry.get('url', '')
        current_notes = entry.get('notes', '')

        # Create edit popup
        popup = ctk.CTkToplevel(window)
        popup.title(f"✏️ Edit {selected_service}")
        popup.geometry("450x450")
        popup.configure(fg_color="#1A1A2E")
        popup.transient(window)
        popup.grab_set()

        ctk.CTkLabel(
            popup,
            text=f"✏️ Edit {selected_service}",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 10))

        # Username
        ctk.CTkLabel(popup, text="Username:").pack()
        username_entry = ctk.CTkEntry(popup, width=300)
        username_entry.pack(pady=5)
        username_entry.insert(0, current_username)

        # URL
        ctk.CTkLabel(popup, text="URL (optional):").pack()
        url_entry = ctk.CTkEntry(popup, width=300)
        url_entry.pack(pady=5)
        if current_url:
            url_entry.insert(0, current_url)

        # Notes
        ctk.CTkLabel(popup, text="Notes (optional):").pack()
        notes_textbox = ctk.CTkTextbox(popup, height=100, width=300)
        notes_textbox.pack(pady=5)
        if current_notes:
            notes_textbox.insert("1.0", current_notes)

        def save_edit():
            new_username = username_entry.get().strip()
            new_url = url_entry.get().strip()
            new_notes = notes_textbox.get("1.0", "end-1c").strip()

            if not new_username:
                status_label.configure(text="❌ Username cannot be empty!", text_color="red")
                return

            # Update the entry
            vault.vault[selected_service]['username'] = new_username
            if new_url:
                vault.vault[selected_service]['url'] = new_url
            else:
                vault.vault[selected_service].pop('url', None)

            if new_notes:
                # Re-encrypt notes
                from encrypter import PasswordEncryptor
                vault.vault[selected_service]['notes'] = encryptor.encrypt(new_notes)
            else:
                vault.vault[selected_service].pop('notes', None)

            vault.save_vault()

            popup.destroy()
            refresh_vault_list(search_entry.get().strip())
            status_label.configure(
                text=f"✅ {selected_service} updated successfully!",
                text_color="#4CAF50"
            )

        ctk.CTkButton(
            popup,
            text="💾 Save Changes",
            command=save_edit,
            width=150,
            height=40,
            fg_color="#2B7A4B",
            hover_color="#1E5F3A"
        ).pack(pady=20)

    def delete_password():
        nonlocal selected_service

        if not selected_service:
            status_label.configure(text="❌ Please select a service first!", text_color="red")
            return

        # Create confirmation popup
        popup = ctk.CTkToplevel(window)
        popup.title("🗑️ Confirm Delete")
        popup.geometry("400x200")
        popup.configure(fg_color="#1A1A2E")
        popup.transient(window)
        popup.grab_set()

        ctk.CTkLabel(
            popup,
            text=f"🗑️ Delete '{selected_service}'?",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)

        ctk.CTkLabel(
            popup,
            text="This action cannot be undone.",
            font=ctk.CTkFont(size=14),
            text_color="red"
        ).pack(pady=10)

        def confirm_delete():
            nonlocal selected_service  # ← ADD THIS

            vault.delete_service(selected_service)
            popup.destroy()
            selected_service = None
            refresh_vault_list(search_entry.get().strip())

            # Disable action buttons
            view_button.configure(state="disabled")
            edit_button.configure(state="disabled")
            delete_button.configure(state="disabled")

            status_label.configure(
                text=f"🗑️ '{selected_service}' deleted successfully!",
                text_color="#FF5722"
            )

        # Buttons
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(
            btn_frame,
            text="🗑️ Delete",
            command=confirm_delete,
            width=100,
            height=35,
            fg_color="#E53935",
            hover_color="#C62828"
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=popup.destroy,
            width=100,
            height=35
        ).pack(side="left", padx=10)

    def search_vault():
        """Search for services"""
        search_term = search_entry.get().strip()
        refresh_vault_list(search_term)
        status_label.configure(
            text=f"🔍 Showing results for: '{search_term}'" if search_term else "📋 Showing all entries",
            text_color="gray"
        )

    # ============================================
    # UI SETUP
    # ============================================

    # Header with back button
    header_frame = ctk.CTkFrame(window, fg_color="transparent")
    header_frame.pack(fill="x", padx=10, pady=10)

    back_button = ctk.CTkButton(
        header_frame,
        text="← Back",
        command=back_page,
        width=80,
        height=35
    )
    back_button.pack(side="left")

    ctk.CTkButton(
        header_frame,
        text="🔒 Lock",
        command=lambda: (clear_window(window), show_master_password()),
        width=80,
        height=35,
        fg_color="#E53935",
        hover_color="#C62828"
    ).pack(side="right")

    # Title
    title_label = ctk.CTkLabel(
        window,
        text="📋 View Vault",
        font=ctk.CTkFont(size=32, weight="bold")
    )
    title_label.pack(pady=10)

    # Search bar
    search_frame = ctk.CTkFrame(window, fg_color="transparent")
    search_frame.pack(pady=10)

    search_entry = ctk.CTkEntry(
        search_frame,
        placeholder_text="Search services...",
        width=300,
        height=35
    )
    search_entry.pack(side="left", padx=5)

    search_button = ctk.CTkButton(
        search_frame,
        text="🔍",
        command=search_vault,
        width=40,
        height=35
    )
    search_button.pack(side="left", padx=5)

    # Bind Enter key to search
    search_entry.bind("<Return>", lambda e: search_vault())

    # List frame (scrollable)
    list_frame = ctk.CTkScrollableFrame(
        window,
        height=350,
        fg_color="#1A1A2E"
    )
    list_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Action buttons
    action_frame = ctk.CTkFrame(window, fg_color="transparent")
    action_frame.pack(pady=10)

    view_button = ctk.CTkButton(
        action_frame,
        text="👁️ View",
        command=view_password,
        width=120,
        height=35,
        state="disabled"  # Starts disabled
    )
    view_button.pack(side="left", padx=5)

    edit_button = ctk.CTkButton(
        action_frame,
        text="✏️ Edit",
        command=edit_password,
        width=120,
        height=35,
        state="disabled",
        fg_color="#FF9800",
        hover_color="#F57C00"
    )
    edit_button.pack(side="left", padx=5)

    delete_button = ctk.CTkButton(
        action_frame,
        text="🗑️ Delete",
        command=delete_password,
        width=120,
        height=35,
        state="disabled",
        fg_color="#E53935",
        hover_color="#C62828"
    )
    delete_button.pack(side="left", padx=5)

    # Status label
    status_label = ctk.CTkLabel(
        window,
        text="📋 Select a service to view, edit, or delete",
        font=ctk.CTkFont(size=14),
        text_color="gray"
    )
    status_label.pack(pady=5)

    # Refresh the vault list
    refresh_vault_list()

# ============================================
# GENERATE OPTION PAGE
# ============================================
def show_generate():

    def generate_password_page():
        clear_window(self=window)
        show_generate_password()

    def generate_passphrase():
        clear_window(self=window)
        show_generate_passphrase()

    def back_page():
        clear_window(self=window)
        show_main_menu()

    overlay_box = ctk.CTkFrame(
        window,
        fg_color="#0D1424",  # Solid black
        corner_radius=25,  # Rounded corners
        border_width=1,
        border_color="#3A4A6B"
    )
    overlay_box.place(
        relx=0.5,
        rely=0.5,
        anchor="center",
        relwidth=0.35,  # 35% of window width
        relheight=0.5  # 50% of window height
    )

    main_frame = ctk.CTkFrame(overlay_box, fg_color="transparent")
    main_frame.place(relx=0.5, rely=0.5, anchor="center")

    back_button = ctk.CTkButton(window, text = "Back", command = back_page)
    back_button.pack(anchor="nw", padx=10, pady=10)

    title_label = ctk.CTkLabel(window,
                               text="Generate password/passphrase",
                               font=ctk.CTkFont(size=48, weight="bold"),
                               )

    password_button = ctk.CTkButton(main_frame, text = "🔑 Password",
                                    command = generate_password_page,
                                    width=400,  # ← Wider
                                    height=80,  # ← Taller
                                    font=ctk.CTkFont(size=20, weight="bold"),
                                    corner_radius=15)
    passphrase_button = ctk.CTkButton(main_frame,
                                      text = "💬 Passphrase",
                                      command = generate_passphrase,
                                      width=400,  # ← Wider
                                      height=80,  # ← Taller
                                      font=ctk.CTkFont(size=20, weight="bold"),
                                      corner_radius=15)

    title_label.pack()
    password_button.pack()
    passphrase_button.pack(pady = 30)

# ============================================
# SAVE PAGE
# ============================================
def show_save_page(window, password_to_save):
    # semi-transparent box
    overlay_box = ctk.CTkFrame(
        window,
        fg_color="#0D1424",  # Solid black
        corner_radius=25,  # Rounded corners
        border_width=1,
        border_color="#3A4A6B"
    )
    overlay_box.place(
        relx=0.5,
        rely=0.5,
        anchor="center",
        relwidth=0.35,  # 35% of window width
        relheight=0.5  # 50% of window height
    )

    # Center everything with place()
    main_frame = ctk.CTkFrame(window, fg_color="transparent")


    current_password = password_to_save

    def main_menu_generate():
        clear_window(self=window)
        show_generate()

    def main_menu():
        clear_window(self=window)
        show_main_menu()

    def back_page():
        clear_window(self=window)
        show_generate()

    def save():

        service = service_entry_string.get().strip() # strip = removes white space
        username = username_entry_string.get().strip()
        url = url_entry_string.get().strip()
        notes = notes_textbox.get("1.0", "end-1c").strip()

        if not service:
            status_label.configure(text = "Please enter a service name!")
            return

        if not username:
            status_label.configure(text = "Please enter a username!")
            return

        try:
            #Save to vault (encrypts automatically)
            vault.add_password(
                service=service,
                username=username,
                password=current_password,
                url=url if url else None,
                notes=notes if notes else None
            )

            # Clear fields after saving
            service_entry_string.set("")
            username_entry_string.set("")
            url_entry_string.set("")
            notes_textbox.delete("1.0", "end")

            field_frame.pack_forget()

            header_frame.pack_forget()

            success_label.configure(
                text=f"Password for '{service}' saved securely!",
                text_color="green"
            )
            success_frame.pack(pady=20)

            status_label.pack_forget()

        except Exception as e:
            status_label.configure(text=f"❌ Error saving: {str(e)}", text_color="red")


# DEBUGGING
        '''
        print("=" * 40)
        print("💾 SAVING TO VAULT")
        print(f"   Service: {service}")
        print(f"   Username: {username}")
        print(f"   Password: {current_password}")
        print(f"   URL: {url}")
        print(f"   Notes: {notes}")
        print("=" * 40)
        '''

    field_frame = ctk.CTkFrame(main_frame, fg_color="transparent")

    service_frame = ctk.CTkFrame(field_frame, fg_color="transparent")

    username_frame = ctk.CTkFrame(field_frame, fg_color="transparent")

    url_frame = ctk.CTkFrame(field_frame, fg_color="transparent")

    notes_frame = ctk.CTkFrame(field_frame, fg_color="transparent")

    header_frame = ctk.CTkFrame(window, fg_color="transparent")

    success_frame = ctk.CTkFrame(main_frame, fg_color="transparent")

    # success
    success_label = ctk.CTkLabel(
        success_frame,
        text="",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color="green"
    )
    success_label.pack(pady=10)

    action_frame = ctk.CTkFrame(success_frame, fg_color="transparent")
    action_frame.pack(pady=10)

    generate_another_btn = ctk.CTkButton(
        action_frame,
        text="🔑 Generate Another",
        command=lambda: main_menu_generate(),
        width=180,
        height=40
    )
    generate_another_btn.pack(side="left", padx=10)

    main_menu_btn = ctk.CTkButton(
        action_frame,
        text="🏠 Main Menu",
        command=lambda: main_menu(),
        width=180,
        height=40
    )
    main_menu_btn.pack(side="left", padx=10)

    # save widgets

    service_entry_string = ctk.StringVar()
    username_entry_string = ctk.StringVar()
    url_entry_string = ctk.StringVar()

    save_label = ctk.CTkLabel(window,
                              text = "Save Password/Passphrase",
                              font = ctk.CTkFont(size = 24, weight = "bold"))

    back_button = ctk.CTkButton(header_frame,
                  text = "Back",
                  command = back_page)

    save_button = ctk.CTkButton(header_frame,
                                text="Save",
                                command = save)

    service_label = ctk.CTkLabel(service_frame, text = "Enter the service: ")
    username_label = ctk.CTkLabel(username_frame, text = "Enter username: ")
    url_label = ctk.CTkLabel(url_frame, text = "Enter URL (Optional): ")
    notes_label = ctk.CTkLabel(notes_frame, text = "Notes (Optional): ")
    status_label = ctk.CTkLabel(window, text = "", font = ctk.CTkFont(size = 24, weight = "bold"))

    service_entry = ctk.CTkEntry(service_frame, textvariable = service_entry_string)
    username_entry = ctk.CTkEntry(username_frame, textvariable = username_entry_string)
    url_entry = ctk.CTkEntry(url_frame, textvariable = url_entry_string)
    notes_textbox = ctk.CTkTextbox(notes_frame, height=80, width=280)


    header_frame.pack(fill = 'x', padx = 10, pady = 10)
    main_frame.place(relx=0.5, rely=0.5, anchor="center")
    back_button.pack(side = 'left')
    save_button.pack(side = 'right')
    save_label.pack(pady = 10)
    field_frame.pack(pady=10)
    service_label.pack(side="left", padx=10)
    username_label.pack(side="left", padx=10)
    url_label.pack(side="left", padx=10)

    service_entry.pack(side = "left", pady = 10)
    username_entry.pack(side = "left", pady = 10)
    url_entry.pack(side = "left", pady = 10)

    service_frame.pack(pady = 10)
    username_frame.pack(pady = 10)
    url_frame.pack(pady = 10)


    notes_label.pack(pady = 10)
    notes_textbox.pack(pady=10)
    notes_frame.pack(pady=10)

    status_label.pack(pady = 10)


# ============================================
# GENERATE PASSWORD
# ============================================
def show_generate_password():
    uppercase_var = ctk.BooleanVar(value = False)
    symbols_var = ctk.BooleanVar(value = False)
    numbers_var = ctk.BooleanVar(value = False)
    output_string = ctk.StringVar() # outputs generated password

    generated_password = ""

    def save_page():
        nonlocal generated_password  # ← Need this to access the password

        if not generated_password:
            output_string.set("Please generate a password first!")
            return

        clear_window(self=window)
        show_save_page(window, generated_password)  # ← Pass the password!

    def back_page():
        clear_window(self=window)
        show_generate()

    def making_password_func():
        # allows modification of variable
        nonlocal generated_password

        # Get user input and check if it's a digit
        user_input = entry_string.get().strip()

        # Check if empty
        if not user_input:
            output_string.set("Please enter a number that is at least 5.")
            save_button.pack_forget()  # Hide save button if error
            return

        # Check if it's a number
        if not user_input.isdigit():
            output_string.set("Error (invalid input): Please input a number.")
            save_button.pack_forget()  # Hide save button if error
            return

        # Convert to int (safe now because we checked with isdigit)
        entry_int = int(user_input)

        # Check if within range
        if entry_int < 5:
            output_string.set("5 - 24")
            save_button.pack_forget()  # Hide save button if error
            return
        elif entry_int > 24:
            output_string.set("5 - 24")
            save_button.pack_forget()
            return

        # Generate the password
        generated_password = generate_password(
            length=entry_int,
            use_upper=uppercase_var.get(),
            use_digits=numbers_var.get(),
            use_symbols=symbols_var.get()
        )
        output_string.set(generated_password)


        # Show the save button
        save_button.pack(pady=10)

# widgets

    overlay_box = ctk.CTkFrame(
        window,
        fg_color="#0D1424",  # Solid black
        corner_radius=25,  # Rounded corners
        border_width=1,
        border_color="#3A4A6B"
    )
    overlay_box.place(
        relx=0.5,
        rely=0.5,
        anchor="center",
        relwidth=0.35,  # 35% of window width
        relheight=0.5  # 50% of window height
    )

    main_frame = ctk.CTkFrame(overlay_box, fg_color="transparent")
    main_frame.place(relx=0.5, rely=0.5, anchor="center")

    title_label = ctk.CTkLabel(window,
                               text="Password Generation",
                               font=ctk.CTkFont(size=32, weight="bold"))


    checkbox_frame = ctk.CTkFrame(main_frame, fg_color="transparent")  # Invisible frame. groups checkbox together

    entry_frame = ctk.CTkFrame(main_frame, fg_color="transparent") # groups length together

    uppercase_check = ctk.CTkCheckBox(checkbox_frame,
                                text = "Uppercase",
                                variable = uppercase_var,
                                font=ctk.CTkFont(size=16),
                                checkbox_width=24,
                                checkbox_height=24)

    symbols_check = ctk.CTkCheckBox(checkbox_frame,
                                text = "Symbols",
                                variable = symbols_var,
                                font=ctk.CTkFont(size=16),
                                checkbox_width=24,
                                checkbox_height=24)

    numbers_check = ctk.CTkCheckBox(checkbox_frame,
                                text = "Numbers",
                                variable = numbers_var,
                                font=ctk.CTkFont(size=16),
                                checkbox_width=24,
                                checkbox_height=24)

    save_button = ctk.CTkButton(main_frame,
                                text = "💾 Save?",
                                command = save_page,
                                width=200,
                                height=45,
                                font=ctk.CTkFont(size=16, weight="bold"),
                                fg_color="#2B7A4B",
                                hover_color="#1E5F3A"
                                )

    entry_string = ctk.StringVar()
    entry = ctk.CTkEntry(entry_frame, textvariable = entry_string) # length
    entry_label = ctk.CTkLabel(entry_frame, text = "Length (5-24): ", font=ctk.CTkFont(size=18))

    generate_button = ctk.CTkButton(main_frame,
                                    text = "Generate Password", command = making_password_func,
                                    width=280,
                                    height=50,
                                    font=ctk.CTkFont(size=18, weight="bold"))

    output_label = ctk.CTkLabel(main_frame,
                                 text = "Output",
                                 font=ctk.CTkFont(size=24, weight="bold"),
                                 textvariable = output_string)

    back_button = ctk.CTkButton(window,
                                text = "Back",
                                command = back_page,
                                width=100,
                                height=40,
                                font=ctk.CTkFont(size=16)
                                )

    back_button.pack(anchor = "nw", padx = 10, pady = 10)

    title_label.pack(pady=10)

    entry_frame.pack(pady=5)
    entry_label.pack(side='left', pady=5)
    entry.pack(side = 'left', pady=5)

    checkbox_frame.pack(pady = 5)
    uppercase_check.pack(side = 'left', padx = 10)
    symbols_check.pack(side = 'left', padx = 10)
    numbers_check.pack(side = 'left', padx = 10)

    generate_button.pack(pady = 10)

    output_label.pack(pady = 10)

# ============================================
# GENERATE PASSPHRASE
# ============================================
def show_generate_passphrase():
    # semi-transparent box
    overlay_box = ctk.CTkFrame(
        window,
        fg_color="#0D1424",  # Solid black
        corner_radius=25,  # Rounded corners
        border_width=1,
        border_color="#3A4A6B"
    )
    overlay_box.place(
        relx=0.5,
        rely=0.5,
        anchor="center",
        relwidth=0.35,  # 35% of window width
        relheight=0.5  # 50% of window height
    )

    # Center everything with place()
    main_frame = ctk.CTkFrame(overlay_box, fg_color="transparent")
    main_frame.place(relx=0.5, rely=0.5, anchor="center")

    # Variables
    output_string = ctk.StringVar()
    generated_passphrase = ""

    def back_page():
        clear_window(window)
        show_generate()

    def go_to_save_page():
        """Navigate to save page with the generated passphrase"""
        nonlocal generated_passphrase

        if not generated_passphrase:
            output_string.set("❌ Please generate a passphrase first!")
            return

        clear_window(window)
        show_save_page(window, generated_passphrase)  # ← Pass to save page

    def making_passphrase_func():
        """Generate passphrase and show save button"""
        nonlocal generated_passphrase

        user_input = entry_string.get().strip()

        # Check if empty
        if not user_input:
            output_string.set("❌ Please enter a number that is at least 3.")
            save_button.pack_forget()
            return

        # Check if it's a number
        if not user_input.isdigit():
            output_string.set("❌ Error (invalid input): Please input a number.")
            save_button.pack_forget()
            return

        # Convert to int
        entry_int = int(user_input)

        # Check range
        if entry_int < 3:
            output_string.set("❌ Passphrase must have at least 3 words.")
            save_button.pack_forget()
            return
        elif entry_int > 6:
            output_string.set("❌ Maximum 6 words allowed.")
            save_button.pack_forget()
            return

        # Generate the passphrase
        generated_passphrase = generate_passphrase(num_words=entry_int)
        output_string.set(f"💬 {generated_passphrase}")

        # ✅ Show the save button
        save_button.pack(pady=10)
        status_label.configure(text="✅ Passphrase generated! Click Save to store it.", text_color="green")

    # UI SETUP
    # Back button
    back_button = ctk.CTkButton(window, text="Back", command=back_page)
    back_button.pack(anchor="nw", padx=10, pady=10)

    # Title
    title_label = ctk.CTkLabel(
        window,
        text="💬 Passphrase Generation",
        font=ctk.CTkFont(size=24, weight="bold")
    )
    title_label.pack(pady=10)

    # Entry frame
    entry_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    entry_frame.pack(pady=5)

    entry_label = ctk.CTkLabel(entry_frame, text="Number of words (3-6):", font=ctk.CTkFont(size=24, weight="bold"))
    entry_label.pack(side='left', pady=5)

    entry_string = ctk.StringVar(value="4")
    entry = ctk.CTkEntry(entry_frame, textvariable=entry_string, width=80)
    entry.pack(side='left', pady=5)

    # Generate button
    generate_button = ctk.CTkButton(
        main_frame,
        text="💬 Generate Passphrase",
        command=making_passphrase_func,
        width=280,
        height=50,
        font=ctk.CTkFont(size=16, weight="bold")
    )
    generate_button.pack(pady=10)

    # Output label
    output_label = ctk.CTkLabel(
        main_frame,
        textvariable=output_string,
        font=ctk.CTkFont(size=24, weight="bold"),
        wraplength=500
    )
    output_label.pack(pady=10)


    # Save button (Starts hidden)
    save_button = ctk.CTkButton(
        main_frame,
        text="💾 Go to Save Page",
        command=go_to_save_page,
        width=280,
        height=50,
        fg_color="#2B7A4B",
        hover_color="#1E5F3A",
        font=ctk.CTkFont(size=16, weight="bold")
    )
    # Don't pack yet - appears after generation

    # Status label
    status_label = ctk.CTkLabel(main_frame, text="", font=ctk.CTkFont(size=14))
    status_label.pack(pady=10)

    # Bind Enter key
    entry.bind("<Return>", lambda e: making_passphrase_func())
    entry.focus()

# ============================================
# CHANGE MASTER PASSWORD
# ============================================
def show_change_master_password():
    """Page for changing the master password."""
    global vault

    def submit():
        current_pw = current_string.get().strip()
        new_pw = new_string.get().strip()
        confirm_pw = confirm_string.get().strip()

        # Validation
        if not current_pw or not new_pw or not confirm_pw:
            status_label.configure(text="❌ All fields are required!", text_color="red")
            return

        if not config.verify_master_password(current_pw):
            status_label.configure(text="❌ Current password is incorrect!", text_color="red")
            current_string.set("")
            return

        if len(new_pw) < 8:
            status_label.configure(text="❌ New password must be at least 8 characters!", text_color="red")
            return

        if new_pw != confirm_pw:
            status_label.configure(text="❌ New passwords do not match!", text_color="red")
            return

        if new_pw == current_pw:
            status_label.configure(text="❌ New password must differ from the current one!", text_color="red")
            return

        try:
            # 1. Re-encrypt the vault with the new password
            vault.re_encrypt_all(current_pw, new_pw)

            # 2. Update the Argon2id hash
            config.change_master_password(new_pw)

            status_label.configure(
                text="✅ Master password changed successfully!",
                text_color="green"
            )

            # 3. Return to main menu after a short delay
            window.after(1500, lambda: (clear_window(window), show_main_menu()))

        except Exception as e:
            status_label.configure(text=f"❌ Error: {str(e)}", text_color="red")

    # UI
    overlay = ctk.CTkFrame(window, fg_color="#0D1424", corner_radius=25, border_width=1, border_color="#3A4A6B")
    overlay.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.4, relheight=0.7)

    main_frame = ctk.CTkFrame(overlay, fg_color="transparent")
    main_frame.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(main_frame, text="🔑 Change Master Password",
                 font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(0, 20))

    # Current password
    ctk.CTkLabel(main_frame, text="Current Master Password:").pack()
    current_string = ctk.StringVar()
    ctk.CTkEntry(main_frame, textvariable=current_string, show="*",
                 width=350, height=40, font=ctk.CTkFont(size=14)).pack(pady=5)

    # New password
    ctk.CTkLabel(main_frame, text="New Master Password:").pack(pady=(15, 0))
    new_string = ctk.StringVar()
    ctk.CTkEntry(main_frame, textvariable=new_string, show="*",
                 width=350, height=40, font=ctk.CTkFont(size=14)).pack(pady=5)

    # Confirm new password
    ctk.CTkLabel(main_frame, text="Confirm New Password:").pack(pady=(15, 0))
    confirm_string = ctk.StringVar()
    ctk.CTkEntry(main_frame, textvariable=confirm_string, show="*",
                 width=350, height=40, font=ctk.CTkFont(size=14)).pack(pady=5)

    # Buttons
    btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    btn_frame.pack(pady=20)

    ctk.CTkButton(btn_frame, text="💾 Change Password", command=submit,
                  width=180, height=45, fg_color="#2B7A4B", hover_color="#1E5F3A",
                  font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=10)

    ctk.CTkButton(btn_frame, text="← Cancel",
                  command=lambda: (clear_window(window), show_main_menu()),
                  width=120, height=45).pack(side="left", padx=10)

    # Status
    status_label = ctk.CTkLabel(main_frame, text="", font=ctk.CTkFont(size=14))
    status_label.pack(pady=10)

# ============================================
# RUN
# ============================================
def main():
    global window

    # Setup the window
    setup_window()

    # Check if first run
    if config.is_first_run():
        show_setup_screen()  # First time → create password
    else:
        show_master_password()  # Returning → enter password

    window.mainloop()

if __name__ == "__main__":
    main()

