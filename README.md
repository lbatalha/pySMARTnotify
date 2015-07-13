# pySMARTnotify
Notify when smart values for drives are out of spec. Uses `smartctl --scan` to detect drives

Checks if any of the specified SMART ID's *RAW_VALUE* is > 0 and checks if the *WHEN_FAILED* field is not "-".

Add drives you want to skip to the ignore list ('dev/something').

###Caveats:
  - Uses SSL for SMTP.
  - SMTP auth password is stored in **plain text**, so make sure you set proper file access permissions.
  - `smartctl` requires root priviliges, make sure the user does not have to input password to run the script.
  - if running as root, remove `sudo` call.
  - make sure user can write the *"flagged drives"* file to the specified path.

###Dependencies:
  - `smartmontools`
  - `python2`
