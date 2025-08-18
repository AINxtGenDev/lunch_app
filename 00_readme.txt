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


Run the installation script with sudo:
  sudo bash install_scraper_timer.sh

  What this solution provides:

  1. Systemd Service (lunch-scraper.service): Runs the scraping task once
  2. Systemd Timer (lunch-scraper.timer): Schedules the service to run daily at 5:00 AM
  3. Benefits over crontab:
    - Better logging with journalctl
    - Automatic retries on failure
    - Persistent (runs missed jobs if Pi was off)
    - Better integration with systemd
    - Proper environment handling

  After installation, you can:

  - Check timer status: systemctl status lunch-scraper.timer
  - View next scheduled run: systemctl list-timers lunch-scraper.timer
  - Check last scrape logs: journalctl -u lunch-scraper.service -n 50
  - Run manually: sudo systemctl start lunch-scraper.service
  - Disable if needed: sudo systemctl disable lunch-scraper.timer


#######################################################################
## lunch-app services
#######################################################################

Create the environment file (keeps your paths configurable):

sudo /etc/default/lunch-scraper
PATH=/home/stecher/miniforge3/envs/lunch-menu-app/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
CONDA_DEFAULT_ENV=lunch-menu-app
HOME=/home/stecher

journalctl -u lunch-scraper.service -n 200 --no-pager

pwd
/etc/systemd/system
(lunch-menu-app) stecher@stechertennis:/etc/systemd/system $ ls lunch*
-rw-r--r-- 1 root root 652 Jul 29 10:13 lunch-app.service
-rw-r--r-- 1 root root 622 Jul 31 20:21 lunch-scraper.service
-rw-r--r-- 1 root root 350 Jul 31 20:21 lunch-scraper.timer

systemctl status lunch-app.service 
● lunch-app.service - Lunch Menu Flask Application
     Loaded: loaded (/etc/systemd/system/lunch-app.service; enabled; preset: enabled)
     Active: active (running) since Mon 2025-08-18 14:44:24 CEST; 9min ago
   Main PID: 24852 (python)
      Tasks: 2 (limit: 3920)
        CPU: 58.909s
     CGroup: /system.slice/lunch-app.service
             ├─24852 /home/stecher/miniforge3/envs/lunch-menu-app/bin/python /home/stecher/miniforge3/envs/lunch-menu-app/bin/gunicorn --config /home/stecher/lunch_app/gunicorn_config.py run:app
             └─24853 /home/stecher/miniforge3/envs/lunch-menu-app/bin/python /home/stecher/miniforge3/envs/lunch-menu-app/bin/gunicorn --config /home/stecher/lunch_app/gunicorn_config.py run:app

Aug 18 14:44:24 stechertennis systemd[1]: Started lunch-app.service - Lunch Menu Flask Application.


systemctl status lunch-scraper.service 
● lunch-scraper.service - Lunch Menu Daily Scraper
     Loaded: loaded (/etc/systemd/system/lunch-scraper.service; static)
     Active: inactive (dead) since Mon 2025-08-18 05:02:24 CEST; 9h ago
TriggeredBy: ● lunch-scraper.timer
    Process: 14690 ExecStart=/home/stecher/miniforge3/envs/lunch-menu-app/bin/python /home/stecher/lunch_app/manual_scrape_today.py (code=exited, status=0/SUCCESS)
   Main PID: 14690 (code=exited, status=0/SUCCESS)
        CPU: 1min 13.123s

Aug 18 05:02:23 stechertennis python[14690]: INFO:app:  Total items scraped: 52
Aug 18 05:02:23 stechertennis python[14690]: INFO:app:============================================================
Aug 18 05:02:23 stechertennis python[14690]: INFO:app:Notifying connected clients of menu update...
Aug 18 05:02:23 stechertennis python[14690]: INFO:app:Broadcast menu update for 8 restaurants with 52 total items
Aug 18 05:02:23 stechertennis python[14690]: Starting manual scrape for today's menus...
Aug 18 05:02:23 stechertennis python[14690]: Scraping completed!
Aug 18 05:02:23 stechertennis python[14690]: Results: {'total_scrapers': 8, 'successful': 7, 'failed': 1, 'total_items': 52, 'errors': [{'scraper': 'Albanco', 'error': 'No data returned'}]}
Aug 18 05:02:24 stechertennis systemd[1]: lunch-scraper.service: Deactivated successfully.
Aug 18 05:02:24 stechertennis systemd[1]: Finished lunch-scraper.service - Lunch Menu Daily Scraper.
Aug 18 05:02:24 stechertennis systemd[1]: lunch-scraper.service: Consumed 1min 13.123s CPU time.



systemctl status lunch-scraper.timer
● lunch-scraper.timer - Run Lunch Menu Scraper Daily at 5 AM
     Loaded: loaded (/etc/systemd/system/lunch-scraper.timer; enabled; preset: enabled)
     Active: active (waiting) since Sun 2025-08-17 04:00:04 CEST; 1 day 10h ago
    Trigger: Tue 2025-08-19 00:01:31 CEST; 9h left
   Triggers: ● lunch-scraper.service

Aug 17 04:00:04 stechertennis systemd[1]: Started lunch-scraper.timer - Run Lunch Menu Scraper Daily at 5 AM.



#######################################################################
## git 
#######################################################################
git status
git add .
git commit -m "Initial commit"
git push -u origin main
git push
