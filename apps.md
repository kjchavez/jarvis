# Jarvis Apps
The core components of a Jarvis app are:

1. Executables for each ACTION
2. A manifest.prototxt describing routes
3. A state.proto file defining the structure of app state
4. A setup.py script to be executed when app is loaded into Jarvis

The directory structure should follow this:

    app/
        bin/
            action1.sh
            action2.sh
        manifest.prototxt
        state.proto
        setup.py

## bin
This directory contains an executable for each possible action in your app. Parameters will be passed on the command line as...

    bin/action1.sh --param_name "param_value"

The executable is responsible for handling this appropriately.

## manifest.prototxt
See the example manifest.prototxt in the `lightapp`. The manifest defines criteria for each of the apps actions. If a Jarvis intent matches the listed action and ALL required parameters, it will trigger the route and the corresponding program will be executed.

## state.proto
Defines the structure of an app's state, as it will be stored in the Jarvis state module.

## setup.py
A script that will be executed only once, when Jarvis is first booted up. Primarily, this is responsible for setting the initial state correctly for the app (if it isn't the default from the protobuf)
