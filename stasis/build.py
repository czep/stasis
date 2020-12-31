from .site import Site

def build(args, conf):
    print("Building site...")
    print("Target is: {}.  Drafts: {}".format(args.target, args.drafts))
    site = Site(args, conf)
    site.build()
