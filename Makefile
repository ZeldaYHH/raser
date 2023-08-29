# Publish on pypi.org 
check: 
	python cfg/pypi.py sdist 
	twine check dist/* 
	
upload: 
	twine upload dist/* 

merge: 
	git remote update 
	git merge upstream/main 

clean: 
	rm -rf dist raser.egg-info  

build-login:
	ssh -Y shixin@lxslc701

build-raser-sandbox: 
	apptainer build --force --fakeroot --sandbox /tmp/raser-sandbox/ cfg/raser.def

shell-raser-sandbox:
	apptainer shell --env-file cfg/env --fakeroot -w /tmp/raser-sandbox 

test-raser-sandbox:
	apptainer shell --env-file cfg/env -B /cefs,/afs,/besfs5,/cvmfs,/scratchfs,/workfs2 /tmp/raser-sandbox 

build-raser-sif:
	apptainer build --fakeroot raser.sif /tmp/raser-sandbox  

shell-raser-sif:
	apptainer shell --env-file cfg/env raser.sif 




 



