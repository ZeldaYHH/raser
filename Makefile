# Publish on pypi.org 
check: 
	python cfg/pypi.py sdist 
	twine check dist/* 
	
upload: 
	twine upload dist/* 

merge: 
	git remote update 
	git merge upsteam/main 

clean: 
	rm -rf dist raser.egg-info  

# Build app container on lxslc701 
build-login:
	ssh -Y shixin@lxslc701

build-raser: 
	apptainer build --fakeroot raser.sif cfg/raser.def

build-raser-dev: 
	apptainer build --force --fakeroot --sandbox /tmp/raser-dev cfg/raser.def

sign-raser: 
	apptainer sign raser.sif 

# Install Geant4 on lxslc7 
geant4_install_1:
	./ext/geant4_build_1.sh  

geant4_install_2:
	./ext/geant4_build_2.sh  

geant4_install_3:
	./ext/geant4_build_3.sh  

	
# Copy Geant4 to cvmfs 
cvmfs-login: 
	ssh commonpub@cvmfspublisher.ihep.ac.cn -i ~/.ssh/id_rsa 

cvmfs-trans:
	cvmfs_server transaction common.ihep.ac.cn 

cvmfs-cp-geant4:
	cd /cvmfs/common.ihep.ac.cn/software/geant4/
	mkdir 10.7.p02 
	cd 10.7.p02 
	scp -r shixin@lxslc7.ihep.ac.cn:~/track/geant4/install . 
	scp -r shixin@lxslc7.ihep.ac.cn:~/track/geant4/data . 

cvmfs-geant4-patch:
	cd /cvmfs/common.ihep.ac.cn/software/geant4/10.7.p02 
	cp -a install/bin/geant4.sh  install/bin/geant4.sh.bak  
	sed -i "s@/afs/ihep.ac.cn/users/s/shixin/track/geant4@/cvmfs/common.ihep.ac.cn/software/geant4/10.7.p02@g" install/bin/geant4.sh 

cvmfs-publish:
	cvmfs_server publish common.ihep.ac.cn 



 



