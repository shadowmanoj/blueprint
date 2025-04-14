"""File reading utilities for handling different document formats."""

import os
import io
import mimetypes


def get_file_type(file_path):
    """Determine the file type based on extension or content.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: File type ('pdf', 'docx', 'txt', etc.)
    """
    # Get file extension from path
    _, ext = os.path.splitext(file_path)
    if ext:
        return ext.lower()[1:]  # Remove the dot
    
    # Try to determine mime type
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        if mime_type == 'application/pdf':
            return 'pdf'
        elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            return 'docx'
        elif mime_type.startswith('text/'):
            return 'txt'
    
    # Default to unknown
    return 'unknown'


def read_file(file_path):
    """Read a file and return its contents.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: File contents as text
    """
    file_type = get_file_type(file_path)
    
    if file_type == 'pdf':
        return read_pdf(file_path)
    elif file_type == 'docx':
        return read_docx(file_path)
    elif file_type in ['txt', 'md', 'json', 'yaml', 'yml']:
        return read_text(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def read_pdf(file_path):
    """Read a PDF file and extract text.
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from PDF
    """
    try:
        # Try to use PyMuPDF (fitz) if available
        import fitz
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except ImportError:
        # Fallback to use PyPDF2 if fitz is not available
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfFileReader(file)
                text = ""
                for page_num in range(reader.numPages):
                    text += reader.getPage(page_num).extractText()
                return text
        except ImportError:
            raise ImportError("Neither PyMuPDF nor PyPDF2 is installed. Install one of them to read PDF files.")


def read_docx(file_path):
    """Read a DOCX file and extract text.
    
    Args:
        file_path (str): Path to the DOCX file
        
    Returns:
        str: Extracted text from DOCX
    """
    try:
        import docx
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except ImportError:
        raise ImportError("python-docx is not installed. Install it to read DOCX files.")


def read_text(file_path):
    """Read a text file and return its content.
    
    Args:
        file_path (str): Path to the text file
        
    Returns:
        str: File content as text
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read() 