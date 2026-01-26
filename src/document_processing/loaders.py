from docx import Document
from pypdf import PdfReader


def load_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def load_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file_object:
        return file_object.read()

def load_doc(file_path: str) -> str:
    document = Document(file_path)
    text = ""
    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"
    return text

#doc = load_doc(r"C:\Users\agata\Desktop\DataScienceProjects\PersonalKnowledgeAssistant\PersonalKnowledgeAssistant\data\documents\demo.docx")
#pdf = load_pdf(r"C:\Users\agata\Desktop\DataScienceProjects\PersonalKnowledgeAssistant\PersonalKnowledgeAssistant\data\documents\test_pdf.pdf")
txt = load_txt(r"C:\Users\agata\Desktop\DataScienceProjects\PersonalKnowledgeAssistant\PersonalKnowledgeAssistant\data\documents\test_txt.txt")

print(txt)