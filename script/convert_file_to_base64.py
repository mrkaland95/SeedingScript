import base64
input_file = "../assets/model_data/english_g2.pth"
output_file = "../assets/model_data_encoded/model_data.py"


def main():
    with open(input_file, 'rb') as f:
        data = base64.b64encode(f.read())

    with open(output_file, 'wb') as f:
        f.write('data = b"""'.encode())
        f.write(data)
        f.write('"""'.encode())


if __name__ == '__main__':
    main()

