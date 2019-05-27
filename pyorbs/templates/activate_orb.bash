if [[ -e "$HOME/.bashrc" ]]; then source "$HOME/.bashrc"; fi
if [[ "${PYORBS_SHELL}" == "1" ]]; then
    export PYORBS_SHELL=0
    $SHELL --init-file "%(init_file)s"
else
    source "%(activate_script)s"
    export PYORBS_ACTIVE_ORB="%(name)s"
    alias deactivate=exit
    if [[ "${PYORBS_NO_CD}" != "1" ]]; then cd "%(cwd)s"; fi
fi
