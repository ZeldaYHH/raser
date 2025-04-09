import ROOT

def cross_talk(cu):
    read_ele_num = len(cu)
    cross_talk_cu = []
    for i in range(read_ele_num):
        cross_talk_cu.append(ROOT.TH1F("cross_talk"+str(i+1),"Cross Talked Current"+" No."+str(i+1)+"electrode",
                                cu[i].GetNbinsX(), cu[i].GetXaxis().GetXmin(), cu[i].GetXaxis().GetXmax()))
        cross_talk_cu[i].Reset()

    for i in range(read_ele_num): 
        if i == 0:
            pass
        else:
            cross_talk_cu[i-1].Add(cu[i], 0.1)
        cross_talk_cu[i].Add(cu[i], 0.8)
        if i == read_ele_num-1:
            pass
        else:
            cross_talk_cu[i+1].Add(cu[i], 0.1)

    return cross_talk_cu
