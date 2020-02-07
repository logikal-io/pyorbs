#!/usr/bin/env bash
_orb_completions() {
    compopt +o default

    # Extracting arguments
    local path_args=("-r --reqs -e --exec -o --orbs")
    local args=(${COMP_WORDS[@]})
    local current=${args[${COMP_CWORD}]}
    local last=${args[-1]}
    local pos_args=()
    local opt_args=()
    for arg in ${args[@]}; do
        if [[ "${arg}" =~ -.* ]]; then opt_args+=("${arg}"); else pos_args+=("${arg}"); fi
    done

    # Checking completion limit
    local limit=1
    for arg in ${opt_args[@]}; do
        if [[ " ${path_args[@]} " =~ " ${arg} " ]]; then ((limit++)); fi
    done
    if [[ "${current}" == "" && ${#pos_args[@]} > ${limit} ]]; then return; fi

    # Generating completion words
    if [[ " ${path_args[@]} " =~ " ${current} " ]]; then
        COMPREPLY="${current}"  # adding space
    elif [[
        ( " ${path_args[@]} " =~ " ${last} " ) ||
        ( "${current}" != "" && ${#args[@]} > 1 && " ${path_args[@]} " =~ " ${args[-2]} " )
    ]]; then
        compopt -o default; COMPREPLY=()  # adding paths
    else
        local path=~/.pyorbs
        if [[ ${COMP_LINE} =~ (-o |--orbs )([^ ]+) ]]; then path=${BASH_REMATCH[2]}; fi
        path="${path/#\~/$HOME}"
        if [[ ! -d "${path}" ]]; then return; fi
        local words=$(ls "${path}")
        COMPREPLY=($(compgen -W "${words}" -- "${current}"))
    fi
} && complete -F _orb_completions orb
