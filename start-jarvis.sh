# Initialize Jarvis state
redis-server $JARVIS_ROOT/config/state.conf
for D in $JARVIS_ROOT/apps/*; do
    if [ -d "${D}" ]; then
        python ${D}/setup.py
    fi
done

# And Jarvis memory
redis-server $JARVIS_ROOT/config/memory.conf

# Finally start the action router
python -m jarvis.router
