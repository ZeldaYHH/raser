import importlib
import subprocess
def main(args_dict):
    if len(args_dict['option']) == 0:
        print("cal main function placeholder")
    else:
        module_name = args_dict['option'][0]
        args_dict['option']=args_dict['option'][1:]
        try:
            module = importlib.import_module("field.cal."+module_name)
            module.main(args_dict)
        except ModuleNotFoundError:
            try:
                subprocess.run('apptainer exec --env-file cfg/env -B /cefs,/afs,/besfs5,/cvmfs,/scratchfs,/workfs2 \
                                /afs/ihep.ac.cn/users/s/shixin/raser/raser-2.0.sif \
                                \"./raser/field/cal/'+module_name+'.py\"', shell=True)
            except FileNotFoundError:
                print("No cal subcommand found")