import os
import subprocess
import urllib.request
import sys

# Base directory assumptions (run script from root of ComfyUI directory)
BASE_DIR = os.path.abspath(os.path.curdir)
MODELS_DIR = os.path.join(BASE_DIR, "models")
CUSTOM_NODES_DIR = os.path.join(BASE_DIR, "custom_nodes")

# Custom Nodes to clone
CUSTOM_NODES = {
    "ComfyUI-KJNodes": "https://github.com/kijai/ComfyUI-KJNodes.git",
    "ComfyUI-VideoHelperSuite": "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git",
    "ComfyUI-WanVideoWrapper": "https://github.com/kijai/ComfyUI-WanVideoWrapper.git",
}

# Models to download with exact folder placement
MODELS = [
    {
        "name": "LongCat Distill LoRA",
        "url": "https://huggingface.co/Kijai/LongCat-Video_comfy/resolve/main/LongCat_distill_lora_alpha64_bf16.safetensors?download=true",
        "path": os.path.join(MODELS_DIR, "loras", "longcat", "LongCat_distill_lora_alpha64_bf16.safetensors")
    },
    {
        "name": "LongCat Diffusion Model",
        "url": "https://huggingface.co/Kijai/LongCat-Video_comfy/resolve/main/LongCat_TI2V_comfy_fp8_e4m3fn_scaled_KJ.safetensors?download=true",
        "path": os.path.join(MODELS_DIR, "diffusion_models", "longcat", "LongCat_TI2V_comfy_fp8_e4m3fn_scaled_KJ.safetensors")
    },
    {
        "name": "Wan 2.1 VAE",
        "url": "https://huggingface.co/Comfy-Org/Wan-2.1/resolve/main/split_files/vae/wan_2.1_vae.safetensors?download=true",
        "path": os.path.join(MODELS_DIR, "vae", "wan_2.1_vae.safetensors")
    },
    {
        "name": "UMT5 Text Encoder",
        "url": "https://huggingface.co/Kijai/WanVideo_comfy/resolve/f0f34caa22112219807f593be7bfd7d9ebe32090/umt5-xxl-enc-bf16.safetensors?download=true",
        "path": os.path.join(MODELS_DIR, "text_encoders", "wan2.2", "umt5-xxl-enc-bf16.safetensors")
    }
]

def download_file(name, url, target_path):
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    if os.path.exists(target_path) and os.path.getsize(target_path) > 0:
        print(f"[EXISTS] {name} already present at: {target_path}")
        return

    print(f"[DOWNLOADING] {name} -> {target_path} ...")
    try:
        # Download with progress indicator
        def report_hook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, (downloaded / total_size) * 100)
                sys.stdout.write(f"\r progress: {percent:.1f}% ({downloaded // (1024*1024)}MB / {total_size // (1024*1024)}MB)")
                sys.stdout.flush()

        urllib.request.urlretrieve(url, target_path, reporthook=report_hook)
        print(f"\n[DONE] Successfully downloaded {name}\n")
    except Exception as e:
        print(f"\n[ERROR] Failed to download {name}: {e}\n")

def setup_custom_nodes():
    os.makedirs(CUSTOM_NODES_DIR, exist_ok=True)
    for repo_name, repo_url in CUSTOM_NODES.items():
        target_dir = os.path.join(CUSTOM_NODES_DIR, repo_name)
        if os.path.exists(target_dir):
            print(f"[EXISTS] Custom node '{repo_name}' already present.")
        else:
            print(f"[CLONING] {repo_name} from {repo_url}...")
            try:
                subprocess.run(["git", "clone", repo_url, target_dir], check=True)
                print(f"[DONE] Cloned {repo_name}\n")
            except Exception as e:
                print(f"[ERROR] Could not clone {repo_name}: {e}\n")

def main():
    print("=========================================================")
    print("  ComfyUI Wan2.1 & LongCat Workflow Automated Setup Script")
    print("=========================================================\n")
    
    # Check if running in ComfyUI directory
    if not os.path.exists("models") and not os.path.exists("main.py"):
        print("[WARNING] 'models' directory not found in current folder.")
        print("Please make sure to run this script inside your main 'ComfyUI/' root directory.\n")
    
    print("1. Installing Custom Nodes...")
    setup_custom_nodes()
    
    print("\n2. Downloading Models & Weights...")
    for model in MODELS:
        download_file(model["name"], model["url"], model["path"])

    print("\n=========================================================")
    print("  Setup Complete!")
    print("  Next steps:")
    print("  1. Restart your ComfyUI server.")
    print("  2. Refresh the browser UI (F5).")
    print("=========================================================")

if __name__ == "__main__":
    main()
