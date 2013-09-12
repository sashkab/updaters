#!/usr/bin/env sh

# Notifies you when updates are available for Homebrew packages
# Uses terminal-notifier in OS X Mountain Lion and above. To install it use command:
# sudo gem install terminal-notifier
#
# Copy file into $HOME/bin and add to crontab:
# 0 7,15 * * * $HOME/bin/homebrew_update.sh

BREW='/usr/local/bin/brew'
$BREW update 2>&1 > /dev/null
outdated=`$BREW outdated`

if [ ! -z "$outdated" ]; then
    /usr/bin/terminal-notifier -message "New updates for homebrew are available" -title "Homebrew"
fi
