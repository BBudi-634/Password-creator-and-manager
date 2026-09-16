import string
import secrets
from wordfreq import random_words


def generate_password(length=16, use_upper=True, use_digits=True, use_symbols=True):
    # Start with lowercase letters (minimum)
    alphabet = string.ascii_lowercase

    # Add options based on user preferences
    if use_upper:
        alphabet += string.ascii_uppercase
    if use_digits:
        alphabet += string.digits
    if use_symbols:
        alphabet += string.punctuation

    # Ensure we have at least something
    if not alphabet:
        alphabet = string.ascii_lowercase

    # Generate password using cryptographically secure random
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_passphrase(num_words=4, add_number=True):
    passphrase = random_words(lang = "en", nwords = num_words, bits_per_word = 12)

    return passphrase

'''
# test
def interactive_mode():
    print("PASSWORD/PASSPHRASE GENERATOR")
    print("=" * 40)

    # Ask for type
    while True:
        choice = input("Password or passphrase? (password/passphrase): ").strip().lower()
        if choice in ['password', 'passphrase']:
            break
        print("Invalid input. Please enter 'password' or 'passphrase'.")

    if choice == 'password':
        # Get length
        while True:
            length = input("Length (5-24): ").strip()
            if not length:
                print("Error: Please enter a number.")
                continue
            if not length.isdigit():
                print("Error: Please enter a valid number.")
                continue
            length = int(length)
            if 5 <= length <= 24:
                break
            print("Error: Length must be between 5 and 24.")

        # Get preferences
        for_symbol = input("Do you want to include symbols? (Y/N): ")
        for_symbol = for_symbol.upper()
        while for_symbol != "Y" and for_symbol != "N":
            print("Invalid input. Please try again.")
            for_symbol = input("Do you want to include symbols? (Y/N): ")
            for_symbol = for_symbol.upper()

        for_numbers = input("Do you want to include numbers? (Y/N): ")
        for_numbers = for_numbers.upper()
        while for_numbers != "Y" and for_numbers != "N":
            print("Invalid input. Please try again.")
            for_numbers = input("Do you want to include numbers? (Y/N): ")
            for_numbers = for_numbers.upper()

        for_upper = input("Do you want to include Uppercase letters? (Y/N): ")
        for_upper = for_upper.upper()
        while for_upper != "Y" and for_upper != "N":
            print("Invalid input. Please try again.")
            for_upper = input("Do you want to include Uppercase letters? (Y/N): ")
            for_upper = for_upper.upper()

        for_numbers = True if for_numbers == "Y" else False
        for_symbol = True if for_symbol == "Y" else False
        for_upper = True if for_upper == "Y" else False

        # Generate password
        password = generate_password(length, for_upper, for_numbers, for_symbol)
        print(f"\nGenerated password: {password}")
        return password

    else:  # passphrase
        # Get number of words
        while True:
            num_words = input("How many words do you want in your passphrase?: ")
            if not num_words:
                print("Error: You didn't enter anything. Please enter a number.")
                continue
            if not num_words.isdigit():
                print("Error: Please enter a valid number (not words or decimals).")
                continue
            num_words = int(num_words)
            if num_words >= 3:
                break
            print("Error: You must have at least more then 3 words.")

        # Generate passphrase
        passphrase = generate_passphrase(num_words)
        print(f"\nGenerated passphrase: {passphrase}")
        return passphrase


if __name__ == "__main__":
    # Run interactive mode when script is executed directly
    interactive_mode()
'''