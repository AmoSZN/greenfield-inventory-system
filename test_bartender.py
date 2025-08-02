import win32com.client
import os

print("Testing BarTender automation...")

try:
    # Check if BarTender is installed
    btapp = win32com.client.Dispatch("BarTender.Application")
    print("✓ BarTender COM object created successfully")
    
    # Check if template exists
    template_path = "C:/BarTenderIntegration/Templates/PackingList.btw"
    if os.path.exists(template_path):
        print(f"✓ Template found: {template_path}")
    else:
        print(f"✗ Template NOT found: {template_path}")
    
    # Try to open the template
    format_doc = btapp.Formats.Open(template_path, False, "")
    print("✓ Template opened successfully")
    
    # Close without printing
    format_doc.Close(2)  # 2 = Don't save changes
    btapp.Quit(2)
    print("✓ BarTender automation test successful!")
    
except Exception as e:
    print(f"✗ Error: {str(e)}")
