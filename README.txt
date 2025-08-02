# BarTender Integration Folder Structure

This folder contains all files related to the Greenfield Metal Sales label printing system.

## Folder Descriptions:

- **Data**: Temporary JSON files from Paradigm ERP webhooks
- **Archive**: Processed JSON files (moved here after printing)
- **Templates**: BarTender label templates (.btw files)
- **Logs**: System logs and print history
- **WebhookReceiver**: Python webhook service files
- **ErrorReports**: Failed print job details
- **Backup**: Template backups and configuration files
- **TestFiles**: Sample JSON files for testing
- **Documentation**: System documentation and guides

## Important Files:
- webhook_receiver.py: Main webhook service
- PackingList.btw: Packing list label template
- ProductLabel.btw: Individual product label template

Created: 2025-07-01 23:53:36
