import pathlib
import shutil

def clean(args, conf):

    print("Cleaning site output directory...")
    site_dir = pathlib.Path('.') / conf['DIR_PUBLISH']
    if site_dir.exists():
        shutil.rmtree(site_dir)
    site_dir.mkdir()
    post_store_path = pathlib.Path('.') / conf['POST_STORE']
    post_store_path.unlink(missing_ok=True)
