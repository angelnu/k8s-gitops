# Paperless

Here we install multiple instances of paperlex-ngx for the family members

## how to configure printer

1. Add the destination (Remote UI)
    Log in to the Remote UI in System Manager Mode (settings can only be changed from there), click [Address Book] on the portal page, then click [Favorites]. Click the text link under [Number]/[Type]/[Name] on a slot marked "Not Registered", choose [File] as the destination type, and fill in:
    - Protocol: Windows (SMB), Host Name (e.g. \\nas.home.prod.<my domain>)
    - Folder Path: downloads\scanner\<paperless name such as recipes>
2. Add the home-screen shortcut (panel only)
    Favorite Settings cannot be registered from the Remote UI ([Canon User Manual](https://oip.manual.canon/USRMA-7183-zz-SSM-750-enUV/contents/devu-basicope-freq_set-reg.html)) — this has to be done at the machine.
    1. On the panel: Scan → File → Address Book → pick the new destination → Apply
    2. adjust the scan settings (resolution, PDF, duplex...)
    3. Favorite Settings → an unregistered slot → Register. Confirm the details, optionally rename it, and when asked whether to register it as a shortcut button select Yes — the combination is then added to the Home screen. Note that the destination cannot be changed afterwards; to change it you must delete the favorite and register it again.