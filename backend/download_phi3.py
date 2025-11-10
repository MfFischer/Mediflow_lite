"""
Download Phi-3 model from Hugging Face for offline AI support.
"""
import os
import urllib.request
from pathlib import Path

def download_file(url: str, destination: str):
    """Download file with progress bar."""
    print(f"Downloading from: {url}")
    print(f"Saving to: {destination}")
    
    def progress_hook(count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size)
        print(f"\rProgress: {percent}% ({count * block_size / (1024*1024):.1f} MB / {total_size / (1024*1024):.1f} MB)", end='')
    
    urllib.request.urlretrieve(url, destination, progress_hook)
    print("\n✅ Download complete!")

def main():
    # Phi-3 Mini 4K Instruct Q4 GGUF model
    model_url = "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf"
    
    # Destination path
    models_dir = Path(__file__).parent / "models"
    models_dir.mkdir(exist_ok=True)
    
    destination = models_dir / "phi-3-mini-4k-instruct-q4.gguf"
    
    if destination.exists():
        print(f"✅ Model already exists at: {destination}")
        print(f"   Size: {destination.stat().st_size / (1024*1024):.1f} MB")
        return
    
    print("🤖 Downloading Phi-3 Mini 4K Instruct Q4 GGUF model...")
    print("   This is a ~2.3 GB file, it may take a few minutes...")
    print()
    
    try:
        download_file(model_url, str(destination))
        print(f"\n✅ Model downloaded successfully!")
        print(f"   Location: {destination}")
        print(f"   Size: {destination.stat().st_size / (1024*1024):.1f} MB")
        print()
        print("🎉 You can now use offline AI mode in MediFlow!")
        print("   Toggle 'Use Local AI' in the AI Assistant page.")
    except Exception as e:
        print(f"\n❌ Error downloading model: {e}")
        print("\nAlternative: Download manually from:")
        print(f"   {model_url}")
        print(f"   Save to: {destination}")

if __name__ == "__main__":
    main()

