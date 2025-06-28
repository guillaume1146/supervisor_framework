"""
Script to remove old files that don't follow the new modular structure
"""

import os
import shutil


def remove_old_files():
    """Remove files that are no longer needed with the new structure"""
    
    files_to_remove = [
        # Old parameter file (replaced by individual phase parameter files)
        "workflow_system/models/parameters.py",
        
        # Old implementations file (replaced by individual phase implementation files)
        "workflow_system/workflows/implementations.py"
    ]
    
    print("🧹 Cleaning up old files that don't follow new modular structure...")
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            print(f"   ❌ Removing: {file_path}")
            os.remove(file_path)
        else:
            print(f"   ⚠️  File not found: {file_path}")
    
    print("✅ Cleanup completed!")


def verify_new_structure():
    """Verify the new modular structure is in place"""
    
    required_directories = [
        "workflow_system/phases",
        "workflow_system/phases/phase1_financial_input",
        "workflow_system/phases/report_generation", 
        "workflow_system/phases/data_processing",
        "workflow_system/utils"
    ]
    
    required_files = [
        "workflow_system/phases/__init__.py",
        "workflow_system/phases/phase1_financial_input/parameters.py",
        "workflow_system/phases/phase1_financial_input/implementation.py",
        "workflow_system/phases/phase1_financial_input/definition.py",
        "workflow_system/utils/__init__.py",
        "workflow_system/utils/validators.py",
        "workflow_system/utils/normalizers.py",
        "workflow_system/workflows/registry.py"
    ]
    
    print("🔍 Verifying new modular structure...")
    
    all_good = True
    
    for directory in required_directories:
        if os.path.exists(directory):
            print(f"   ✅ Directory exists: {directory}")
        else:
            print(f"   ❌ Directory missing: {directory}")
            all_good = False
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ File exists: {file_path}")
        else:
            print(f"   ❌ File missing: {file_path}")
            all_good = False
    
    if all_good:
        print("✅ New modular structure is properly set up!")
    else:
        print("❌ Some files/directories are missing. Please check the setup.")
    
    return all_good


if __name__ == "__main__":
    print("🏗️  Migrating to New Modular Structure")
    print("=" * 50)
    
    # Verify new structure first
    if verify_new_structure():
        # Remove old files
        remove_old_files()
        print("\n🎉 Migration to modular structure completed!")
        print("\nNext steps:")
        print("1. Test with: python test_phase1_workflow.py")
        print("2. Start API: python main_fastapi.py")
        print("3. Test endpoints in Postman")
    else:
        print("\n⚠️  Please set up the new modular structure first before running cleanup.")
