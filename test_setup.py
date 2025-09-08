"""
Simple test to verify the project structure and imports
Run this to ensure everything is properly set up
"""

def test_imports():
    """Test that all main imports work correctly"""
    print("🧪 Testing imports...")
    
    try:
        # Test legacy imports (should work)
        from arxiv_docs.arxiv_api import search_and_download_arxiv_papers
        from arxiv_docs.clean_pdfs import parse_pdfs, save_chunks_todb
        print("✅ Legacy imports working")
        
        # Test new production imports
        from app.core.config import settings
        from app.models.schemas import PaperProcessRequest, ProcessingStatus
        from app.pipeline.state import create_initial_state
        print("✅ Production imports working")
        
        # Test main CLI
        from main import interactive_mode, start_api_server
        print("✅ Main CLI imports working")
        
        print("\n🎉 All imports successful! Project structure is clean and working.")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    return True


def test_configuration():
    """Test configuration loading"""
    print("🔧 Testing configuration...")
    
    try:
        from app.core.config import settings
        
        print(f"✅ App name: {settings.app_name}")
        print(f"✅ Environment: {settings.environment}")
        print(f"✅ Debug mode: {settings.debug}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 LaughGraph Project Verification")
    print("=" * 50)
    
    success = True
    success &= test_imports()
    success &= test_configuration()
    
    if success:
        print("\n✅ All tests passed! Your project is ready to use.")
        print("\nNext steps:")
        print("1. Set up your .env file with API keys")
        print("2. Run: python main.py interactive")
        print("3. Or run: python main.py api")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
