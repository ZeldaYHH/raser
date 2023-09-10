from . import gen_devsim_db
def main(args):
    label = vars(args)['label']

    if label == 'gen_devsim_db':
        gen_devsim_db.main()
    else:
        raise NameError(label)