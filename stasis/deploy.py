from .s3 import S3

def deploy(args, conf):
    msg_suffix = ""
    if args.dry_run:
        msg_suffix = "  DRY RUN"
    print("Deploying site...", msg_suffix)
    s3 = S3(args, conf)
    s3.deploy()

