# Emergent Behaviours in Heterogeneous Swarms of RVR and BOLT Robots

Nicholas Liu - z5364371

--------------------------------------------------------------------

[link to repo (all files are in repo)](https://github.com/nicliu2002/RVR-and-Bolt-Swarm)

## Code Setup and Running Procedure

To run the code start by making sure all files but `RVR Script.py` are contained within the the one directory. The code is run from the main function of `SwarmController.py`, however some initial parameters must first be setup.

1. In `SwarmController.py` here you will need to update the configurations for each robot to do this you will need the BOLT identifiers and RVR identifiers and IPs, identifier here references the BOLT's identifier and VICON name and the RVR's VICON name, make sure the indexes for the RVR identifiers and IPs line up.
2. Following this the VICON system will need to be setup, the IP address for VICON can be configured in the `ViconLocator.py` file, in the VICON Tracker software make sure to correctly label the BOLT and RVR markers with the respective identifiers previously used.
3. Make sure all robots are aligned facing towards +y on the VICON system.
4. SSH into the RVR with `ssh pi@<rvr_ip>`, upload the `RVR_Script.py` file and run it, the RVR **must be facing forward** at this point as this resets the heading.
5. Run the `main()` in `SwarmController.py` to start swarming.

## Parameter Configuration

The swarming parameters are adjusted within the `Boid.py` file, these can be found in the `__init__` function of each class.

## Data and Figures

The preferred way of collecting data for this is to utilise the VICON recording function and exporting these as CSV, this is due to any logging function taking up valuable time away from velocity updates and slowing the swarm calculations down, within `Data and Figures/Plotters` there are scripts to produce single plot metrics, plots of multiple trials mean and 95% CI metrics, location trace and videos of the location plot.

Within the `appendix` and `final_trials_plots` directories are all the plots used within the report while the raw data for these can be found in `Hand Tuning Tests Results` and `final_trials` for both the results gathered during hand tuning and the final trials for presentation in the report. While all metrics for each result gathered was plotted in the report in either `appendix` or `final_trials_plots` all videos are also generated in the `location_plot_videos` directory.

## Archive

Archive contains all archived files including the failed decentralised control implementation, if further work is completed on this, this is run through first running `vicon_bridge` on a laptop to stream VICON location data to each RVR, and then running `RVR_Controller.py` on each RVR, this will connect the RVR to both itself and the BOLTs, similar identifier conventions are used like those seen above.