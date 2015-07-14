# pySMARTnotify
Notify when smart values for drives are out of spec. Uses `smartctl --scan` to detect drives

Checks if any of the specified SMART ID's *RAW_VALUE* is > 0 and checks if the *WHEN_FAILED* field is not "-".

Add drives you want to skip to the ignore list ('dev/something').

###Caveats:
  - Uses SSL for SMTP.
  - SMTP auth password is stored in **plain text**, so make sure you set proper file access permissions (0700 ?).
  - `smartctl` requires root priviliges, it will try to invoke sudo if not running as root, make sure the user does not have to input a password to run smartctl\*
  - make sure user can write the *"flagged drives"* file to the specified path.

###Dependencies:
  - [`smartmontools`](https://www.smartmontools.org/)
  - [`python2`](https://www.python.org)


\*You can add a line to `/etc/sudoers`:
`USERNAME ALL = NOPASSWD: /usr/sbin/smartctl`

