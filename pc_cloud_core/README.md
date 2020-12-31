# Still in development
## Original logic for PC_CLOUD_CORE (TRIAL-150)
 
1. [PE] Cluster Initiation (EULA acceptance)
2. [PE & PC] Increase Aplos timeout to prevent Prism timeout
3. [PE & PC] Configure SMTP
4. [PE] Rename cluster
5. [PE] Create DSIP and VIP (should also reserve static IPs in GCP for these IPs)
6. [PE] Creation of Primary Network and IPAM - already done
7. [PE] Upload, deploy and power on 3 Ubuntu VMs
8. [PC] Inject Prism Central data (injects a fake cluster with data for capacity planning, inefficient VMs, etc.)
9. [PE] Deploy AutoDC2
10. [PE] Setup of DNS zones in AutoDC2
11. [PE] Setup AutoDC2 as an authentication source for Prism Element
12. [PC] Setup AutoDC2 as an authentication source for Prism Central
13. [PC] Upload Cloud CentOS image to PC for Calm blueprint (needs to be on PC image service for Calm to access)
14. [PC] Configure the Calm project (Nutanix provider, default-net subnet, environment variables)
15. [PC] Import 2 Blueprints (MyApp.json and MyCustomApp.json)
16. [PC] Modify both blueprints so that it's ready to launch without further customization necessary (passwords, etc)
17. [PC] Publish and Approve MyApp.json so it appears in the Marketplace

## Notes

### Steps we need to add
1. Enable Calm - or use the $ENABLE_CALM plugin (currently TD2 doesn't use this plugin so I'm assuming it's part of PC_CLOUD_CORE)
### Steps we might be able to remove, either because it's done in another plugin or we just never really needed it
1. [PE] Cluster Initiation (EULA acceptance) --> Using a generic spec w/o PC_CLOUD_CORE and PE_CLOUD_CORE, EULA was already accepted. Possibly part of the $RESET_PRISM_PASS or $REGISTER_PE_PC plugins
2. [PE & PC] Increase Aplos timeout to prevent Prism timeout --> Not sure if this is necessary as we autologin regardless
3. [PE & PC] Configure SMTP --> might not be required in TD2 but would be required for Prism lab
4. [PE] Rename Cluster --> This should be configurable in the spec itself
6. [PE] Creation of Primary Network and IPAM --> currently done as part of $MANAGED_NETWORK
11. [PE] Setup AutoDC2 as an authentication source for Prism Element --> probably just doing this in PC is enough

## Todo
- Use Haigh's helper functions everywhere
- Calm enablement (or use $ENABLE_CALM?) and all the Calm stuff
- Step 2 - Aplos timeout (if necessary)
- Step 3 - SMTP config
- Step 5 - Creation of DSIP/VIP (if not done already)
- Step 6 - Creation of network if required (if not done by $MANAGED_NETWORK)