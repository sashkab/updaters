#!/usr/bin/env sh

# Notifies you when updates are available for Homebrew packages
# Uses terminal-notifier in OS X Mountain Lion and above. To install it use command:
# brew install terminal-notifier

if [ -e "/opt/homebrew/bin/brew" ]; then
    BREW_EXEC="/opt/homebrew/bin/brew"
elif [ -e "/usr/local/bin/brew" ]; then
    BREW_EXEC="/usr/local/bin/brew"
fi
TN="$($BREW_EXEC --prefix terminal-notifier)/bin/terminal-notifier"

# https://github.com/Homebrew/brew/blob/master/share/doc/homebrew/Analytics.md
export HOMEBREW_NO_ANALYTICS=1

if [ -z "$1" ]; then
    $BREW_EXEC update > /dev/null 2>&1
    outdated=$($BREW_EXEC outdated)

    if [ -n "$outdated" ]; then
	$TN -message "$outdated" -title "Homebrew Updates" # -execute $0' upgrade'
    fi
#else
#    $BREW_EXEC upgrade 2>&1 > /dev/null
fi
