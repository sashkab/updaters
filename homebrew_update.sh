#!/usr/bin/env sh

# Notifies you when updates are available for Homebrew packages
# Uses terminal-notifier in OS X Mountain Lion and above. To install it use command:
# brew install terminal-notifier

BREW_EXEC='/usr/local/bin/brew'

# https://github.com/Homebrew/brew/blob/master/share/doc/homebrew/Analytics.md
export HOMEBREW_NO_ANALYTICS=1

if [ -z "$1" ]; then
    $BREW_EXEC update > /dev/null 2>&1
    outdated=$($BREW_EXEC outdated)

    if [ -n "$outdated" ]; then
	/usr/local/bin/terminal-notifier -message "$outdated" -title "Homebrew Updates" # -execute $0' upgrade'
    fi
#else
#    $BREW_EXEC upgrade 2>&1 > /dev/null
fi
