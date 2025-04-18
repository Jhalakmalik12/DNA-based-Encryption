import random
import json

# --- Encoding & DNA Setup ---

def text_to_dna_numbers(text):
    binary = ''.join(format(ord(c), '08b') for c in text)
    twobit_segments = [binary[i:i+2] for i in range(0, len(binary), 2)]
    return [int(b, 2) for b in twobit_segments]

def dna_numbers_to_text(dna_numbers):
    binary_str = ''.join(format(num, '02b') for num in dna_numbers)
    chars = [chr(int(binary_str[i:i+8], 2)) for i in range(0, len(binary_str), 8)]
    return ''.join(chars)

def generate_random_dna(length):
    return ''.join(random.choice('ATCG') for _ in range(length))

def dna_to_numbers(dna_seq):
    mapping = {'A': 0, 'T': 1, 'C': 2, 'G': 3}
    return [mapping[base] for base in dna_seq]

# --- Substitution & Transposition ---

def substitution(data, key):
    return [(d + k) % 4 for d, k in zip(data, key)]

def reverse_substitution(data, key):
    return [(d - k + 4) % 4 for d, k in zip(data, key)]

def transposition(data, key):
    paired = list(zip(key, data))
    paired.sort(key=lambda x: x[0])
    return [x[1] for x in paired]

def reverse_transposition(data, key):
    paired = list(zip(key, data))
    sorted_indices = sorted(range(len(key)), key=lambda i: key[i])
    result = [0] * len(data)
    for i, idx in enumerate(sorted_indices):
        result[idx] = paired[i][1]
    return result

# --- Encryption & Decryption ---

def encrypt(data, dna_seq, n_rounds):
    dna_nums = dna_to_numbers(dna_seq)
    round_keys = []

    for _ in range(n_rounds):
        sindex = random.randint(0, len(dna_nums) - len(data))
        tindex = random.randint(0, len(dna_nums) - len(data))

        subkey = dna_nums[sindex:sindex + len(data)]
        transkey = dna_nums[tindex:tindex + len(data)]

        data = substitution(data, subkey)
        data = transposition(data, transkey)

        round_keys.append({'sindex': sindex, 'tindex': tindex})

    return data, round_keys

def decrypt(data, dna_seq, round_keys):
    dna_nums = dna_to_numbers(dna_seq)

    for round_key in reversed(round_keys):
        sindex = round_key['sindex']
        tindex = round_key['tindex']

        transkey = dna_nums[tindex:tindex + len(data)]
        subkey = dna_nums[sindex:sindex + len(data)]

        data = reverse_transposition(data, transkey)
        data = reverse_substitution(data, subkey)

    return data

# --- File Utilities ---

def save_list_to_file(lst, filename):
    with open(filename, 'w') as f:
        f.write(' '.join(map(str, lst)))

def load_list_from_file(filename):
    with open(filename, 'r') as f:
        return list(map(int, f.read().split()))

def save_keyfile(keyfile, dna_seq, round_keys):
    with open(keyfile, 'w') as f:
        json.dump({'dna': dna_seq, 'rounds': round_keys}, f)

def load_keyfile(keyfile):
    with open(keyfile, 'r') as f:
        data = json.load(f)
    return data['dna'], data['rounds']

# --- Main Encryption/Decryption Functions ---

def encrypt_file(input_file, output_file, key_file, n_rounds=5, dna_len=1000):
    with open(input_file, 'r') as f:
        text = f.read()

    dna_seq = generate_random_dna(dna_len)
    numeric_data = text_to_dna_numbers(text)
    encrypted, round_keys = encrypt(numeric_data, dna_seq, n_rounds)

    save_list_to_file(encrypted, output_file)
    save_keyfile(key_file, dna_seq, round_keys)
    print("Encryption completed.")

def decrypt_file(encrypted_file, key_file, output_file):
    encrypted = load_list_from_file(encrypted_file)
    dna_seq, round_keys = load_keyfile(key_file)

    decrypted_nums = decrypt(encrypted, dna_seq, round_keys)
    decrypted_text = dna_numbers_to_text(decrypted_nums)

    with open(output_file, 'w') as f:
        f.write(decrypted_text)
    print("Decryption completed.")

# --- Example Usage ---

if __name__ == "__main__":
    # Encrypt
    encrypt_file("input.txt", "encrypted.txt", "keyfile.json", n_rounds=5)

    # Decrypt
    decrypt_file("encrypted.txt", "keyfile.json", "decrypted.txt")
