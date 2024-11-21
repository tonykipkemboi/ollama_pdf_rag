from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter

class DocumentManager:
    def __init__(self, directory_path, glob_pattern="./*.md"):
        self.directory_path = directory_path
        self.glob_pattern = glob_pattern
        self.documents = []
        self.all_sections = []
    
    def load_documents(self):
        loader = DirectoryLoader(self.directory_path, glob=self.glob_pattern, show_progress=True, loader_cls=UnstructuredMarkdownLoader)
        self.documents = loader.load()

    def split_documents(self):
        headers_to_split_on = [("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3"), ("####", "Header 4")]
        text_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        for doc in self.documents:
            sections = text_splitter.split_text(doc.page_content)
            self.all_sections.extend(sections)