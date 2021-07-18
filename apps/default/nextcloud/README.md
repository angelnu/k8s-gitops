# Notes

## Adding a folder manually moved to Nextcloud

`sudo -u www-data php -d memory_limit=-1 /var/www/html/occ files:scan --path=anunez/files/Software/Devices -vv`