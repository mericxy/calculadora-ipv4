def ip_to_binary(ip):
    return '.'.join([format(int(octet), '08b') for octet in ip.split('.')])


def mask_to_cidr(mask):
    binary_mask = ''.join([format(int(octet), '08b') for octet in mask.split('.')])
    return binary_mask.count('1')


def cidr_to_mask(cidr):
    mask = (0xffffffff >> (32 - cidr)) << (32 - cidr)
    return f"{(mask >> 24) & 0xff}.{(mask >> 16) & 0xff}.{(mask >> 8) & 0xff}.{mask & 0xff}"


def determine_class(ip):
    first_octet = int(ip.split('.')[0])
    if first_octet >= 0 and first_octet <= 127:
        return 'A'
    elif first_octet >= 128 and first_octet <= 191:
        return 'B'
    elif first_octet >= 192 and first_octet <= 223:
        return 'C'
    elif first_octet >= 224 and first_octet <= 239:
        return 'D'
    else:
        return 'E'


def default_mask(ip_class):
    if ip_class == 'A':
        return '255.0.0.0'
    elif ip_class == 'B':
        return '255.255.0.0'
    elif ip_class == 'C':
        return '255.255.255.0'
    else:
        return '0.0.0.0'


def subnets_and_hosts(cidr, ip_class):
    if ip_class == 'A':
        default_bits = 8
    elif ip_class == 'B':
        default_bits = 16
    elif ip_class == 'C':
        default_bits = 24
    else:
        return 0, 0  # Classes D e E não são usadas para sub-redes convencionais

    num_subnets = 2 ** (cidr - default_bits)
    num_hosts = 2 ** (32 - cidr) - 2
    return num_subnets, num_hosts


def calculate_subnets(ip, cidr):
    ip_parts = list(map(int, ip.split('.')))
    subnet_mask = cidr_to_mask(cidr)
    binary_subnet_mask = ''.join([format(int(octet), '08b') for octet in subnet_mask.split('.')])

    subnet_increment = 2 ** (32 - cidr)
    subnets = []

    for i in range(0, 2 ** (cidr % 8)):
        network_address = (ip_parts[0] << 24) + (ip_parts[1] << 16) + (ip_parts[2] << 8) + ip_parts[3]
        subnet = network_address + (i * subnet_increment)
        subnets.append(f"{(subnet >> 24) & 0xff}.{(subnet >> 16) & 0xff}.{(subnet >> 8) & 0xff}.{subnet & 0xff}")

    return subnets


def is_valid_ip(ip):
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit():
            return False
        if not 0 <= int(part) <= 255:
            return False
    return True


def is_special_ip(ip):
    first_octet = int(ip.split('.')[0])
    if first_octet == 10:
        return True  # Private network
    if first_octet == 127:
        return True  # Loopback
    if first_octet == 169 and int(ip.split('.')[1]) == 254:
        return True  # Link-local
    if first_octet == 172 and 16 <= int(ip.split('.')[1]) <= 31:
        return True  # Private network
    if first_octet == 192 and int(ip.split('.')[1]) == 168:
        return True  # Private network
    if 224 <= first_octet <= 239:
        return True  # Multicast
    if 240 <= first_octet <= 255:
        return True  # Reserved for future use
    return False


def is_network_or_broadcast_ip(ip, mask):
    ip_binary = ip_to_binary(ip).replace('.', '')
    mask_binary = ip_to_binary(mask).replace('.', '')
    network_address_binary = ''.join(['1' if mask_binary[i] == '1' else '0' for i in range(32)])
    broadcast_address_binary = ''.join(['1' if mask_binary[i] == '0' else '0' for i in range(32)])

    network_address = '.'.join([str(int(network_address_binary[i:i + 8], 2)) for i in range(0, 32, 8)])
    broadcast_address = '.'.join([str(int(broadcast_address_binary[i:i + 8], 2)) for i in range(0, 32, 8)])

    return ip == network_address or ip == broadcast_address


# Exemplo de uso
ip = input("Digite o endereço IP: ")

# Verificar se o IP é válido
if not is_valid_ip(ip):
    print("Endereço IP inválido. Por favor, digite um endereço IP válido.")
else:
    # Determinar a classe do endereço IP
    ip_class = determine_class(ip)

    # Calcular máscara de sub-rede padrão com base na classe do IP
    calculated_mask = default_mask(ip_class)

    # Calcular CIDR a partir da máscara de sub-rede
    cidr_suffix = mask_to_cidr(calculated_mask)

    # Verificar se o IP é um IP especial
    if is_special_ip(ip):
        print("Endereço IP reservado para uso especial. Por favor, digite um endereço IP válido.")
    # Verificar se o IP é um endereço de rede ou broadcast
    elif is_network_or_broadcast_ip(ip, calculated_mask):
        print("Endereço IP é um endereço de rede ou broadcast. Por favor, digite um endereço IP válido.")
    else:
        # Calcular quantidade de sub-redes e hosts por sub-rede
        num_subnets, num_hosts = subnets_and_hosts(cidr_suffix, ip_class)

        # Calcular sub-redes
        subnets = calculate_subnets(ip, cidr_suffix)

        # Calcular notação binária do IP e da máscara
        binary_ip = ip_to_binary(ip)
        binary_mask = ip_to_binary(calculated_mask)

        print(f"Endereço IP: {ip}")
        print(f"Máscara de Sub-rede: {calculated_mask}")
        print(f"CIDR Calculado: /{cidr_suffix}")
        print(f"Classe do IP: {ip_class}")
        print(f"Quantidade de Sub-redes: {num_subnets}")
        print(f"Quantidade de Hosts por Sub-rede: {num_hosts}")
        print(f"Notação Binária do IP: {binary_ip}")
        print(f"Notação Binária da Máscara: {binary_mask}")
        print("Sub-redes:")
        for subnet in subnets:
            print(subnet)
