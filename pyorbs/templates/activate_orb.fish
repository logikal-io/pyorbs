if test "$PYORBS_SHELL" = "1"
    set --export PYORBS_SHELL "0"
    $SHELL -C 'source "%(init_file)s"'
else
    source "%(activate_script)s"
    set --export PYORBS_ACTIVE_ORB "%(name)s"
    alias deactivate=exit
    if test "$PYORBS_NO_CD" != "1"; cd "%(cwd)s"; end
end
