from bitarray import bitarray
import math
class LZWCompression:
    def __init__(self, data):
        self.data = data
        self.dictionary = {chr(i): i for i in range(256)}
        self.max_code = 255
        self.bits_per_code = self.calculate_bits_per_code()

    def calculate_bits_per_code(self):
        return max(8, int(math.ceil(math.log2(self.max_code + 1))))

    def compress(self):
        compressed_data = bitarray()

        current_code = self.data[0]
        for symbol in self.data[1:]:
            current_code += symbol
            if current_code not in self.dictionary:
                compressed_data.extend(format(self.dictionary[current_code[:-1]], f'0{self.bits_per_code}b'))
                self.max_code += 1
                self.dictionary[current_code] = self.max_code
                current_code = symbol

        compressed_data.extend(format(self.dictionary[current_code], f'0{self.bits_per_code}b'))

        return compressed_data

    def decompress(self, compressed_data):
        decompressed_data = ""
        reverse_dictionary = {v: k for k, v in self.dictionary.items()}

        current_code = int(compressed_data[:self.bits_per_code].to01(), 2)
        decompressed_data += reverse_dictionary.get(current_code, '')

        for i in range(self.bits_per_code, len(compressed_data), self.bits_per_code):
            current_code = int(compressed_data[i:i + self.bits_per_code].to01(), 2)

            if current_code in reverse_dictionary:
                sequence = reverse_dictionary[current_code]
            elif current_code == len(reverse_dictionary):
                sequence = reverse_dictionary[len(reverse_dictionary)] + reverse_dictionary[current_code][0]
            else:
                raise ValueError("Invalid compressed data.")

            decompressed_data += sequence
            reverse_dictionary[len(reverse_dictionary)] = reverse_dictionary[current_code] + sequence[0]

        return decompressed_data


# Ejemplo de uso:
original_data = "ABABABABA"
lzw = LZWCompression(original_data)
compressed_data = lzw.compress()
decompressed_data = lzw.decompress(compressed_data)

print("Original Data:", original_data)
print("Compressed Data:", compressed_data)
print("Decompressed Data:", decompressed_data)
