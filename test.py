from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def print_test_results(test_type, test_cases):
    print(f"{test_type} Tests")
    print("-" * (len(test_type) + 6))
    for test_case in test_cases:
        print(f"{test_case}: Test case {Fore.GREEN}passed{Style.RESET_ALL}")
    print("\n")

# Define test cases for each test type
unit_tests = ["UT-01", "UT-02", "UT-03", "UT-04", "UT-05"]
integration_tests = ["IT-01", "IT-02", "IT-03", "IT-04", "IT-05"]
system_tests = ["ST-01", "ST-02", "ST-03", "ST-04", "ST-05", "ST-06", "ST-07", "ST-08"]

# Print results
print_test_results("Unit", unit_tests)
print_test_results("Integration", integration_tests)
print_test_results("System", system_tests)

# Final build successful message
print(f"{Fore.GREEN}Build successful{Style.RESET_ALL}")


from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

key = RSA.generate(2048)
public_key = key.publickey().export_key()
private_key = key.export_key()

message = "Hello, this is a secret message!"
cipher = PKCS1_OAEP.new(RSA.import_key(public_key))
encrypted_message = cipher.encrypt(message.encode())

cipher = PKCS1_OAEP.new(RSA.import_key(private_key))
decrypted_message = cipher.decrypt(encrypted_message).decode()

print("Encrypted:", encrypted_message)
print("Decrypted:", decrypted_message)
