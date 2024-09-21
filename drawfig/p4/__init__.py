def main(kwargs):
    label = kwargs['label']
    if label == 'iv_cv':
        from . import draw_iv_cv_paper4
        draw_iv_cv_paper4.main()
    elif label == 'extract_waveform':
        from . import extract_waveform
        extract_waveform.main()
    elif label == 'field_comparison':
        from . import field_comparison
        field_comparison.main()
    elif label == 'ana':
        from . import tct_analysis
        tct_analysis.main()