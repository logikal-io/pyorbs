if [[ -e "$HOME/.bashrc" ]]; then source "$HOME/.bashrc"; fi
if [[ "${{PYORBS_NEW_SHELL}}" == "1" ]]; then
    export PYORBS_NEW_SHELL=0
    $SHELL --init-file "{init_file}"
else
    source "{activate_script}"
    export PYORBS_CURRENT_ORB="{name}"
    alias deactivate=exit
    if [[ "${{PYORBS_NO_CD}}" != "1" ]]; then cd "{cwd}"; fi
fi
