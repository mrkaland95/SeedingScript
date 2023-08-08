import base64
input_file = "../assets/images/seed.png"
output_file = "../assets/seed_data.pyw"


def main():
    with open(input_file, 'rb') as f:
        data = base64.b64encode(f.read())

    with open(output_file, 'wb') as f:
        f.write('data = b"""'.encode())
        f.write(data)
        f.write('"""'.encode())


if __name__ == '__main__':
    main()

