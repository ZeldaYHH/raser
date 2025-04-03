import ROOT
import re
import os
from array import array
import random
import json
import multiprocessing
import shutil

from device import build_device as bdv
from . import cflm_p3
from . import get_current_p3

def main():
    
    output_path = "output/lumip3"
    
    random.seed(3020122)
    
    rand = ROOT.TRandom3()
    average_hit = 3.2
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

    with open('./setting/g4experiment/cflm_p3.json', 'r') as p:
         g4_dic = json.load(p)
    
    detector_json = os.getenv("RASER_SETTING_PATH")+"/detector/"
    with open(os.path.join(detector_json, g4_dic['DetModule'])) as q:
         det_dic = json.load(q)
    
    det_name = det_dic['det_name']
    my_d = bdv.Detector(det_name)

    file = ROOT.TFile("output/lumiDataFile_p3.root", "READ")
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
            cflm_p3.main()
            get_current_p3.main()
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
                   with open('./setting/g4experiment/cflm_p3.json', 'r') as file:
                            g4_dic = json.load(file)    
                            g4_dic['NumofGun']    = int(hitEvents)
                            g4_dic['par_in']      = pos
                            g4_dic['par_direct']  = mom
                            g4_dic['par_energy']  = energy
                            g4_dic['CurrentName'] = f"PoiPixelCurrent_{hitTime}.root"   
                            updated_g4_dic = json.dumps(g4_dic, indent=4)
                
                   with open('./setting/g4experiment/cflm_p3.json', 'w') as file:
                        file.write(updated_g4_dic)
    
                   p = multiprocessing.Process(target=worker_function_I, args=(queue, lock, line, hitTime))
                   p.start()
                   p.join()
                    
                   while not queue.empty():
                        output_info = queue.get() 
                        print("队列输出:", output_info)  # 确认输出内容
                        if output_info is None:
                           print("警告: worker_function 返回了 None,可能发生了错误!")

    pattern = re.compile(r"PoiPixelCurrent_(\d+)_(-?\d+)_(\d+).txt")
    mg = ROOT.TMultiGraph()

    for root, dirs, files in os.walk(output_path):
        for ht_folder in dirs:
            for filename in os.listdir(os.path.join(output_path, ht_folder)):
                if pattern.match(filename):
                   time_list, current_list = [], []
                   with open(os.path.join(output_path, ht_folder, filename), 'r') as file:
                        for line in file:
                            time = float(line.split(' ')[0])*1e9
                            current = float(line.split(' ')[1])*1e6
                            time_list.append(time)
                            current_list.append(current)
                   graph1 = ROOT.TGraph(len(time_list), array('d', time_list), array('d', current_list))
                   mg.Add(graph1, 'lp')

    c1 = ROOT.TCanvas('c1', 'c1', 800, 600)
    mg.Draw('AP')
    mg.GetXaxis().SetTitle('Time(ns)')
    mg.GetYaxis().SetTitle('Current(uA)')

    c1.SaveAs(os.path.join(output_path, 'PoiPixelCurrent.pdf'))

def classify_current(f_folder_path, d_folder_name):
    
    pattern = re.compile(r"PoiPixelCurrent_(\d+)_(-?\d+)_(\d+).txt")

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