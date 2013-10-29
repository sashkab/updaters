#!/usr/bin/env sh

# Notifies you when updates are available for Homebrew packages
# Uses terminal-notifier in OS X Mountain Lion and above. To install it use command:
# sudo gem install terminal-notifier
#
# Copy file into $HOME/bin and add to crontab:
# 0 7,15 * * * $HOME/bin/homebrew_update.sh

BREW_EXEC='/usr/local/bin/brew'

if [ -z "$1" ]; then
    $BREW_EXEC update 2>&1 > /dev/null
    outdated=`$BREW_EXEC outdated`

    if [ ! -z "$outdated" ]; then
	/usr/bin/terminal-notifier -message "$outdated" -title "Homebrew Updates" -execute $0' upgrade'
    fi
else
    $BREW_EXEC upgrade 2>&1 > /dev/null
fi
