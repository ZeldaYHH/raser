#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@Description: Signal re-formation for events of great amount
@Date       : 2025/04/09 15:24:27
@Author     : Chenxi Fu
@version    : 1.0
'''

import ROOT

from current.cross_talk import cross_talk
from afe.readout import Amplifier

def main(amp_name, file_name):
    f = ROOT.TFile(file_name)
    tree = f.Get("tree")  # 假设 TTree 名字为 "tree"
    cross_talk_tree = ROOT.TTree("tree", "cross talk tree")
    amplified_tree = ROOT.TTree("tree", "amplified tree")

    n_entries = tree.GetEntries()
    for i in range(n_entries):
        tree.GetEntry(i)
        cu = tree.data

        cross_talk_cu = cross_talk(cu)
        save_signal_TTree(cross_talk_tree, cross_talk_cu)
        amplified_cu = Amplifier(cross_talk_cu, amp_name, seed=i)
        save_signal_TTree(amplified_tree, amplified_cu)

    cross_talk_file_name = file_name.replace("signal_cu", "signal_ct")
    cross_talk_file = ROOT.TFile(cross_talk_file_name, "RECREATE")
    cross_talk_tree.Write()
    cross_talk_file.Close()

    amplified_file_name = file_name.replace("signal_cu", "signal_amp")
    amplified_file = ROOT.TFile(amplified_file_name, "RECREATE")
    amplified_tree.Write()
    amplified_file.Close()

    f.Close()




    