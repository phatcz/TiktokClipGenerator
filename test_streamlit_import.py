"""
Quick test to check if importing app_streamlit.py causes I/O errors
"""
import sys
import io

print("Testing app_streamlit.py import...")
print("-" * 50)

try:
    # Try to import the streamlit app module
    import app_streamlit
    print("✓ Import successful - no I/O errors during import")
except Exception as e:
    error_type = type(e).__name__
    error_msg = str(e)
    print(f"✗ Import failed with {error_type}: {error_msg}")
    
    # Check specifically for I/O related errors
    if "closed file" in error_msg.lower() or "i/o operation" in error_msg.lower():
        print("\n⚠ I/O ERROR DETECTED - This matches the reported issue!")
        print(f"   Error details: {error_type}: {error_msg}")
    else:
        print(f"\n   This is a different error (not the I/O closed file issue)")

print("-" * 50)
print("Test complete.")

