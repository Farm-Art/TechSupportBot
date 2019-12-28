from config import markups, path_to_subjects
from img2pdf import convert
from PyPDF2 import PdfFileMerger
from zipfile import ZipFile
import comtypes.client
import os


comtypes.CoInitialize()


def access_error(update, context):
    update.message.reply_text('У вас недостаточно прав для '
                              'использования этой команды.')
    update.message.reply_text('Ну или вашей фамилии нет в базе данных, '
                              'В таком случае пропишите /start.',
                              reply_markup=markups['idle'])
    return 0


def access(admin=True):
    def wrapper(func):
        def result(update, context):
            if admin:
                if context.user_data['is_admin']:
                    return func(update, context)
                else:
                    return access_error(update, context)
            else:
                return func(update, context)
        return result
    return wrapper


def convert_from_docx(filename):
    newfilename = filename.split('.')[0] + '.pdf'
    wdFormatPDF = 17

    in_file = os.path.abspath(os.curdir) + '\\' + filename
    out_file = os.path.abspath(os.curdir) + '\\' + newfilename

    comtypes.CoInitialize()
    word = comtypes.client.CreateObject('Word.Application')
    doc = word.Documents.Open(in_file)
    doc.SaveAs(out_file, FileFormat=wdFormatPDF)
    doc.Close()
    word.Quit()
    os.remove(filename)
    return newfilename


def combine_files(*args, name):
    files = []
    merger = PdfFileMerger()
    for file in args:
        if file.endswith('.jpg') or file.endswith('.png'):
            oldfile = file
            img = convert((file,))
            file = file.split('.')[0] + '.pdf'
            with open(file, mode='wb') as output:
                output.write(img)
                output.close()
            os.remove(oldfile)
        elif file.endswith('.doc') or file.endswith('.docx'):
            file = convert_from_docx(file)
        files.append(open(file, mode='rb'))
        merger.append(file)
    with open(name + '.pdf', mode='wb') as file:
        merger.write(file)
        merger.close()
    for file in files:
        file.close()
    for file in files:
        try:
            os.remove(file.name)
        except Exception as ex:
            print("Failed to clean up after combining:", ex)
    return name + '.pdf'



