"""
A simple script to verify that key dependencies are correctly installed.
"""

def check_imports():
    """Test importing key libraries."""
    print("Checking imports...")
    
    try:
        import openai
        print("✅ OpenAI")
    except ImportError as e:
        print(f"❌ OpenAI: {e}")
    
    try:
        import yaml
        print("✅ PyYAML")
    except ImportError as e:
        print(f"❌ PyYAML: {e}")
    
    try:
        import langchain
        print("✅ LangChain")
    except ImportError as e:
        print(f"❌ LangChain: {e}")
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv")
    except ImportError as e:
        print(f"❌ python-dotenv: {e}")
    
    try:
        import pymupdf
        print("✅ PyMuPDF")
        
        # Try importing fitz from pymupdf
        try:
            import pymupdf.fitz as fitz
            print("✅ pymupdf.fitz")
        except ImportError:
            try:
                # Alternative import method
                import fitz
                print("✅ fitz")
            except ImportError as e:
                print(f"❌ fitz: {e}")
                
    except ImportError as e:
        print(f"❌ PyMuPDF: {e}")
    
    print("\nImport check complete!")

if __name__ == "__main__":
    check_imports() 