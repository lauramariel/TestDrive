# Startup script for Windows client setup for connecting to the Nutanix Files instance
# running on the same VPC. This was designed to be run as a startup script passed to a
# Windows GCP VM that is defined in the resource spec files.json
#
# It does the following:
# - Sets up firewall rules for network discovery and file sharing
# - Installs the NFS Client
# - Sets the local DNS to the AutoDC (Alpine DC) IP that is running on the cluster as ntnxlab.local
# - Adds the computer to the ntnxlab.local domain and does a reboot
# - After reboot, the script will run again.
# - The second time the script runs, it will:
#   - Attempt to run everything again but shouldn't have an impact (this should eventually be optimized/fixed)
#   - Add the SSP Basic Users to the local Remote Desktop Users group
#   - Download the Sample Data to the C:\ drive
#
# Author: laura@nutanix.com
# Date: 07-07-2020

# Set ntnxlab.local IP address
$AutoDCIP = "172.31.0.41"

# Set up Logging
Function Log {
    param(
        [Parameter(Mandatory=$true)][String]$msg
    )
    
    Add-Content $LogFile $msg
}

$Date = Get-Date -format "yyyy-MM-dd-HHmmss"
$LogFile = "C:\Users\Public\startup-log-$Date.txt"
New-Item $LogFile
Set-Content $LogFile "$Date Start Script"

Log("Enabling Network Discovery and File Sharing")
# Allow Network Discovery and File Sharing
Get-NetFirewallRule -DisplayGroup "Network Discovery" | Set-NetFirewallRule -Action Allow
Get-NetFirewallRule -DisplayGroup "Network Discovery" | Enable-NetFirewallRule
Get-NetFirewallRule -DisplayGroup "File and Printer Sharing" | Set-NetFirewallRule -Action Allow 
Get-NetFirewallRule -DisplayGroup "File and Printer Sharing" | Enable-NetFirewallRule

# Install NFS Client
Log("Installing NFS Client")
Install-WindowsFeature nfs-client
Log("Sleeping 30s")
sleep 30

# Get network interface ifIndex
$index = Get-NetAdapter | Where { $_.Name -eq "Ethernet" } | foreach { $_.ifIndex }
Log("Index of the Ethernet adapter is $index")

# Set DNS to ntnxlab.local IP address
Log("Setting DNS to $AutoDCIP")
Set-DnsClientServerAddress -InterfaceIndex $index -ServerAddresses $AutoDCIP

Log("Sleeping 5s")
sleep 5

# Connect to ntnxlab.local
Log("Adding computer to domain ntnxlab.local")
$joinCred = New-Object pscredential -ArgumentList ([pscustomobject]@{
    UserName = "ntnxlab.local\Administrator"
    Password = (ConvertTo-SecureString -String 'nutanix/4u' -AsPlainText -Force)[0]
})

Add-Computer -Domain "ntnxlab.local" -Credential $joinCred -Confirm:$false -Restart -Force

Log("Sleeping 5s")
sleep 5

# Add-Computer command will reboot, so initial log file will end here

Log("After Reboot")

# Add SSP Basic Admins to Remote Desktop Users
Log("Adding SSP Basic Admins to Remote Desktop Users")
Add-LocalGroupMember -Group "Remote Desktop Users" -Member "ntnxlab.local\SSP Basic Users"

# Download Sample Data to C:\
Log("Downloading Sample Data")
Invoke-WebRequest "https://storage.googleapis.com/testdrive-templates/files/deepdive/SampleData_Small.zip" -outfile "C:\sampledata.zip"

# Download Wallpaper
Log("Downloading and setting wallpaper")
Invoke-WebRequest "https://storage.googleapis.com/testdrive-walkme-graphics/wallpapers/Bezel-Wallpaper-01.png" -outfile "C:\Users\Public\Pictures\bezel-wallpaper-01.png"
Set-ItemProperty -path 'HKCU:\Control Panel\Desktop\' -name Wallpaper -value "C:\Users\Public\Pictures\bezel-wallpaper-01.png"

# Block all outbound connections
Log("Adding firewall rules")
Set-NetFirewallProfile -Name Domain -DefaultOutboundAction Block
Set-NetFirewallProfile -Name Private -DefaultOutboundAction Block
Set-NetFirewallProfile -Name Public -DefaultOutboundAction Block

# Enable NetLogon and open required ports
Enable-NetFirewallRule -Name Netlogon-TCP-RPC-In
Enable-NetFirewallRule -Name Netlogon-NamedPipe-In
New-NetFirewallRule -DisplayName "Nutanix Files Support TCP" -Direction Outbound -Action Allow -Protocol TCP -RemotePort 445,88,53
New-NetFirewallRule -DisplayName "Nutanix Files Support UDP" -Direction Outbound -Action Allow -Protocol UDP -RemotePort 445,88,389,53

# Block users from running apps as admin
# TBD

Log("=== Errors ===")
Log($error)
Log("==============")

$Date = Get-Date -format "yyyy-MM-dd-HHmmss"
Log("$Date End Script")