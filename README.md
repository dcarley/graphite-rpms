RPMs for Graphite/Carbon/Whisper project.

 - http://graphite.wikidot.com/
 - http://graphite.readthedocs.org/
 - https://launchpad.net/graphite/

This is a continuation of the user contributions detailed at:

 - https://bugs.launchpad.net/graphite/+bug/546737

All dependencies can be satisified by the stock CentOS/RHEL and EPEL repositories. To use these packages on EL5 you will need version 8.0 or greater of `python-twisted-core`. This can be easily obtained by recompiling the SRPM from EL6. Newer versions of Python, Django, etc are not currently required.

Build SRPMs with `rpmbuild -bs --nodeps` and binary RPMs with `mock`.
