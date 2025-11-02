import random
import math

BITS = 16
SIGNED_MAX = 2 ** (BITS - 1) - 1
SIGNED_MIN = -(2 ** (BITS - 1))

def to_binary(n, bits=BITS):
    if n < 0:
        return "ERROR_NEG"
    return bin(n)[2:].zfill(bits)


def to_one_complement(n, bits=BITS):
    if n >= 0:
        if n > 2 ** (bits - 1) - 1:
            return "OVERFLOW_POS"
        return "0" + to_binary(n, bits=bits - 1)
    else:
        magnitude = abs(n)
        if magnitude > 2 ** (bits - 1) - 1:
            return "OVERFLOW_NEG"
        standard_bin = to_binary(magnitude, bits=bits - 1)
        inverted = ''.join('1' if b == '0' else '0' for b in standard_bin)
        return "1" + inverted


def to_two_complement(n, bits=BITS):
    if n > 2 ** (bits - 1) - 1:
        return "OVERFLOW_POS"
    if n < -(2 ** (bits - 1)):
        return "OVERFLOW_NEG"
    return bin(n & (2 ** bits - 1))[2:].zfill(bits)


def bias_binary_conversion(n, bits=BITS):
    K = (2 ** (bits - 1)) - 1
    biased = n + K
    if biased < 0 or biased > (2 ** bits - 1):
        return "BIAS_RANGE_ERROR"
    return to_binary(biased, bits)

def _frac_to_bin(f: float, precision: int = 30) -> str:
    binary_str = ""
    while f > 0 and len(binary_str) < precision:
        f *= 2
        bit = math.floor(f)
        binary_str += str(int(bit))
        f -= bit
    return binary_str

def to_IEEE_float_point(n: float) -> str:
    if n == 0.0:
        return '0' * 32
    sign = '1' if n < 0 else '0'
    abs_n = abs(n)
    _int = int(math.floor(abs_n))
    _frac = abs_n - _int
    bin_int = bin(_int)[2:]
    bin_frac = _frac_to_bin(_frac, 30)
    if abs_n >= 1.0:
        E = len(bin_int) - 1
        mantissa_source = bin_int[1:] + bin_frac
    else:
        try:
            first_one_index = bin_frac.index('1')
            E = -(first_one_index + 1)
            mantissa_source = bin_frac[first_one_index + 1:]
            
        except ValueError:
            return '0' * 32 
    BIAS = 127
    exponent_val = E + BIAS
    if exponent_val >= 255:
         return f"OVERFLOW_INF"
    if exponent_val <= 0:
        return f"UNDERFLOW_ZERO"
    exponent = bin(exponent_val)[2:].zfill(8)
    mantissa = (mantissa_source + '0' * 23)[:23]
    result = sign + exponent + mantissa
    return result

def generate_IEEE_question():
    x = round(random.uniform(-10.0, 10.0), 5)
    ans = to_IEEE_float_point(x) 
    return f"What is the IEEE binary value of {x}?", ans

def generate_power_of_two_question():
    k = random.randint(5, 16)
    return f"What is the value of 2^{k}?", str(2 ** k)


def generate_conversion_question():
    n = random.randint(SIGNED_MIN // 8, SIGNED_MAX // 8)
    sit = random.randint(1, 3)
    bits = BITS

    if sit == 1:
        q = f"Show the 1's Complement of {n} with {bits} bits:"
        ans = to_one_complement(n, bits)
    elif sit == 2:
        q = f"Show the 2's Complement of {n} with {bits} bits:"
        ans = to_two_complement(n, bits)
    else:
        K = (2 ** (bits - 1)) - 1
        max_n = (2 ** bits - 1) - K
        min_n = 0 - K
        n = random.randint(min_n, max_n)
        q = f"Show the Bias ({K}) Binary Conversion of {n} with {bits} bits:"
        ans = bias_binary_conversion(n, bits)
    return q, ans, bits
