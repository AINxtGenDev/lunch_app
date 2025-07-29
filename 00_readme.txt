#######################################################################
Create and activate environment
#######################################################################
*) cd /home/nuc8/05_development/02_lunch_app

   conda env create -f environment.yaml

   if environment.yaml was modified use this command:
   conda env update --name lunch-menu-app --file environment.yaml --prune
   
   conda remove --name lunch-menu-app --all
   
   
*) on Raspberry Pi 4

   # Download and install Miniforge for ARM64
   wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh
   chmod +x Miniforge3-Linux-aarch64.sh
   ./Miniforge3-Linux-aarch64.sh

   # Restart shell or source bashrc
   source ~/.bashrc

   # Create environment from your yaml
   conda env create -f environment.yaml
   conda activate lunch-menu-app
   
   # For webdriver-manager, you might need to specify Chrome ARM64
   # Make sure you have chromium-browser installed:
   sudo apt install chromium-browser chromium-chromedriver

*) Activate the environment
   ##############################
   conda activate lunch-menu-app
   ##############################
   
   # To verify everything worked correctly, you can run:
   conda env list    # Shows all environments, with * next to the active one
   python --version  # Should show Python 3.12

*) Keep track of exact package version
   # Export current environment
   conda env export > environment.yml
   # For better cross-platform compatibility:
   conda env export --from-history > environment.yml

#######################################################################
Common useful commands
#######################################################################
    conda --version
    conda info
    
    # List all environments
    conda env list

   # Deactivate current environment
   conda deactivate

   # Remove environment if needed
   conda env remove -n lunch-menu-app

---> use conda install instead of pip when possible <---

#######################################################################
## git 
#######################################################################
git status
git add .
git commit -m "Initial commit"
git push -u origin main
git push
