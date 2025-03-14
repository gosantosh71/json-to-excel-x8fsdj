#!/usr/bin/env bash
# Bash completion script for the JSON to Excel Conversion Tool

# Global variables defining available commands and options
COMMANDS="convert validate info help"
CONVERT_OPTIONS="--sheet-name --array-handling --verbose --chunk-size --fields"
VALIDATE_OPTIONS="--verbose"
INFO_OPTIONS="--verbose --format"
HELP_OPTIONS="convert validate info help"
ARRAY_HANDLING_VALUES="expand join"
FORMAT_VALUES="text json"
TOOL_COMMAND="json_to_excel"

# Main completion function that provides suggestions based on current command-line input
_json_to_excel_completions() {
    # Get the current word being completed from COMP_WORDS array
    local cur="${COMP_WORDS[COMP_CWORD]}"
    # Get the previous word for context
    local prev="${COMP_WORDS[COMP_CWORD-1]}"
    # Initialize an empty array for completion suggestions
    local suggestions=()
    
    # If completing the first argument (command), suggest available commands
    if [ $COMP_CWORD -eq 1 ]; then
        suggestions=($COMMANDS)
    else
        # Determine which command we're completing for
        local command=""
        for ((i=1; i < COMP_CWORD; i++)); do
            if [[ " $COMMANDS " == *" ${COMP_WORDS[i]} "* ]]; then
                command="${COMP_WORDS[i]}"
                break
            fi
        done
        
        # If completing option values, suggest appropriate values
        if [[ "$prev" == "--array-handling" ]]; then
            suggestions=($ARRAY_HANDLING_VALUES)
        elif [[ "$prev" == "--format" ]]; then
            suggestions=($FORMAT_VALUES)
        elif [[ "$prev" == "--sheet-name" || "$prev" == "--fields" || "$prev" == "--chunk-size" ]]; then
            # These options take custom values, no specific suggestions
            suggestions=()
        # If completing options for a specific command, suggest appropriate options
        elif [[ "$cur" == -* ]]; then
            case "$command" in
                convert)
                    suggestions=($CONVERT_OPTIONS)
                    ;;
                validate)
                    suggestions=($VALIDATE_OPTIONS)
                    ;;
                info)
                    suggestions=($INFO_OPTIONS)
                    ;;
                help)
                    suggestions=($HELP_OPTIONS)
                    ;;
            esac
        else
            # If completing file arguments, use file completion
            suggestions=($(_get_file_completions "$cur" "$command" "$COMP_CWORD"))
        fi
    fi
    
    # Filter suggestions based on the current word prefix
    COMPREPLY=($(_filter_completions "$cur" "${suggestions[@]}"))
    return 0
}

# Provides file path completions for input and output file arguments
_get_file_completions() {
    local current_word="$1"
    local command="$2"
    local arg_position="$3"
    
    local completions=()
    
    # For 'convert' command's first argument (input file), suggest .json files
    # For 'convert' command's second argument (output file), suggest .xlsx files
    # For 'validate' and 'info' commands, suggest .json files
    case "$command" in
        convert)
            # Find the position relative to the command
            local cmd_pos=0
            for ((i=1; i < arg_position; i++)); do
                if [[ "${COMP_WORDS[i]}" == "$command" ]]; then
                    cmd_pos=$i
                    break
                fi
            done
            
            # Calculate position after the command
            local rel_pos=$((arg_position - cmd_pos))
            
            if [[ $rel_pos -eq 1 ]]; then
                # Input JSON file
                completions=($(compgen -f -X '!*.json' -- "$current_word" 2>/dev/null))
            elif [[ $rel_pos -eq 2 ]]; then
                # Output Excel file
                completions=($(compgen -f -X '!*.xlsx' -- "$current_word" 2>/dev/null))
            else
                # Default file completion
                completions=($(compgen -f -- "$current_word" 2>/dev/null))
            fi
            ;;
        validate|info)
            # Find the position relative to the command
            local cmd_pos=0
            for ((i=1; i < arg_position; i++)); do
                if [[ "${COMP_WORDS[i]}" == "$command" ]]; then
                    cmd_pos=$i
                    break
                fi
            done
            
            # Calculate position after the command
            local rel_pos=$((arg_position - cmd_pos))
            
            if [[ $rel_pos -eq 1 ]]; then
                # Input JSON file
                completions=($(compgen -f -X '!*.json' -- "$current_word" 2>/dev/null))
            else
                # Default file completion
                completions=($(compgen -f -- "$current_word" 2>/dev/null))
            fi
            ;;
        *)
            # Use compgen with appropriate file patterns to generate suggestions
            completions=($(compgen -f -- "$current_word" 2>/dev/null))
            ;;
    esac
    
    # Return the generated file suggestions
    echo "${completions[@]}"
}

# Filters completion suggestions based on the current word prefix
_filter_completions() {
    local current_word="$1"
    shift
    local suggestions=("$@")
    
    # Use compgen to filter suggestions that match the current word prefix
    if [ ${#suggestions[@]} -gt 0 ]; then
        compgen -W "${suggestions[*]}" -- "$current_word"
    fi
}

# Register the completion function
complete -F _json_to_excel_completions "$TOOL_COMMAND"