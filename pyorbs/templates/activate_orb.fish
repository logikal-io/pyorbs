if test "$PYORBS_NEW_SHELL" = "1"
    set --export PYORBS_NEW_SHELL "0"
    $SHELL -C 'source "{init_file}"'
else
    source "{activate_script}"
    set --export PYORBS_CURRENT_ORB "{name}"
    alias deactivate=exit
    if test "$PYORBS_NO_CD" != "1"; cd "{cwd}"; end
end
