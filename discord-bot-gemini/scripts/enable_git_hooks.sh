#!/usr/bin/env bash
echo "Configuring repo hooks to use the .githooks directory..."
git config core.hooksPath .githooks
echo "Hooks path set to: $(git config --get core.hooksPath)"
echo "Note: This only configures hooks locally for this repo. Other contributors must run this command or use a setup script."
