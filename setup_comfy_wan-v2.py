import os
import subprocess
import urllib.request
import sys
import shutil

BASE_DIR = os.path.abspath(os.path.curdir)
MODELS_DIR = os.path.join(BASE_DIR, "models")
CUSTOM_NODES_DIR = os.path.join(BASE_DIR, "custom_nodes")

CUSTOM_NODES = {
    "ComfyUI-KJNodes": "https://github.com/kijai/ComfyUI-KJNodes.git",
    "ComfyUI-VideoHelperSuite": "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git",
    "ComfyUI-WanVideoWrapper": "https://github.com/kijai/ComfyUI-WanVideoWrapper.git",
    "cg-use-everywhere": "https://github.com/chrisgoringe/cg-use-everywhere.git",
}

MODELS = [
    {
        "name": "LongCat Distill LoRA",
        "url": "https://huggingface.co/Kijai/LongCat-Video_comfy/resolve/main/LongCat_distill_lora_alpha64_bf16.safetensors?download=true",
        "primary_path": os.path.join(MODELS_DIR, "loras", "longcat", "LongCat_distill_lora_alpha64_bf16.safetensors"),
        "extra_paths": []
    },
    {
        "name": "LongCat Diffusion Model",
        "url": "https://huggingface.co/Kijai/LongCat-Video_comfy/resolve/main/LongCat_TI2V_comfy_fp8_e4m3fn_scaled_KJ.safetensors?download=true",
        "primary_path": os.path.join(MODELS_DIR, "diffusion_models", "longcat", "LongCat_TI2V_comfy_fp8_e4m3fn_scaled_KJ.safetensors"),
        "extra_paths": [
            os.path.join(MODELS_DIR, "checkpoints", "longcat", "LongCat_TI2V_comfy_fp8_e4m3fn_scaled_KJ.safetensors"),
            os.path.join(MODELS_DIR, "unet", "longcat", "LongCat_TI2V_comfy_fp8_e4m3fn_scaled_KJ.safetensors")
        ]
    },
    {
        "name": "Wan 2.1 VAE",
        "url": "https://huggingface.co/Comfy-Org/Wan-2.1/resolve/main/split_files/vae/wan_2.1_vae.safetensors?download=true",
        "primary_path": os.path.join(MODELS_DIR, "vae", "wan_2.1_vae.safetensors"),
        "extra_paths": []
    },
    {
        "name": "UMT5 Text Encoder",
        "url": "https://huggingface.co/Kijai/WanVideo_comfy/resolve/f0f34caa22112219807f593be7bfd7d9ebe32090/umt5-xxl-enc-bf16.safetensors?download=true",
        "primary_path": os.path.join(MODELS_DIR, "text_encoders", "wan2.2", "umt5-xxl-enc-bf16.safetensors"),
        "extra_paths": [
            os.path.join(MODELS_DIR, "clip", "wan2.2", "umt5-xxl-enc-bf16.safetensors")
        ]
    }
]

def create_link_or_copy(src, dst):
    """Creates symlink or copies file to fallback locations for maximum node compatibility."""
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst):
        return
    try:
        os.symlink(src, dst)
        print(f"   ↳ Created symlink -> {dst}")
    except (OSError, AttributeError):
        try:
            shutil.copyfile(src, dst)
            print(f"   ↳ Copied fallback file -> {dst}")
        except Exception as e:
            print(f"   ↳ Could not link/copy to {dst}: {e}")

def download_file(name, url, primary_path, extra_paths):
    os.makedirs(os.path.dirname(primary_path), exist_ok=True)
    if os.path.exists(primary_path) and os.path.getsize(primary_path) > 0:
        print(f"[EXISTS] {name} present at: {primary_path}")
    else:
        print(f"[DOWNLOADING] {name} ...")
        try:
            def report_hook(block_num, block_size, total_size):
                downloaded = block_num * block_size
                if total_size > 0:
                    percent = min(100, (downloaded / total_size) * 100)
                    sys.stdout.write(f"\r progress: {percent:.1f}% ({downloaded // (1024*1024)}MB / {total_size // (1024*1024)}MB)")
                    sys.stdout.flush()

            urllib.request.urlretrieve(url, primary_path, reporthook=report_hook)
            print(f"\n[DONE] Downloaded {name}")
        except Exception as e:
            print(f"\n[ERROR] Download failed for {name}: {e}")
            return

    for extra in extra_paths:
        create_link_or_copy(primary_path, extra)

def setup_custom_nodes():
    os.makedirs(CUSTOM_NODES_DIR, exist_ok=True)
    for repo_name, repo_url in CUSTOM_NODES.items():
        target_dir = os.path.join(CUSTOM_NODES_DIR, repo_name)
        if os.path.exists(target_dir):
            print(f"[EXISTS] Custom node '{repo_name}' present.")
        else:
            print(f"[CLONING] {repo_name}...")
            try:
                subprocess.run(["git", "clone", repo_url, target_dir], check=True)
                print(f"[DONE] Cloned {repo_name}\n")
            except Exception as e:
                print(f"[ERROR] Could not clone {repo_name}: {e}\n")

def main():
    print("=========================================================")
    print("  ComfyUI Wan2.1 & LongCat Workflow Setup (v2 Updated)")
    print("=========================================================\n")
    
    if not os.path.exists("models") and not os.path.exists("main.py"):
        print("[WARNING] 'models' directory not found in current directory.")
        print("Run this script from the root of your ComfyUI installation folder.\n")
    
    print("1. Installing / Updating Custom Nodes...")
    setup_custom_nodes()
    
    print("\n2. Downloading & Linking Model Weights...")
    for model in MODELS:
        download_file(model["name"], model["url"], model["primary_path"], model["extra_paths"])

    print("\n=========================================================")
    print("  Setup v2 Complete!")
    print("  - Text encoder auto-mirrored to models/clip/ & models/text_encoders/")
    print("  - Diffusion model auto-mirrored to models/diffusion_models/ & models/checkpoints/")
    print("  1. Restart ComfyUI server.")
    print("  2. Refresh browser (F5).")
    print("=========================================================")

if __name__ == "__main__":
    main()
