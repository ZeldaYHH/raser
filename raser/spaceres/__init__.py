from . import pixeldetector_telescope
def main(args):
    label = vars(args)['label']

    if label == 'pixeldetector_telescope':
        pixeldetector_telescope.main()
    else:
        raise NameError(label)