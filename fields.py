from os import remove
from re import match
from tempfile import NamedTemporaryFile
from subprocess import check_output
from fdfgen import forge_fdf

def get_fields(pdf_file):
'''
Uses pdftk to get a pdf's fields as a string, parses the string
and returns the fields as a list of lists, where the field name is
the first element in the list and its current value is the second
element
'''
    fields = {}
    call = ['pdftk', pdf_file, 'dump_data_fields']
    try:
        data_string = check_output(call).decode('utf8')
    except FileNotFoundError:
        raise PdftkNotInstalledError('Could not locate PDFtk installation')
    data_list = data_string.split('\r\n')
    if len(data_list) == 1:
        data_list = data_string.split('\n')
    for index, line in enumerate(data_list):
        if line:
            re_object = match(r'(\w+): (.+)', line)
            if re_object is not None:
                if re_object.group(1) == 'FieldName':
                    key = re_object.group(2)
                    fields[key] = ''
                elif re_object.group(1) == 'FieldValue':
                    fields[key] = re_object.group(2)
    return fields

def write_pdf(source, fields, output, flatten=False):
'''
Takes source file path, list of fdf fields, and output path, and
creates a filled-out pdf
'''
    fdf = forge_fdf(fdf_data_strings=fields)
    with NamedTemporaryFile(delete=False) as file:
        file.write(fdf)
    call = ['pdftk', source, 'fill_form', file.name, 'output', output]
    if flatten:
        call.append('flatten')
    try:
        check_output(call)
    except FileNotFoundError:
        raise PdftkNotInstalledError('Could not locate PDFtk installation')
    remove(file.name)
    
class PdftkNotInstalledError(Exception):
    pass
