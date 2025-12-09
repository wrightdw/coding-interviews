#!/bin/bash

# Move frontend files to client directory
mv /workspaces/codespaces-react/src /workspaces/codespaces-react/client/
mv /workspaces/codespaces-react/public /workspaces/codespaces-react/client/
mv /workspaces/codespaces-react/index.html /workspaces/codespaces-react/client/
mv /workspaces/codespaces-react/vite.config.js /workspaces/codespaces-react/client/
mv /workspaces/codespaces-react/jsconfig.json /workspaces/codespaces-react/client/
mv /workspaces/codespaces-react/package.json /workspaces/codespaces-react/client/
mv /workspaces/codespaces-react/package-lock.json /workspaces/codespaces-react/client/
mv /workspaces/codespaces-react/node_modules /workspaces/codespaces-react/client/

echo "Frontend files moved to client directory"
