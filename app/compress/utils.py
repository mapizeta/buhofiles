import zipfile
import os
#import py7zr
import tarfile

def compress_files(file_paths, compression_level='ZIP_DEFLATED'): #compression_method='zip'
    """
    Comprime los archivos en el formato especificado.

    :param file_paths: Lista de rutas a los archivos a comprimir.
    :param compression_method: Método de compresión ('zip', '7z', 'tar').
    :return: Ruta del archivo comprimido.
    """
    """
    Comprime los archivos con un nivel de compresión especificado.

    :param file_paths: Lista de rutas a los archivos a comprimir.
    :param compression_level: Nivel de compresión (ZIP_STORED, ZIP_DEFLATED).
    :return: Ruta del archivo comprimido.
    """
    # Convertir el nivel de compresión a la constante correspondiente
    compression_map = {
        'ZIP_STORED': zipfile.ZIP_STORED,
        'ZIP_DEFLATED': zipfile.ZIP_DEFLATED,
    }
    compression = compression_map.get(compression_level, zipfile.ZIP_DEFLATED)

    compressed_file_path = 'app/static/uploads/compressed_files.zip'
    with zipfile.ZipFile(compressed_file_path, 'w', compression=compression) as zipf:
        for file in file_paths:
            zipf.write(file, os.path.basename(file))

    # Opcional: Eliminar los archivos temporales después de comprimir
    for file in file_paths:
        os.remove(file)

    return compressed_file_path

    # Determinar el nombre del archivo comprimido según el método
    #compressed_file_path = f'app/static/uploads/compressed_files.{compression_method}'

    #if compression_method == 'zip':
    #    with zipfile.ZipFile(compressed_file_path, 'w') as zipf:
    #        for file in file_paths:
    #            zipf.write(file, os.path.basename(file))
    #elif compression_method == '7z':
    #    with py7zr.SevenZipFile(compressed_file_path, 'w') as archive:
    #        for file in file_paths:
    #            archive.write(file, os.path.basename(file))
    #elif compression_method == 'tar':
    #    with tarfile.open(compressed_file_path, 'w') as tar:
    #        for file in file_paths:
    #            tar.add(file, arcname=os.path.basename(file))
    #else:
    #    raise ValueError(f"Método de compresión no soportado: {compression_method}")

    # Opcional: Eliminar los archivos temporales después de comprimir
    #for file in file_paths:
    #    os.remove(file)

    #return compressed_file_path

