import os
import sys
from huggingface_hub import HfApi

def upload_to_hf(token):
    api = HfApi()
    
    repo_id = "fathima-ai01/contract-simplifier"
    folder_path = "." # current directory
    
    print(f"Uploading files to Hugging Face Space: {repo_id}...")
    
    try:
        api.upload_folder(
            folder_path=folder_path,
            repo_id=repo_id,
            repo_type="space",
            token=token,
            ignore_patterns=[".git/*", ".env", "myenv/*", "__pycache__/*", ".vscode/*"],
            commit_message="Upload complete Contract Language Simplifier project"
        )
        print("\n✅ Upload complete! Your space should now be updating with the latest files.")
    except Exception as e:
        print(f"\n❌ Error during upload: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python upload_to_hf.py <YOUR_HUGGINGFACE_WRITE_TOKEN>")
        sys.exit(1)
        
    upload_to_hf(sys.argv[1])
