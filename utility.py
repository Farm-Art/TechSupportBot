from config import path_to_subjects_folder, path_to_subjects, subjects
from img2pdf import convert
from PyPDF2 import PdfFileMerger
from zipfile import ZipFile
import comtypes.client
import shutil
import tempfile
import os

comtypes.CoInitialize()


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


def add_to_archive(*files, subject, surname):
    files = list(files)
    if len(files) == 1:
        filename = surname + '.' + files[0].split('.')[1]
        os.rename(files[0], filename)
        files[0] = filename
    else:
        with ZipFile(surname + '.zip', mode='a') as temp:
            for file in files:
                temp.write(file)
            temp.close()
        filename = surname + '.zip'
    if check_for_copies(path_to_subjects_folder + subject + '.zip', filename):
        remove_from_zip(path_to_subjects_folder + subject + '.zip', filename)
    with ZipFile(path_to_subjects_folder + subject + '.zip', mode='a') as archive:
        archive.write(filename)
        archive.close()
    for file in files:
        os.remove(file)
    if len(files) > 1:
        os.remove(filename)
    print(subjects.keys())
    if not any(surname in names for names in subjects.values()):
        subjects[subject].append(surname)
        with open(path_to_subjects, mode='w', encoding='utf-8') as file:
            for subject, students in subjects.items():
                print(subject, *students, file=file)


def check_for_copies(archive, filename):
    try:
        with ZipFile(archive) as data:
            for file in data.filelist:
                if file.filename == filename:
                    return True
        return False
    except FileNotFoundError:
        return False


def remove_from_zip(zipfname, *filenames):
    tempdir = tempfile.mkdtemp()
    try:
        tempname = os.path.join(tempdir, 'new.zip')
        with ZipFile(zipfname, 'r') as zipread:
            with ZipFile(tempname, 'w') as zipwrite:
                for item in zipread.infolist():
                    if item.filename not in filenames:
                        data = zipread.read(item.filename)
                        zipwrite.writestr(item, data)
        shutil.move(tempname, zipfname)
    finally:
        shutil.rmtree(tempdir)


class Generator:
    curr = 0
    step = 1

    @classmethod
    def __getitem__(cls, item):
        for _ in range(item):
            yield cls.curr
            cls.curr += cls.step


class Feature:
    gen = Generator()

    def __init__(self):
        self.handlers = []
        self.states = []
        self.markups = {}

    def __getitem__(self, item):
        return self.handlers[item]

    def keys(self):
        return self.states

