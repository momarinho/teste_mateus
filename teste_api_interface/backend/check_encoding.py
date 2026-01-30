import chardet

file_path = r"c:\Users\Transporte-02\Desktop\teste_mateus\teste_transformacao_validacao\operadoras_ativas.csv"

with open(file_path, 'rb') as f:
    rawdata = f.read(1000)
    result = chardet.detect(rawdata)
    print(f"Detected encoding: {result}")
