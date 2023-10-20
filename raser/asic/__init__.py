

def main(args):
    label = vars(args)['label']
        
    if label == 'regincr':
        from . import regincr
        regincr.main()
    else:
        raise NameError(label)
    