import os
import array
import time
import multiprocessing
import ROOT

from device import build_device as bdv
from . import cflm_p3
from field import devsim_field as devfield
from current import cal_current as ccrt

from util.output import output
import json

def main():
    
    geant4_json = os.getenv("RASER_SETTING_PATH")+"/g4experiment/cflm_p3.json"
    with open(geant4_json) as f:
         g4_dic = json.load(f)

    detector_json = os.getenv("RASER_SETTING_PATH")+"/detector/"
    with open(os.path.join(detector_json , g4_dic['DetModule'])) as q:
         det_dic = json.load(q)

    start = time.time()

    det_name = det_dic['det_name']
    my_d = bdv.Detector(det_name)
    voltage = det_dic['bias']['voltage']
    amplifier = det_dic['amplifier']

    print(my_d.device)
    print(voltage)

    my_f = devfield.DevsimField(my_d.device, my_d.dimension, voltage, det_dic['read_out_contact'], 0)

    def worker_function(queue, lock, i, j):
       
       try:
           result_message = "Execution completed successfully"
           print('DetectorID(Y,Z):       ', (i, j))
           my_g4 = cflm_p3.cflmPixelG4Interaction(my_d, i, j)

           if my_g4.HitFlag == 0:
               print("No secondary particles hit the detector")
           else:
               my_current = ccrt.CalCurrentG4P(my_d, my_f, my_g4, -1)
               save_current(my_current, g4_dic, det_dic['read_out_contact'], i, j)
       except Exception as e:
           result_message = f"Error: {e}"
       with lock:
           queue.put(result_message)
  
    lock = multiprocessing.Lock()
    queue = multiprocessing.Queue()
    
    dividedAreaZIndex = []
    for k in range(30):
        dividedAreaZIndex.append(k)
    dividedAreaYIndex = [-3, -2, -1, 0, 1, 2]
    
    for i in dividedAreaYIndex:  
        for j in dividedAreaZIndex:
            p = multiprocessing.Process(target=worker_function, args=(queue, lock, i, j))
            p.start()
            p.join()
            while not queue.empty():
                output_info = queue.get() 
                print("队列输出:", output_info)
                if output_info is None:
                    print("警告: worker_function 返回了 None,可能发生了错误!")   
    del my_f
    end = time.time()
    print("total_time:%s"%(end-start))
    
def save_current(my_current, g4_dic, read_ele_num, p, q):
 
    time = array.array('d', [999.])
    current = array.array('d', [999.])
    fout = ROOT.TFile(os.path.join("output/lumip3", g4_dic['CurrentName'].split('.')[0])  + ".root", "RECREATE")
    t_out = ROOT.TTree("tree", "signal")
    t_out.Branch("time", time, "time/D")
    for i in range(len(read_ele_num)):
        t_out.Branch("current"+str(i), current, "current"+str(i)+"/D")
        for j in range(my_current.n_bin):
            current[0]=my_current.sum_cu[i].GetBinContent(j)
            time[0]=j*my_current.t_bin
            t_out.Fill()
    t_out.Write()
    fout.Close()
   
    file = ROOT.TFile(os.path.join("output/lumip3", g4_dic['CurrentName'].split('.')[0])  + ".root", "READ")
    tree = file.Get("tree")

    pwl_file = open(os.path.join("output/lumip3", f"{g4_dic['CurrentName'].split('.')[0]}_{p}_{q}.txt"), "w")

    for i in range(tree.GetEntries()):
       tree.GetEntry(i)
       time_pwl = tree.time
       current_pwl = tree.current0
       pwl_file.write(str(time_pwl) + " " + str(current_pwl) + "\n")
    
    pwl_file.close()
    file.Close()