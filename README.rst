soup.io archiver
================

As soup.io crew decided that 2016 was so bad that it did not happen, a lot of dank memes and other content has been lost. This script is meant to shamelessly crawl over a soup.io account of choice and download all the images from it.

Usage
=====

The archiver will use Parallel::ForkManager if available, to fetch multiple files at once.

You can install Parallel::ForkManager using your distribution package manager or using cpanm (cpanminus).

If the modules are already present on system::

    perl archiver 'SOMENAME.soup.io'

in case of going with cpanm (for example, if distro lacks the modules, or one have no root access)::

    cpanm --notest --installdeps . -L deps
    perl -I deps/lib/perl5 archiver 'SOMENAME.soup.io'

LIVE LONG AND PROSPER.
