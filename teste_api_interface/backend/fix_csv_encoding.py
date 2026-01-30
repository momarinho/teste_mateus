import os

file_path = r"c:\Users\Transporte-02\Desktop\teste_mateus\teste_transformacao_validacao\operadoras_ativas.csv"
backup_path = file_path + ".bak"

try:
    if not os.path.exists(backup_path):
        import shutil
        shutil.copy2(file_path, backup_path)
        print(f"Backup created at {backup_path}")

    with open(file_path, 'rb') as f:
        content = f.read()

    # Apply fix: UTF-8 bytes -> String (garbled) -> Latin-1 bytes (original UTF-8 bytes) -> String (correct)
    # But wait.
    # content is bytes: b'... BENEF\xc3\x83\xc2\x8dCIOS ...'
    # content.decode('utf-8') -> "BENEFÃ CIOS" (where space is \x8d)
    # .encode('latin-1') -> b'... BENEF\xc3\x8dCIOS ...' (which is UTF-8 for BENEFÍCIOS)
    
    fixed_content = content.decode('utf-8').encode('latin-1')
    
    # Write back as binary (because it is now valid UTF-8 bytes)
    with open(file_path, 'wb') as f:
        f.write(fixed_content)
        
    print("File encoding fixed successfully.")
    
except Exception as e:
    print(f"Error fixing file: {e}")
