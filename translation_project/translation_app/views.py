# translation_app/views.py
from translation_project import settings
from .forms import FileUploadForm

import os
import pandas as pd

from django.shortcuts import render, redirect
from django.http import FileResponse
from django.conf import settings
from .models import UploadedFile
from openpyxl import Workbook
import concurrent.futures
from ai4bharat.transliteration import XlitEngine

# Initialize the XlitEngine
e = XlitEngine(beam_width=10, src_script_type="indic")

target_language = 'en'
source_language = 'mr'

# Create a cache dictionary to store translations
translation_cache = {}

def translate_text(text):
    if isinstance(text, str) and text.strip():  
        if text in translation_cache:
            return translation_cache[text]
        else:
            translation = e.translit_sentence(text, 'mr')
            translation_cache[text] = translation  # Cache the translation
            return translation
    else:
        return text

def translate_file(request):
    if request.method == 'POST':
        file_id = request.POST.get('file_id')
        if file_id:
            uploaded_file = UploadedFile.objects.get(id=file_id)
            excel_file_path = uploaded_file.file.path
            xls = pd.ExcelFile(excel_file_path)
            sheet_names = xls.sheet_names

            for sheet_name in sheet_names:
                df = pd.read_excel(excel_file_path, sheet_name=sheet_name, header=None)
                columns = pd.read_excel(excel_file_path, sheet_name=sheet_name, header=None, nrows=1).iloc[0].tolist()
                columns_to_translate = list(range(len(columns)))

                with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                    for column_name in columns_to_translate:
                        batch_size = 100
                        translated_data = []
                        batch = df[column_name].tolist()
                        for i in range(0, len(batch), batch_size):
                            translated_batch = list(executor.map(translate_text, batch[i:i + batch_size]))
                            translated_data.extend(translated_batch)
                        df[f'Translated_{column_name}'] = translated_data

                df.drop(columns=columns_to_translate, axis=1, inplace=True)
                output_file_path = os.path.join(settings.MEDIA_ROOT, 'translated_files', 'lib_excel.xlsx')
                
                df.to_excel(output_file_path, index=False)

            # Provide a download link for the translated file
            translated_file = open(output_file_path, 'rb')
            response = FileResponse(translated_file)
            response['Content-Disposition'] = 'attachment; filename="translated_file.xlsx"'
            return response

    return redirect('upload')




def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save()
            return redirect('confirmation', uploaded_file.id)
    else:
        form = FileUploadForm()
    return render(request, 'upload_file.html', {'form': form})



def confirmation(request, file_id):
    uploaded_file = UploadedFile.objects.get(id=file_id)
    return render(request, 'confirmation.html', {'uploaded_file': uploaded_file})
