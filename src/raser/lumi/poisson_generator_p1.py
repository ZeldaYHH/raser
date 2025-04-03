import ROOT
import re
import os
from array import array
import random
import json
import multiprocessing
import shutil

from device import build_device as bdv
from . import cflm_p1
from . import get_current_p1

def main():
    
    output_path = "output/lumidSides/pixel"   #
    random.seed(3020122)                             #
    
    rand = ROOT.TRandom3()
    average_hit = 3.4
    total_samples = 100000
    hitnumber = []


    for i in range(total_samples):
        hitnumber.append(rand.Poisson(average_hit))
    
    hist = ROOT.TH1F("hist", "One-Dimensional Histogram", 10000, -5, 15)

    for num in hitnumber:
        hist.Fill(num)

    cp = ROOT.TCanvas("cp", "cp", 800, 600)
    hist.Draw()

    cp.SaveAs(os.path.join(output_path, 'poisson_dis.pdf'))

    with open('./setting/g4experiment/cflm_p1.json', 'r') as p:   #
         g4_dic = json.load(p)
    
    detector_json = os.getenv("RASER_SETTING_PATH")+"/detector/"
    with open(os.path.join(detector_json, g4_dic['DetModule'])) as q:
         det_dic = json.load(q)
    
    det_name = det_dic['det_name']
    my_d = bdv.Detector(det_name)

    file = ROOT.TFile("output/lumiDataFile_p1.root", "READ")
    tree = file.Get("electrons")

    pos, mom, energy = [], [], []
    TotalHitInfo = [] 
    
    for i in range(tree.GetEntries()):

        tree.GetEntry(i)
        pos.append([tree.pos_x, tree.pos_y, tree.pos_z])
        mom.append([tree.px, tree.py, tree.pz])
        energy.append(tree.s_energy) 

    for k in range(len(pos)):
        TotalHitInfo.append([pos[k], mom[k], energy[k]])
    
    random.shuffle(TotalHitInfo)

    sampleNumber = 10
    randomhit = random.sample(hitnumber, sampleNumber)

    nCount = 0
    with open(os.path.join(output_path, 'PossionHit.txt'), 'w') as PossionHitFile:      
         for i in range(len(randomhit)):
             if randomhit[i] == 0:
                  PossionHitFile.write(f'{randomhit[i]} {999} {nCount*10}\n')
             else:
                  randomHitInfo = random.sample(TotalHitInfo, randomhit[i])
                  PossionHitFile.write(f'{randomhit[i]} {randomHitInfo} {nCount*10}\n')
             nCount+=1

    def worker_function_I(queue, lock, j, ht):
        try:
            print(f"运行 loop_solver:{j}")
            result_message = "Execution completed successfully"
            cflm_p1.main()                                                             #
            get_current_p1.main()
            os.remove(os.path.join(output_path, "s_p_steps.json"))
            os.remove(os.path.join(output_path, "s_energy_steps.json"))
            os.remove(os.path.join(output_path, "s_edep_devices.json"))
            classify_current(output_path, ht)
        except Exception as e:
            result_message = f"Error: {e}"
        with lock:
            queue.put(result_message)
    lock = multiprocessing.Lock()
    queue = multiprocessing.Queue()

    HitTimeList = []
    with open(os.path.join(output_path, 'PossionHit.txt'), 'r') as Hit_input_file:
         for line in Hit_input_file:
              pos, mom, energy = [], [], []
              match = re.match(r'(\d+) (\[.*\]) (\d+)', line)
              if match:
                   hitEvents = match.group(1)
                   pos_mom_energy = match.group(2)
                   pos_mom_energy_list = eval(pos_mom_energy)
                   hitTime = int(match.group(3))
                   HitTimeList.append(hitTime)
                   if int(hitEvents) == 0:
                        print('No hit events')
                   else:
                        for ele in pos_mom_energy_list:
                            pos.append(ele[0])
                            mom.append(ele[1])
                            energy.append(ele[2])
                   with open('./setting/g4experiment/cflm_p1.json', 'r') as file:
                            g4_dic = json.load(file)    
                            g4_dic['NumofGun']    = int(hitEvents)
                            g4_dic['par_in']      = pos
                            g4_dic['par_direct']  = mom
                            g4_dic['par_energy']  = energy
                            g4_dic['CurrentName'] = f"PoiPixelCurrent_{hitTime}.root"   
                            updated_g4_dic = json.dumps(g4_dic, indent=4)
                
                   with open('./setting/g4experiment/cflm_p1.json', 'w') as file:
                        file.write(updated_g4_dic)
    
                   p = multiprocessing.Process(target=worker_function_I, args=(queue, lock, line, hitTime))
                   p.start()
                   p.join()
                    
                   while not queue.empty():
                        output_info = queue.get() 
                        print("队列输出:", output_info)  # 确认输出内容
                        if output_info is None:
                           print("警告: worker_function 返回了 None,可能发生了错误!")
    
    pattern_I = re.compile(r"PoiPixelCurrent_(\d+)_I_(-?\d+)_(\d+).txt")
    pattern_II = re.compile(r"PoiPixelCurrent_(\d+)_II_(-?\d+)_(\d+).txt")
    mg1 = ROOT.TMultiGraph()
    mg2 = ROOT.TMultiGraph()
    
    for root, dirs, files in os.walk(output_path):
        for ht_folder in dirs:
            for filename in os.listdir(os.path.join(output_path, ht_folder)):
                if pattern_I.match(filename):
                   time_list_I, current_list_I = [], []
                   with open(os.path.join(output_path, ht_folder, filename), 'r') as file:
                        for line in file:
                            time_I = float(line.split(' ')[0])*1e9
                            current_I = float(line.split(' ')[1])*1e6
                            time_list_I.append(time_I)
                            current_list_I.append(current_I)
                   graph1 = ROOT.TGraph(len(time_list_I), array('d', time_list_I), array('d', current_list_I))
                   mg1.Add(graph1, 'lp')
                elif pattern_II.match(filename):
                     time_list_II, current_list_II = [], []
                     with open(os.path.join(output_path, ht_folder, filename), 'r') as file:
                          for line in file:
                              time_II = float(line.split(' ')[0])*1e9
                              current_II = float(line.split(' ')[1])*1e6
                              time_list_II.append(time_II)
                              current_list_II.append(current_II)
                     graph2 = ROOT.TGraph(len(time_list_II), array('d', time_list_II), array('d', current_list_II))
                     mg2.Add(graph2, 'lp')

    c1 = ROOT.TCanvas('c1', 'c1', 800, 600)
    mg1.Draw('AP')
    mg1.GetXaxis().SetTitle('Time(ns)')
    mg1.GetYaxis().SetTitle('Current(uA)')
    c2 = ROOT.TCanvas('c2', 'c2', 800, 600)
    mg2.Draw('AP')
    mg2.GetXaxis().SetTitle('Time(ns)')
    mg2.GetYaxis().SetTitle('Current(uA)')

    c1.SaveAs(os.path.join(output_path, 'PoiPixelCurrent_I.pdf'))
    c2.SaveAs(os.path.join(output_path, 'PoiPixelCurrent_II.pdf'))      

def classify_current(f_folder_path, d_folder_name):
    
    pattern = re.compile(r"PoiPixelCurrent_(\d+)_(I|II)_(-?\d+)_(\d+).txt")

    os.makedirs(os.path.join(f_folder_path, str(d_folder_name)), exist_ok=True)
    for filename in os.listdir(f_folder_path):
        if pattern.match(filename):
            htime = int(pattern.match(filename).group(1))
            if htime == int(d_folder_name):
                shutil.move(os.path.join(f_folder_path, filename), os.path.join(f_folder_path, str(d_folder_name)))
                print(f"{filename} has been moved to {d_folder_name}")
    
    print('Add time label......')

    for filename in os.listdir(os.path.join(f_folder_path, str(d_folder_name))):
        if filename.endswith(".txt"):
           file_path = os.path.join(f_folder_path, str(d_folder_name), filename)
           new_lines = []
           with open(file_path, 'r') as file:
                for line in file:
                    parts = line.split(' ')
                    if parts: 
                       stime = float(parts[0]) + int(d_folder_name)*1e-9  
                       new_line = f"{stime} {' '.join(parts[1:])}" 
                       new_lines.append(new_line)
        
           with open(file_path, 'w') as file:
                file.writelines(new_lines)

    print('Time label added successfully')
