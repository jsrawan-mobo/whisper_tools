#! /bin/sh
nohup sh -c 'streamlit run index.py > /var/log/pocket/streamlit.log 2>&1' &
nohup sh -c 'jupyter notebook --port=8888 --no-browser --ip=0.0.0.0 --allow-root --notebook-dir=/src/notebooks > /var/log/pocket/jupyter.log 2>&1' &
sleep 1
tail -f  /var/log/pocket/jupyter.log /var/log/pocket/streamlit.log
